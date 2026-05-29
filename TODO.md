# TODO - Cải thiện độ mượt camera (chấm công & đăng ký)

## Step 1
Hiểu rõ điểm gây lag hiện tại ở:
- `attendance_cam.py` (chấm công)
- `test_cam.py` (đăng ký)
- cơ chế UI polling/terminate (`controllers/ctk_controller.py`)

## Step 2
Thiết kế cải tiến (không đổi behavior UI hiện có):
- Giảm tải face_recognition bằng cách **tách tần suất detect/encode** theo frame (skipping frames)
- Chốt kết quả đúng người và tránh ghi JSON nhiều lần trong cùng lượt
- Giảm/loại bỏ block CPU không cần thiết (sleep, tính toán thừa)

## Step 3
Chỉnh `test_cam.py`:
- Nếu đã có face_locations thì chỉ vẽ + giữ preview mượt
- Nếu người dùng nhấn s mà không có face mới: vẫn hiển thị hướng dẫn
- Giảm tần suất face_locations (ví dụ mỗi N frame)

## Step 4
Chỉnh `attendance_cam.py`:
- Detect/encode face với chu kỳ N frame (ví dụ 2-4)
- Dùng logic chốt: chọn **best match** trong 1 khoảng thời gian (hold last match) để UI ổn định
- Khi đã wrote_result: giảm detect/encode cho tới khi bị terminate bởi UI

## Step 5
Chỉnh nhẹ `ctk_controller.py` (nếu cần):
- Polling hợp lý hơn (ví dụ 150-250ms)
- Đảm bảo terminate an toàn

## Step 6
Chạy thử:
- Đăng ký khuôn mặt: test_cam.py
- Chấm công: attendance_cam.py qua UI
- Xác nhận không bị ghi sai người / vẫn chống trùng theo ngày

