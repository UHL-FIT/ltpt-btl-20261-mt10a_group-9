import os
import sys
from datetime import datetime, date
import pandas as pd
from utils.logger import setup_logger
import firebase_admin
from firebase_admin import credentials, firestore

logger = setup_logger("face_attendance")

# Xác định đường dẫn thư mục gốc của project
def get_base_dir() -> str:
    # Kiểm tra xem chương trình có đang chạy dưới dạng file exe không
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(__file__))

# Cấu hình và kết nối đến Firestore
FIREBASE_KEY_JSON = os.path.join(get_base_dir(), "firebase_key.json")
cre = credentials.Certificate(FIREBASE_KEY_JSON)
firebase_admin.initialize_app(cre)
db = firestore.client()

BASE_DIR = get_base_dir()
DATA_DIR = os.path.join(BASE_DIR, "data")

FACE_STUDENTS_CSV = os.path.join(DATA_DIR, "face_students.csv")
FACE_LOGS_CSV = os.path.join(DATA_DIR, "face_logs.csv")

# Đọc danh sách sinh viên đã đăng ký từ Firestore collection "register"
def load_students() -> pd.DataFrame:
    try:
        docs = db.collection("register").stream()
        rows: list[dict] = []
        for doc in docs:
            data = doc.to_dict() or {}
            rows.append(
                {
                    "msv": str(doc.id).strip().upper(),
                    "ho_ten": str(data.get("name", "") or "").strip(),
                    "lop": str(data.get("class", "") or "").strip(),
                    "sdt": str(data.get("phone_number", "") or "").strip(),
                    "face_path": str(data.get("face_path", "") or "").strip(),
                }
            )

        df = pd.DataFrame(rows)
        # Kiếm tra xem df có rỗng không
        if df.empty:
            return pd.DataFrame(columns=["msv", "ho_ten", "lop", "sdt", "face_path"])
        
        df = df.fillna("")
        df["msv"] = df["msv"].astype(str).str.strip().str.upper()
        return df
    
    except Exception as e:
        logger.exception("load_students() firestore error")
        return pd.DataFrame(columns=["msv", "ho_ten", "lop", "sdt", "face_path"])

# Thêm sinh viên vào collection "register"
def add_student(student: dict[str, str]) -> tuple[bool, str]:
    # student: {msv, ho_ten, lop, sdt, face_path}
    msv = str(student.get("msv", "")).strip().upper()
    ho_ten = str(student.get("ho_ten", "")).strip()
    lop = str(student.get("lop", "")).strip()
    sdt = str(student.get("sdt", "")).strip()
    face_path = str(student.get("face_path", "")).strip()

    if not msv:
        return False, "MSV không được để trống"

    if not ho_ten:
        return False, "Họ tên không được để trống"

    try:
        doc_ref = db.collection("register").document(msv)
        doc = doc_ref.get()
        if doc.exists: return False, "MSV đã tồn tại"
        doc_ref.set(
            {
                "name": ho_ten,
                "class": lop,
                "phone_number": sdt,
                "face_path": face_path,
                "created_at": datetime.now().isoformat(timespec="seconds"),
            }
        )
        return True, "Đã thêm sinh viên"
    
    except Exception:
        logger.exception("add_student() error")
        return False, "Lỗi khi thêm sinh viên" 

# Cập nhật thông tin sinh viên trong database
def update_student(msv: str, update: dict[str, str]) -> tuple[bool, str]:
    msv = str(msv).strip().upper()
    if not msv:
        return False, "MSV không hợp lệ"

    try:
        doc_ref = db.collection("register").document(msv)
        doc = doc_ref.get()
        if not doc.exists:
            return False, "Không tìm thấy MSV"

        payload: dict[str, str] = {}
        if "ho_ten" in update:
            payload["name"] = str(update.get("ho_ten", "") or "").strip()
        if "lop" in update:
            payload["class"] = str(update.get("lop", "") or "").strip()
        if "sdt" in update:
            payload["phone_number"] = str(update.get("sdt", "") or "").strip()
        if "face_path" in update:
            payload["face_path"] = str(update.get("face_path", "") or "").strip()

        if not payload:
            return False, "Không có dữ liệu để cập nhật"

        doc_ref.update(payload)
        return True, "Đã cập nhật"
    
    except Exception:
        logger.exception("update_student() error")
        return False, "Lỗi khi cập nhật"

# Xóa sinh viên trong databse
def delete_student(msv: str) -> tuple[bool, str]:
    msv = str(msv).strip().upper()
    if not msv:
        return False, "MSV không hợp lệ"

    try:
        doc_ref = db.collection("register").document(msv)
        doc = doc_ref.get()
        if not doc.exists:
            return False, "Không tìm thấy MSV"
        doc_ref.delete()
        return True, "Đã xoá"
    
    except Exception:
        logger.exception("delete_student() error")
        return False, "Lỗi khi xoá"

def register_face(msv: str, face_path: str = "") -> tuple[bool, str]:
    msv = str(msv).strip().upper()
    face_path = str(face_path).strip()

    if not msv:
        return False, "MSV không hợp lệ"
    if not face_path:
        return False, "face_path không hợp lệ"

    if not os.path.exists(face_path):
        return False, f"Không tìm thấy ảnh: {face_path}"

    ok, msg = update_student(msv, {"face_path": face_path})
    return ok, msg

# Thêm dòng log vào Firestore collection "logs"
def do_attendance(msv: str, status: str = "OK", note: str = "") -> tuple[bool, str]:
    """Ghi 1 bản ghi chấm công vào collection `logs`.

    Đồng bộ với tab Lịch sử mong muốn (không hiển thị status/note):
    - id: (doc id ngẫu nhiên)
    - name, class, phone_number lấy từ collection `register`.
    - time lấy thời điểm hiện tại.

    Lưu ý:
    - Hàm vẫn giữ tham số status/note để không làm hỏng các chỗ gọi cũ,
      nhưng sẽ KHÔNG ghi chúng vào `logs`.
    """
    msv = str(msv).strip().upper()
    if not msv:
        return False, "MSV không hợp lệ"

    try:
        reg_doc = db.collection("register").document(msv).get()
        if not reg_doc.exists:
            return False, "Không tồn tại MSV"

        reg_data = reg_doc.to_dict() or {}
        db.collection("logs").add(
            {
                "id": msv,
                "name": str(reg_data.get("name", "") or "").strip(),
                "class": str(reg_data.get("class", "") or "").strip(),
                "phone_number": str(reg_data.get("phone_number", "") or "").strip(),
                "time": datetime.now().isoformat(timespec="seconds"),
            }
        )
        return True, "Chấm công thành công!"

    except Exception:
        logger.exception("do_attendance() error")
        return False, "Lỗi khi chấm công"

# Lấy dữ liệu từ Collection "logs"
def get_history(start= None, end= None, msv: str = "") -> pd.DataFrame:
    try:
        msv = str(msv or "").strip().upper()
        docs = db.collection("logs").stream()
        rows: list[dict] = []
        for doc in docs:
            data = doc.to_dict() or {}
            log_id = str(doc.id).strip().upper()
            msv_val = str(data.get("id", "") or "").strip().upper()
            rows.append(
                {
                    "log_id": log_id,
                    "msv": msv_val,
                    "name": str(data.get("name", "") or "").strip(),
                    "class": str(data.get("class", "") or "").strip(),
                    "phone_number": str(data.get("phone_number", "") or "").strip(),
                    "time": data.get("time", ""),
                    # giữ lại nếu có
                    "status": str(data.get("status", "") or ""),
                    "note": str(data.get("note", "") or ""),
                }
            )

        df = pd.DataFrame(rows)
        if df.empty:
            return df

        df["time"] = pd.to_datetime(df["time"], errors="coerce")

        # filter theo mã SV: lấy theo field `id` trong logs
        # (ma sv hiển thị ở cột msv = id trong logs)
        if msv:
            df = df[df["msv"].astype(str).str.upper() == msv]

        if start is not None:
            start_dt = datetime.combine(start, datetime.min.time())
            df = df[df["time"] >= start_dt]

        if end is not None:
            end_dt = datetime.combine(end, datetime.max.time())
            df = df[df["time"] <= end_dt]

        df = df.sort_values("time", ascending=False)
        df["time"] = df["time"].dt.strftime("%Y-%m-%d %H:%M:%S")

        return df

    except Exception:
        logger.exception("get_history() error")
        return pd.DataFrame(columns=["log_id", "msv", "name", "class", "phone_number", "time"])

# Lấy dữ liệu thống kê
def get_stats() -> dict[str, object]:
    try:
        docs = db.collection("logs").stream()
        rows: list[dict] = []
        for doc in docs:
            data = doc.to_dict() or {}
            rows.append(
                {
                    "msv": str(data.get("id", "") or "").strip().upper(),
                    "time": data.get("time", ""),
                }
            )

        df = pd.DataFrame(rows)
        if df.empty:
            return {
                "total_logs": 0,
                "ok": 0,
                "unknown": 0,
                "today_logs": 0,
                "today_ok": 0,
            }

        df["time"] = pd.to_datetime(df["time"], errors="coerce")

        total_logs = len(df)

        now = datetime.now()
        today_mask = (df["time"].dt.date == now.date())
        today_logs = int(today_mask.sum())

        # Không còn status => trả về số lượng log hôm nay
        return {
            "total_logs": total_logs,
            "today_logs": today_logs,
        }

    except Exception:
        logger.exception("get_stats() error")
        return {
            "total_logs": 0,
            "today_logs": 0,
        }


