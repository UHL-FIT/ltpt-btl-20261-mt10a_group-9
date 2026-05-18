import os
import sys
from datetime import datetime, date
from typing import Dict, Optional, Tuple
import pandas as pd
from utils.logger import setup_logger

logger = setup_logger("face_attendance")

def _get_base_dir() -> str:
    # Khi chạy source trực tiếp: base_dir là repo root (nơi models/ nằm trong).
    # Khi build exe (frozen): để đơn giản ta vẫn ghi/đọc ở thư mục data/ cạnh executable.
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(__file__))

BASE_DIR = _get_base_dir()
DATA_DIR = os.path.join(BASE_DIR, "data")

FACE_STUDENTS_CSV = os.path.join(DATA_DIR, "face_students.csv")
FACE_LOGS_CSV = os.path.join(DATA_DIR, "face_logs.csv")

# Tạo dữ liệu mẫu nếu chưa có file csv
def _ensure_csv_files() -> None:
    os.makedirs(DATA_DIR, exist_ok=True)

    if not os.path.exists(FACE_STUDENTS_CSV):
        # Mặc định 1 sinh viên mẫu để UI nhìn thấy dữ liệu.
        df = pd.DataFrame(
            [
                {
                    "msv": "SV001",
                    "ho_ten": "Nguyen Van A",
                    "lop": "CTK42",
                    "sdt": "",
                    "face_path": "",
                    "created_at": datetime.now().isoformat(timespec="seconds"),
                }
            ]
        )
        df.to_csv(FACE_STUDENTS_CSV, index=False, encoding="utf-8-sig")

    if not os.path.exists(FACE_LOGS_CSV):
        df = pd.DataFrame(
            [
                {
                    "log_id": "1",
                    "msv": "SV001",
                    "time": datetime.now().isoformat(timespec="seconds"),
                    "status": "OK",
                    "note": "",
                }
            ]
        )
        df.to_csv(FACE_LOGS_CSV, index=False, encoding="utf-8-sig")

# Đọc danh sách sinh viên từ file csv
def load_students() -> pd.DataFrame:
    _ensure_csv_files()
    df = pd.read_csv(FACE_STUDENTS_CSV, dtype=str, encoding="utf-8-sig")
    if df.empty:
        return df
    for col in ["msv", "ho_ten", "lop", "sdt", "face_path", "created_at"]:
        if col not in df.columns:
            df[col] = ""
    df = df.fillna("")
    df["msv"] = df["msv"].astype(str).str.strip().str.upper()
    return df

# Thêm sinh viên 
def add_student(student: Dict[str, str]) -> Tuple[bool, str]:
    """student: {msv, ho_ten, lop, sdt, face_path}"""
    _ensure_csv_files()
    df = load_students()

    msv = str(student.get("msv", "")).strip().upper()
    ho_ten = str(student.get("ho_ten", "")).strip()
    lop = str(student.get("lop", "")).strip()
    sdt = str(student.get("sdt", "")).strip()
    face_path = str(student.get("face_path", "")).strip()

    if not msv:
        return False, "MSV không được để trống"
    
    if not ho_ten:
        return False, "Họ tên không được để trống"
    
    if (df["msv"] == msv).any():
        return False, "MSV đã tồn tại"

    new_row = {
        "msv": msv,
        "ho_ten": ho_ten,
        "lop": lop,
        "sdt": sdt,
        "face_path": face_path,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }

    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(FACE_STUDENTS_CSV, index=False, encoding="utf-8-sig")
    return True, "Đã thêm sinh viên" 

# Cập nhật thông itn sinh viên
def update_student(msv: str, update: Dict[str, str]) -> Tuple[bool, str]:
    _ensure_csv_files()
    df = load_students()
    msv = str(msv).strip().upper()

    idx = df.index[df["msv"] == msv].tolist()
    if not idx:
        return False, "Không tìm thấy MSV"

    for key in ["ho_ten", "lop", "sdt", "face_path"]:
        if key in update:
            df.loc[idx, key] = str(update.get(key, "")).strip()

    df.to_csv(FACE_STUDENTS_CSV, index=False, encoding="utf-8-sig")
    return True, "Đã cập nhật"

# Xóa sinh viên
def delete_student(msv: str) -> Tuple[bool, str]:
    _ensure_csv_files()
    df = load_students()
    msv = str(msv).strip().upper()
    if not (df["msv"] == msv).any():
        return False, "Không tìm thấy MSV"
    df = df[df["msv"] != msv]
    df.to_csv(FACE_STUDENTS_CSV, index=False, encoding="utf-8-sig")
    return True, "Đã xoá"

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

# Thêm dòng log vào face_log.csv
def do_attendance(msv: str, status: str = "OK", note: str = "") -> Tuple[bool, str]:
    _ensure_csv_files()
    df_students = load_students()

    msv = str(msv).strip().upper()
    if not (df_students["msv"] == msv).any():
        return False, "Không tồn tại MSV"

    df_logs = pd.read_csv(FACE_LOGS_CSV, dtype=str, encoding="utf-8-sig")
    if df_logs.empty:
        next_id = "1"
    else:
        try:
            next_id = str(int(df_logs["log_id"].astype(str).str.strip().fillna("0").max()) + 1)
        except Exception:
            next_id = str(len(df_logs) + 1)

    new_row = {
        "log_id": next_id,
        "msv": msv,
        "time": datetime.now().isoformat(timespec="seconds"),
        "status": str(status).strip().upper(),
        "note": str(note).strip(),
    }

    df_logs = pd.concat([df_logs, pd.DataFrame([new_row])], ignore_index=True)
    df_logs.to_csv(FACE_LOGS_CSV, index=False, encoding="utf-8-sig")
    return True, "Đã chấm công"


def _parse_time_series(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], errors="coerce")
    return df


def get_history(start: Optional[date] = None, end: Optional[date] = None, msv: str = "") -> pd.DataFrame:
    _ensure_csv_files()
    df = pd.read_csv(FACE_LOGS_CSV, dtype=str, encoding="utf-8-sig")
    if df.empty:
        return df

    df = _parse_time_series(df)

    if msv:
        msv = str(msv).strip().upper()
        df = df[df["msv"].astype(str).str.upper() == msv]

    if start is not None:
        start_dt = datetime.combine(start, datetime.min.time())
        df = df[df["time"] >= start_dt]

    if end is not None:
        end_dt = datetime.combine(end, datetime.max.time())
        df = df[df["time"] <= end_dt]

    df = df.sort_values("time", ascending=False)
    # Format back string
    df["time"] = df["time"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df


def get_stats() -> Dict[str, object]:
    """Thống kê tổng quát + theo ngày gần nhất."""
    _ensure_csv_files()
    df = pd.read_csv(FACE_LOGS_CSV, dtype=str, encoding="utf-8-sig")
    if df.empty:
        return {
            "total_logs": 0,
            "ok": 0,
            "unknown": 0,
            "today_logs": 0,
            "today_ok": 0,
        }

    df = _parse_time_series(df)

    total_logs = len(df)
    df["status"] = df["status"].fillna("").astype(str).str.upper().str.strip()
    ok = int((df["status"] == "OK").sum())

    # unknown: nếu bạn dùng các status khác thì cập nhật sau.
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

