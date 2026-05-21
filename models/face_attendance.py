import os
import sys
from datetime import datetime, date
from typing import Dict, Optional, Tuple
import pandas as pd
from utils.logger import setup_logger
import firebase_admin
from firebase_admin import credentials, firestore

logger = setup_logger("face_attendance")

def _get_base_dir() -> str:
    # Khi chạy source trực tiếp: base_dir là repo root (nơi models/ nằm trong).
    # Khi build exe (frozen): để đơn giản ta vẫn ghi/đọc ở thư mục data/ cạnh executable.
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(__file__))

FIREBASE_KEY_JSON = os.path.join(_get_base_dir(), "firebase_key.json")
cred = credentials.Certificate(FIREBASE_KEY_JSON)
firebase_admin.initialize_app(cred)
db = firestore.client()

BASE_DIR = _get_base_dir()
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
        if df.empty:
            # Đảm bảo DataFrame có đủ cột để tránh lỗi khi dùng iterrows/ get
            return pd.DataFrame(columns=["msv", "ho_ten", "lop", "sdt", "face_path"])

        df = df.fillna("")
        df["msv"] = df["msv"].astype(str).str.strip().str.upper()
        return df
    
    except Exception as e:
        logger.exception("load_students() firestore error")
        return pd.DataFrame(columns=["msv", "ho_ten", "lop", "sdt", "face_path"])


# Thêm sinh viên vào database, cụ thể là collection "register"
def add_student(student: Dict[str, str]) -> Tuple[bool, str]:
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
def update_student(msv: str, update: Dict[str, str]) -> Tuple[bool, str]:
    """Update thông tin sinh viên trong Firestore.

    update có thể chứa các key:
    - ho_ten -> name
    - lop -> class
    - sdt -> phone_number
    - face_path -> face_path
    """
    msv = str(msv).strip().upper()
    if not msv:
        return False, "MSV không hợp lệ"

    try:
        doc_ref = db.collection("register").document(msv)
        doc = doc_ref.get()
        if not doc.exists:
            return False, "Không tìm thấy MSV"

        payload: Dict[str, str] = {}
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
def delete_student(msv: str) -> Tuple[bool, str]:
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


def register_face(msv: str, face_path: str = "") -> Tuple[bool, str]:
    """Liên kết ảnh khuôn mặt với sinh viên theo MSV.

    Args:
        msv: Mã sinh viên.
        face_path: Đường dẫn ảnh khuôn mặt (vd: dataset/SV001.jpg)

    Returns:
        (ok, msg)
    """
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
def do_attendance(msv: str, status: str = "OK", note: str = "") -> Tuple[bool, str]:
    """Ghi 1 bản ghi chấm công vào collection `logs`.
    - Doc id: tự sinh
    - Field tối thiểu: msv, time, status, note
    - KHÔNG thêm created_at/date (theo yêu cầu)
    """
    msv = str(msv).strip().upper()
    status = str(status).strip().upper()
    note = str(note).strip()

    if not msv:
        return False, "MSV không hợp lệ"

    try:
        # kiểm tra MSV tồn tại
        doc = db.collection("register").document(msv).get()
        if not doc.exists:
            return False, "Không tồn tại MSV"

        db.collection("logs").add(
            {
                "msv": msv,
                "time": datetime.now().isoformat(timespec="seconds"),
                "status": status,
                "note": note,
            }
        )
        return True, "Đã chấm công"
    
    except Exception:
        logger.exception("do_attendance() error")
        return False, "Lỗi khi chấm công"


def _parse_time_series(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    return df


""" Lấy lịch sử chấm công từ collection `logs`.
    Trả về DataFrame với các cột: log_id, msv, time, status, note
"""
def get_history(start: Optional[date] = None, end: Optional[date] = None, msv: str = "") -> pd.DataFrame:
    
    try:
        msv = str(msv or "").strip().upper()

        query = db.collection("logs")
        docs = query.stream()

        rows: list[dict] = []
        for doc in docs:
            data = doc.to_dict() or {}
            row_time = data.get("time", "")
            rows.append(
                {
                    "log_id": str(doc.id),
                    "msv": str(data.get("msv", "") or "").strip().upper(),
                    "time": row_time,
                    "status": str(data.get("status", "") or ""),
                    "note": str(data.get("note", "") or ""),
                }
            )

        df = pd.DataFrame(rows)
        if df.empty:
            return df

        df["time"] = pd.to_datetime(df["time"], errors="coerce")
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
        return pd.DataFrame(columns=["log_id", "msv", "time", "status", "note"])

"""Thống kê tổng quát + theo ngày gần nhất từ collection `logs`."""
def get_stats() -> Dict[str, object]:
    try:
        docs = db.collection("logs").stream()
        rows: list[dict] = []
        for doc in docs:
            data = doc.to_dict() or {}
            rows.append(
                {
                    "msv": str(data.get("msv", "") or "").strip().upper(),
                    "time": data.get("time", ""),
                    "status": str(data.get("status", "") or ""),
                    "note": str(data.get("note", "") or ""),
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
        df["status"] = df["status"].fillna("").astype(str).str.upper().str.strip()

        total_logs = len(df)
        ok = int((df["status"] == "OK").sum())
        unknown = int((df["status"] != "OK").sum())

        now = datetime.now()
        today_mask = (df["time"].dt.date == now.date())
        today_logs = int(today_mask.sum())
        today_ok = int(((df["time"].dt.date == now.date()) & (df["status"] == "OK")).sum())

        return {
            "total_logs": total_logs,
            "ok": ok,
            "unknown": unknown,
            "today_logs": today_logs,
            "today_ok": today_ok,
        }
    except Exception:
        logger.exception("get_stats() error")
        return {
            "total_logs": 0,
            "ok": 0,
            "unknown": 0,
            "today_logs": 0,
            "today_ok": 0,
        }

