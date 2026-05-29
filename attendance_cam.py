import cv2 as cv
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import face_recognition

from models import face_attendance


def _get_base_dir() -> str:
    # Repo root
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = _get_base_dir()
DATA_DIR = os.path.join(BASE_DIR, "data")
os.makedirs(DATA_DIR, exist_ok=True)

LAST_ATTENDANCE_JSON = os.path.join(DATA_DIR, "last_attendance.json")


def _safe_read_json(path: str) -> Optional[dict]:
    try:
        if not os.path.exists(path):
            return None
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def _safe_write_json(path: str, payload: dict) -> None:
    tmp_path = path + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def _compute_embeddings_from_students() -> Tuple[List[List[float]], List[str], Dict[str, dict]]:
    """Return:
    - known_encodings: list of embeddings
    - known_msws: list of corresponding MSV
    - student_info_by_msv: dict msv -> {ho_ten, lop, sdt}
    """
    df = face_attendance.load_students()
    known_encodings: List[List[float]] = []
    known_msws: List[str] = []
    info: Dict[str, dict] = {}

    if df is None or df.empty:
        return known_encodings, known_msws, info

    for _, row in df.iterrows():
        msv = str(row.get("msv", "")).strip().upper()
        face_path = str(row.get("face_path", "")).strip()

        ho_ten = str(row.get("ho_ten", "")).strip()
        lop = str(row.get("lop", "")).strip()
        sdt = str(row.get("sdt", "")).strip()

        if not msv or not face_path:
            continue
        if not os.path.exists(face_path):
            # face_path trong CSV có thể chưa đúng/thiếu
            continue

        try:
            img = face_recognition.load_image_file(face_path)
            encs = face_recognition.face_encodings(img)
            if not encs:
                continue
            # lấy embedding đầu tiên
            enc = encs[0]

            known_encodings.append(enc)
            known_msws.append(msv)
            info[msv] = {"ho_ten": ho_ten, "lop": lop, "sdt": sdt}
        except Exception:
            # bỏ qua sinh viên lỗi ảnh
            continue

    return known_encodings, known_msws, info


def _load_already_marked_today() -> set[str]:
    """Return set of MSV đã chấm OK hôm nay."""
    try:
        df = face_attendance.get_history()
        if df is None or df.empty:
            return set()

        now = datetime.now()
        # get_history() đã format time string theo %Y-%m-%d %H:%M:%S
        # df["time"] là string
        marked: set[str] = set()
        for _, row in df.iterrows():
            msv = str(row.get("msv", "")).strip().upper()
            if not msv:
                continue
            t_str = str(row.get("time", "")).strip()
            try:
                t_dt = datetime.strptime(t_str, "%Y-%m-%d %H:%M:%S")
            except Exception:
                continue
            if t_dt.date() == now.date():
                marked.add(msv)
        return marked
    except Exception:
        return set()

def _match_face(
    encoding,
    known_encodings: List[List[float]],
    known_msws: List[str],
    tolerance: float = 0.5,
) -> Optional[str]:
    if not known_encodings:
        return None

    try:
        # compare_faces trả về list bool
        matches = face_recognition.compare_faces(known_encodings, encoding, tolerance=tolerance)
        if not any(matches):
            return None

        # Lấy khoảng cách nhỏ nhất trong các index match
        distances = face_recognition.face_distance(known_encodings, encoding)
        best_idx = None
        best_dist = None
        for i, is_match in enumerate(matches):
            if not is_match:
                continue
            d = float(distances[i])
            if best_dist is None or d < best_dist:
                best_dist = d
                best_idx = i

        if best_idx is None:
            return None
        return str(known_msws[best_idx]).strip().upper()
    except Exception:
        return None


def main():
    # Load embeddings trước
    known_encodings, known_msws, student_info = _compute_embeddings_from_students()
    already_marked_today = _load_already_marked_today()

    cam = cv.VideoCapture(0, cv.CAP_DSHOW)
    try:
        if not cam.isOpened():
            # báo lỗi lên JSON để UI biết (không crash)
            _safe_write_json(
                LAST_ATTENDANCE_JSON,
                {"status": "ERROR", "error": "Khong the mo cam"},
            )
            return

        wrote_result = False
        last_face_seen_time = 0.0

        # Giảm tải detect/encode để camera mượt hơn
        detect_every_n = 3
        frame_count = 0


        last_face_locations = []
        last_encodings = []




        while True:
            res, frame = cam.read()
            if (not res) or (frame is None):
                break

            flipped_frame = cv.flip(frame, 1)

            # Hiển thị trạng thái
            cv.putText(
                flipped_frame,
                "Dang nhan dien...",
                (20, 40),
                cv.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 255),
                2,
                cv.LINE_AA,
            )

            rgb = cv.cvtColor(flipped_frame, cv.COLOR_BGR2RGB)

            # Giảm tải: chỉ detect/encode mỗi N frame, còn lại dùng kết quả cũ
            if frame_count % detect_every_n == 0:
                face_locations = face_recognition.face_locations(rgb)
                encodings = face_recognition.face_encodings(rgb, face_locations)

                if face_locations:
                    last_face_seen_time = time.time()
                    last_face_locations = face_locations
                    last_encodings = encodings
            else:
                face_locations = last_face_locations
                encodings = last_encodings

            frame_count += 1

            for (top, right, bottom, left), enc in zip(face_locations, encodings):

                # xanh lá
                cv.rectangle(flipped_frame, (left, top), (right, bottom), (0, 255, 0), 2)

                matched_msv = _match_face(enc, known_encodings, known_msws, tolerance=0.6)

                if matched_msv:
                    # chống trùng theo ngày
                    if matched_msv in already_marked_today:
                        label = f"{matched_msv} - DA CHAM HÔM NAY"
                        status = "ALREADY_MARKED_TODAY"
                    else:
                        ok, _ = face_attendance.do_attendance(matched_msv, status="OK")
                        already_marked_today.add(matched_msv)
                        label = f"{matched_msv} - OK"
                        status = "SUCCESS" if ok else "UNKNOWN"

                    cv.putText(
                        flipped_frame,
                        label,
                        (left, top - 10),
                        cv.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 255, 0),
                        2,
                        cv.LINE_AA,
                    )

                    # ghi kết quả 1 lần duy nhất
                    if not wrote_result:
                        info = student_info.get(matched_msv, {})
                        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        _safe_write_json(
                            LAST_ATTENDANCE_JSON,
                            {
                                "status": status,
                                "msv": matched_msv,
                                "ho_ten": info.get("ho_ten", ""),
                                "lop": info.get("lop", ""),
                                "sdt": info.get("sdt", ""),
                                "time": now,
                            },
                        )
                        wrote_result = True

                        # Chốt 1 lần duy nhất rồi dừng xử lý face trong frame này
                        break

                else:

                    cv.putText(
                        flipped_frame,
                        "UNKNOWN",
                        (left, top - 10),
                        cv.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 255),
                        2,
                        cv.LINE_AA,
                    )

            # Hiển thị
            cv.imshow("CHAM CONG", flipped_frame)

            # Phím q để thoát thủ công
            key = cv.waitKey(1) & 0xFF
            if key == ord("q") or key == ord("Q"):
                break

            # Nếu đã wrote_result rồi: giữ camera thêm một chút rồi thoát
            # để đúng yêu cầu “bấm OK mới đóng”: phần đóng thực tế sẽ do controller.
            # Vì hiện controller chưa có kill process, mình sẽ KHÔNG tự thoát ở đây.
            # Tuy nhiên để tránh tốn CPU, vẫn có thể giảm tốc độ.
            if wrote_result:
                time.sleep(0.01)



    except Exception:
        # báo lỗi
        _safe_write_json(
            LAST_ATTENDANCE_JSON,
            {"status": "ERROR", "error": "Loi khi nhan dien"},
        )
    finally:
        try:
            cam.release()
        except Exception:
            pass
        try:
            cv.destroyAllWindows()
        except Exception:
            pass


if __name__ == "__main__":
    main()

