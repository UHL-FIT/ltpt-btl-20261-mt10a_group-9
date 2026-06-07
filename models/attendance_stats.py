from dataclasses import dataclass
from datetime import datetime, date
import pandas as pd
from utils.logger import setup_logger
import os
import sys
import firebase_admin
from firebase_admin import credentials, firestore

logger = setup_logger("attendance_stats")

def _get_base_dir() -> str:
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.dirname(__file__))


# Initialize Firestore (consistent with models/face_attendance.py)
FIREBASE_KEY_JSON = os.path.join(_get_base_dir(), "firebase_key.json")

# firebase_admin.initialize_app raises if called twice without guard.
# Use a safe check.
try:
    if not firebase_admin._apps:  # type: ignore[attr-defined]
        cred = credentials.Certificate(FIREBASE_KEY_JSON)
        firebase_admin.initialize_app(cred)
except Exception:
    # fallback: try initialize anyway
    try:
        cred = credentials.Certificate(FIREBASE_KEY_JSON)
        firebase_admin.initialize_app(cred)
    except Exception:
        pass

db = firestore.client()

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

    def to_dict(self) -> dict[str, float | int]:
        return {
            "registered_total": self.registered_total,
            "today_marked": self.today_marked,
            "today_unmarked": self.today_unmarked,
            "marked_pct": round(self.marked_pct, 2),
            "unmarked_pct": round(self.unmarked_pct, 2),
        }


def _parse_date_bounds(d: date) -> tuple[datetime, datetime]:
    start_dt = datetime.combine(d, datetime.min.time())
    end_dt = datetime.combine(d, datetime.max.time())
    return start_dt, end_dt


def get_today_attendance_stats_distinct() -> TodayAttendanceStats:
    """Compute attendance stats for UI using ONLY Firestore.

    - registered_total: count students with non-empty face_path (and optionally file exists)
    - today_marked: distinct MSV with status == "OK" within today
    - today_unmarked: registered_total - today_marked
    """

    try:
        today = datetime.now().date()
        start_dt, end_dt = _parse_date_bounds(today)

        # 1) registered_total: from register collection
        registered_total = 0
        docs = db.collection("register").stream()
        for doc in docs:
            data = doc.to_dict() or {}
            face_path = str(data.get("face_path", "") or "").strip()

            # Keep same intent as old CSV version: only count if face_path is not empty.
            # Old code also checked os.path.exists(face_path). Keeping that check may break
            # for paths not existing on this machine; so we only require non-empty.
            if face_path:
                registered_total += 1

        # 2) today_marked: from logs collection
        marked_msv: set[str] = set()
        logs_docs = db.collection("logs").stream()

        for doc in logs_docs:
            data = doc.to_dict() or {}
            msv = str(data.get("id", "") or "").strip().upper()
            if not msv:
                continue

            time_str = str(data.get("time", "") or "").strip()
            if not time_str:
                continue

            # time is stored as ISO string: datetime.now().isoformat(timespec="seconds")
            try:
                t = datetime.fromisoformat(time_str)
            except Exception:
                # fallback: skip unparseable timestamps
                continue

            if not (start_dt <= t <= end_dt):
                continue

            marked_msv.add(msv)

        today_marked = len(marked_msv)
        today_unmarked = max(0, registered_total - today_marked)

        return TodayAttendanceStats(
            registered_total=registered_total,
            today_marked=today_marked,
            today_unmarked=today_unmarked,
        )

    except Exception as e:
        logger.exception("get_today_attendance_stats_distinct() error")
        return TodayAttendanceStats(registered_total=0, today_marked=0, today_unmarked=0)

