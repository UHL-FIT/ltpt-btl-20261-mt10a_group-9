from dataclasses import dataclass
from datetime import datetime
from typing import Dict
import os
import sys
import pandas as pd

def _get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(__file__))


BASE_DIR = _get_base_dir()
DATA_DIR = os.path.join(BASE_DIR, "data")
FACE_STUDENTS_CSV = os.path.join(DATA_DIR, "face_students.csv")
FACE_LOGS_CSV = os.path.join(DATA_DIR, "face_logs.csv")


def _safe_read_csv(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        return pd.DataFrame()
    try:
        return pd.read_csv(path, dtype=str, encoding="utf-8-sig")
    except Exception:
        return pd.DataFrame()


def _parse_time_series(df: pd.DataFrame) -> pd.DataFrame:
    if df is None or df.empty:
        return df
    df = df.copy()
    if "time" in df.columns:
        df["time"] = pd.to_datetime(df["time"], errors="coerce")
    return df


@dataclass(frozen=True)
class TodayAttendanceStats:
    registered_total: int
    today_marked: int  # distinct MSV with status OK today
    today_unmarked: int

    @property
    def marked_pct(self) -> float:
        if self.registered_total <= 0:
            return 0.0
        return (self.today_marked / self.registered_total) * 100.0

    @property
    def unmarked_pct(self) -> float:
        if self.registered_total <= 0:
            return 0.0
        return (self.today_unmarked / self.registered_total) * 100.0

    def to_dict(self) -> Dict[str, float | int]:
        return {
            "registered_total": self.registered_total,
            "today_marked": self.today_marked,
            "today_unmarked": self.today_unmarked,
            "marked_pct": round(self.marked_pct, 2),
            "unmarked_pct": round(self.unmarked_pct, 2),
        }


def get_today_attendance_stats_distinct() -> TodayAttendanceStats:
    """Compute attendance stats for UI.

    - registered_total: count of students with non-empty face_path (and face_path exists)
    - today_marked: number of distinct MSV with status == OK within today
    - today_unmarked: registered_total - today_marked
    """

    students = _safe_read_csv(FACE_STUDENTS_CSV)
    if students.empty:
        registered_total = 0
    else:
        for col in ["msv", "face_path"]:
            if col not in students.columns:
                students[col] = ""
        students["face_path"] = students["face_path"].fillna("").astype(str).str.strip()
        students_valid = students[students["face_path"] != ""]
        # validate file exists to avoid broken records
        def _exists(p: str) -> bool:
            try:
                return bool(p) and os.path.exists(p)
            except Exception:
                return False

        students_valid = students_valid[students_valid["face_path"].apply(_exists)]
        registered_total = int(len(students_valid))

    logs = _safe_read_csv(FACE_LOGS_CSV)
    logs = _parse_time_series(logs)
    if logs.empty or "msv" not in logs.columns or "status" not in logs.columns or "time" not in logs.columns:
        today_marked = 0
    else:
        logs["status"] = logs["status"].fillna("").astype(str).str.upper().str.strip()
        now = datetime.now()
        today_mask = logs["time"].dt.date == now.date()
        ok_mask = logs["status"] == "OK"
        subset = logs[today_mask & ok_mask]
        if subset.empty:
            today_marked = 0
        else:
            subset["msv"] = subset["msv"].astype(str).str.strip().str.upper()
            today_marked = int(subset["msv"].nunique())

    today_unmarked = max(0, registered_total - today_marked)
    return TodayAttendanceStats(
        registered_total=registered_total,
        today_marked=today_marked,
        today_unmarked=today_unmarked,
    )

