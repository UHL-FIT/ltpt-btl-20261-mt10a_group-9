import cv2 as cv
import face_recognition
import os
import argparse
import sys


def _ensure_dataset_dir(data_dir: str) -> None:
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)


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
    _ensure_dataset_dir(data_dir)

    output_path = os.path.join(data_dir, f"{msv}.jpg")

    cam = cv.VideoCapture(args.camera_index, cv.CAP_DSHOW)
    cam.set(cv.CAP_PROP_FRAME_WIDTH, 640)
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, 480)

    # Biến phục vụ việc giảm tải cho CPU (Bỏ khung hình)
    frame_count = 0
    face_locations = []


    try:
        if not cam.isOpened():
            print('Loi: Khong the mo cam!')
        else:
            print('Camera da san sang!')
            while True:
                res, frame = cam.read()
                if (not res) or (frame is None):
                    print('Loi: Doc khung hinh khong thanh cong!')
                    break
                
                # Lật ảnh cho giống soi gương
                flipped_frame = cv.flip(frame, 1)
                display_frame = flipped_frame.copy()

                # SỬA LỖI 1: Cứ 4 khung hình mới quét mặt 1 lần bằng AI để camera mượt mà
                if frame_count % 4 == 0:
                    # Chuyển đổi hệ màu sang RGB phục vụ face_recognition
                    rgb_frame = cv.cvtColor(display_frame, cv.COLOR_BGR2RGB)
                    face_locations = face_recognition.face_locations(rgb_frame)

                frame_count += 1

                # Vẽ khung chữ nhật xanh xung quanh mặt từ dữ liệu đã quét
                for (top, right, bottom, left) in face_locations:
                    cv.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                    cv.putText(display_frame, "Bam 's' de luu anh", (left, top - 10), 
                            cv.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                cv.imshow('DANG KY KHUON MAT', display_frame)

                # 4. Bắt sự kiện phím bấm
                key = cv.waitKey(1) & 0xFF
                # Nếu nhấn 's' và có mặt trong khung hình -> Lưu ảnh và thoát
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
        print('He thong da don dep va dong an toan!')

if __name__ == "__main__":
    main()