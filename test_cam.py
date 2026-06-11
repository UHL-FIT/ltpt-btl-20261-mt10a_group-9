import cv2 as cv
import face_recognition
import os
import argparse
import sys
import pathlib

def ensure_dataset_dir(dataset_dir: str) -> None:
    if not os.path.exists(dataset_dir):
        os.makedirs(dataset_dir)

def main():
    parser = argparse.ArgumentParser(description="Capture 1 face image for registration")
    parser.add_argument("--msv", type=str, required=True, help="Student code")
    parser.add_argument("--camera-index", type=int, default=0)
    args = parser.parse_args()

    msv = str(args.msv).strip().upper()
    if not msv:
        print("Loi: MSV khong hop le", file=sys.stderr)
        return 2

    # Tạo thư mục chứa dataset nếu chưa có
    data_dir = "dataset"
    ensure_dataset_dir(data_dir)

    output_path = os.path.join(data_dir, f"{msv}.jpg")

    cam = cv.VideoCapture(args.camera_index, cv.CAP_DSHOW)
    cam.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, 480)
    cam.set(cv.CAP_PROP_BUFFERSIZE, 1)  # giảm latency: không buffer frame cũ

    # Biến phục vụ việc giảm tải cho CPU (Bỏ khung hình)
    frame_count = 0
    face_locations = []
    last_detected = []
    detect_every_n = 5  # detect mỗi 5 frame: giảm CPU, camera mượt hơn

    # Đường dẫn file tín hiệu ready (cùng thư mục data/ với attendance)
    repo_root = pathlib.Path(__file__).parent
    ready_flag = repo_root / "data" / "cam_register_ready.flag"
    ready_flag.parent.mkdir(exist_ok=True)

    try:
        if not cam.isOpened():
            print('Loi: Khong the mo cam!')
        else:
            # --- Bắn tín hiệu về UI: camera đã sẵn sàng ---
            ready_flag.touch()
            print('Camera da san sang!')
            while True:
                res, frame = cam.read()
                if (not res) or (frame is None):
                    print('Loi: Doc khung hinh khong thanh cong!')
                    break
                
                # Lật ảnh cho giống soi gương
                flipped_frame = cv.flip(frame, 1)
                display_frame = flipped_frame  # không cần .copy() vì chỉ đọc

                # Giảm tải: chỉ detect mặt mỗi N frame, các frame còn lại dùng kết quả cũ
                if frame_count % detect_every_n == 0:
                    rgb_frame = cv.cvtColor(display_frame, cv.COLOR_BGR2RGB)
                    # Resize xuống 1/4 trước khi detect -> tăng tốc 4-16 lần
                    small_rgb = cv.resize(rgb_frame, (0, 0), fx=0.25, fy=0.25)
                    small_locations = face_recognition.face_locations(small_rgb)
                    # Scale tọa độ ngược lại về kích thước frame gốc
                    face_locations = [
                        (top * 4, right * 4, bottom * 4, left * 4)
                        for (top, right, bottom, left) in small_locations
                    ]
                    if face_locations:
                        last_detected = face_locations

                # Nếu chưa detect được ở frame hiện tại thì dùng last_detected để khung hiển thị ổn định
                if not face_locations and last_detected:
                    face_locations = last_detected

                frame_count += 1


                # Vẽ khung chữ nhật xanh xung quanh mặt từ dữ liệu đã quét
                for (top, right, bottom, left) in face_locations:
                    cv.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv.putText(display_frame, "Bam 's' de luu anh", (left, top - 10), 
                            cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                cv.imshow('DANG KY KHUON MAT', display_frame)

                # 4. Bắt sự kiện phím bấm
                key = cv.waitKey(1) & 0xFF
                # Nếu nhấn 's' và có mặt (dựa trên last_detected) -> Lưu ảnh và thoát
                if key == ord('s') or key == ord('S'):  # Nhận diện cả chữ hoa và chữ thường
                    if len(face_locations) > 0:
                        filename = output_path

                        # Lưu ảnh gốc thực tế (frame)
                        cv.imwrite(filename, flipped_frame)
                        print(f"Thu thap anh thanh cong: {filename}")

                        break
                    else:
                        print("Khong tim thay khuon mat trong khung hinh, vui long thu lai!")

                # Nếu nhấn 'q' -> Hủy bỏ, tắt cam đi ra
                elif key == ord('q') or key == ord('Q'):
                    print("Da huy bo quet mat.")
                    break

    except Exception as e:
        print(f'Loi phat sinh: {e}')

    finally:
        cam.release()
        cv.destroyAllWindows()
        # Xóa flag nếu còn (tránh lần sau nhận nhầm)
        try:
            ready_flag.unlink(missing_ok=True)
        except Exception:
            pass
        print('He thong da don dep va dong an toan!')

if __name__ == "__main__":
    main()