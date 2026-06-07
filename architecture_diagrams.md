# Các Sơ Đồ Luồng Xử Lý (Sequence Diagrams)

Tài liệu này chứa các sơ đồ luồng xử lý (Sequence Diagrams) được vẽ bằng Mermaid cho ứng dụng điểm danh khuôn mặt SmartAttend.

## 1. Sơ đồ luồng xử lý tổng quan toàn hệ thống (Overall System Flow)

**Mô tả:** Sơ đồ này mô tả vòng đời chung của ứng dụng từ lúc người dùng khởi chạy cho đến khi tải dữ liệu khởi tạo và sẵn sàng nhận tương tác. Khi ứng dụng (`main.py`) được bật, hệ thống sẽ gọi Controller (`ctk_controller`) để vẽ giao diện. Trong quá trình khởi tạo UI, Controller sẽ âm thầm gọi hai luồng song song để truy xuất dữ liệu từ Firebase Firestore: một luồng tải lịch sử chấm công đổ vào bảng (TreeView), luồng còn lại tính toán KPI để vẽ hai biểu đồ Matplotlib. Sau khi mọi thứ sẵn sàng, vòng lặp chính của ứng dụng được mở ra để chờ phản hồi từ các nút bấm của người dùng.

```mermaid
sequenceDiagram
    actor User as Người dùng
    participant Main as main.py
    participant Ctrl as ctk_controller
    participant View as ctk_view
    participant FaceApp as face_attendance
    participant StatsApp as attendance_stats
    participant DB as Firebase Firestore

    User->>Main: Khởi chạy ứng dụng
    Main->>Ctrl: chay_ung_dung()
    Ctrl->>View: create_main_window()
    View-->>Ctrl: Trả về root (Window) và UI Dict
    
    rect rgb(240, 248, 255)
    Note over Ctrl, DB: Khởi tạo dữ liệu ban đầu
    Ctrl->>FaceApp: get_history(msv="")
    FaceApp->>DB: Truy vấn collection "logs"
    DB-->>FaceApp: Trả về danh sách logs
    FaceApp-->>Ctrl: Trả về Pandas DataFrame
    Ctrl->>View: Cập nhật bảng Lịch sử (TreeView)
    
    Ctrl->>StatsApp: get_today_attendance_stats_distinct()
    StatsApp->>DB: Truy vấn collection "register" & "logs"
    DB-->>StatsApp: Trả về số liệu tổng và chấm công
    StatsApp-->>Ctrl: Trả về đối tượng TodayAttendanceStats
    Ctrl->>View: Vẽ và cập nhật Biểu đồ (Matplotlib)
    end
    
    Ctrl-->>User: Hiển thị giao diện chính (Sẵn sàng)
    
    loop Chờ tương tác người dùng
        User->>Ctrl: Click các nút (Đăng kí, Chấm công, Thống kê,...)
        Ctrl->>Ctrl: Gọi hàm xử lý tương ứng
    end
```

## 2. Sơ đồ chức năng Đăng kí Sinh viên & Khuôn mặt

**Mô tả:** Quá trình đăng kí được chia làm 2 giai đoạn độc lập nhưng nối tiếp nhau. 
- **Giai đoạn 1 (Đăng ký thông tin):** Người dùng nhập thông tin text (MSV, Tên, Lớp, Số điện thoại) và lưu. Controller gọi `face_attendance.add_student()` để đẩy thẳng document này lên collection `register` của Firestore.
- **Giai đoạn 2 (Đăng ký khuôn mặt):** Người dùng ấn "Đăng ký khuôn mặt". Controller mở một tiến trình phụ (`test_cam.py`) để chạy camera độc lập nhằm tránh giật lag UI. Sinh viên đứng trước cam và bấm phím 's' để chụp. Ảnh lưu cục bộ ở thư mục `dataset/`. Khi camera tắt, tiến trình chính kiểm tra sự tồn tại của file ảnh và cập nhật lại đường dẫn file này lên Firestore cho tài khoản sinh viên đó.

```mermaid
sequenceDiagram
    actor User as Người dùng
    participant Ctrl as ctk_controller
    participant FaceApp as face_attendance
    participant DB as Firebase (register)
    participant CamTest as test_cam.py (Subprocess)
    participant FS as Local FileSystem

    User->>Ctrl: Nhập thông tin (MSV, Tên, Lớp, SĐT)
    User->>Ctrl: Bấm "Lưu thông tin đăng kí"
    Ctrl->>FaceApp: add_student(student_info)
    FaceApp->>DB: Kiểm tra MSV tồn tại & Thêm mới document
    DB-->>FaceApp: Trả về kết quả
    FaceApp-->>Ctrl: Kết quả (True/False)
    Ctrl-->>User: Hiển thị thông báo "Lưu thành công"

    User->>Ctrl: Bấm "Đăng kí khuôn mặt"
    Ctrl->>FaceApp: load_students() (Kiểm tra MSV đã lưu chưa)
    FaceApp-->>Ctrl: Trả về DataFrame

    Note over Ctrl, CamTest: Mở chương trình lấy mẫu Camera
    Ctrl->>CamTest: subprocess.run(["test_cam.py", "--msv", MSV])
    CamTest->>User: Mở cửa sổ Camera
    User->>CamTest: Đứng trước Cam và bấm phím 's'
    CamTest->>FS: Lưu ảnh vào dataset/{MSV}.jpg
    CamTest-->>Ctrl: Kết thúc tiến trình (Process exit)
    
    Ctrl->>FS: Kiểm tra xem ảnh dataset/{MSV}.jpg có tồn tại
    FS-->>Ctrl: Tồn tại
    Ctrl->>FaceApp: register_face(msv, face_path)
    FaceApp->>DB: Cập nhật trường "face_path" cho document MSV
    DB-->>FaceApp: Cập nhật thành công
    FaceApp-->>Ctrl: Trả về True
    Ctrl-->>User: Hiển thị thông báo "Đăng kí khuôn mặt thành công"
```

## 3. Sơ đồ chức năng Chấm công (Attendance Flow)

**Mô tả:** Đây là quy trình phức tạp nhất. Khi ấn "Bắt đầu chấm công", luồng UI chính (Controller) không trực tiếp xử lý camera (tránh ứng dụng bị đơ), mà sinh ra một Subprocess chạy file `attendance_cam.py`. 
Để giao tiếp giữa tiến trình chính và tiến trình camera phụ, hệ thống dùng 1 file tạm là `last_attendance.json`.
- File Camera quét khuôn mặt, tính khoảng cách mã hóa (embeddings) để xác định danh tính. Nếu thành công và người dùng chưa điểm danh trong ngày, nó ghi dữ liệu lên collection `logs` của Firestore và đồng thời nhả trạng thái SUCCESS ra file JSON.
- Ở phía UI, Controller quét (polling) liên tục file JSON đó (250ms/lần). Nếu bắt được tín hiệu SUCCESS, UI sẽ load thông tin hiển thị lên màn hình, hiện popup thông báo thành công và trực tiếp tiêu diệt tiến trình Camera để kết thúc lượt chấm công, sau đó xóa file JSON dọn dẹp.

```mermaid
sequenceDiagram
    actor User as Sinh viên / Người dùng
    participant Ctrl as ctk_controller
    participant AttCam as attendance_cam.py (Subprocess)
    participant FaceRec as face_recognition
    participant FaceApp as face_attendance
    participant DB as Firebase (logs)
    participant FS as last_attendance.json (File tạm)

    User->>Ctrl: Bấm "Bắt đầu chấm công"
    Ctrl->>Ctrl: Khởi tạo polling đọc file json mỗi 250ms
    Ctrl->>AttCam: subprocess.Popen(["attendance_cam.py"])
    
    AttCam->>FaceApp: _compute_embeddings_from_students()
    FaceApp->>DB: Tải danh sách SV (register collection)
    DB-->>FaceApp: Dữ liệu SV
    FaceApp-->>AttCam: DataFrame SV (chứa face_path)
    AttCam->>FaceRec: Đọc ảnh và tạo mã hóa (Embeddings)
    FaceRec-->>AttCam: known_encodings, known_msws
    
    loop Mỗi khung hình (Frame)
        AttCam->>User: Quét khuôn mặt từ Webcam
        AttCam->>FaceRec: detect & face_encodings
        FaceRec-->>AttCam: encoding của khung hình
        AttCam->>AttCam: _match_face() (So sánh khoảng cách)
        
        alt Nhận diện thành công & Chưa chấm hôm nay
            AttCam->>FaceApp: do_attendance(msv)
            FaceApp->>DB: Thêm bản ghi vào collection "logs"
            DB-->>FaceApp: Success
            FaceApp-->>AttCam: Trả về True
            AttCam->>FS: Ghi trạng thái (SUCCESS, MSV, Tên...) vào last_attendance.json
            Note over AttCam: Vòng lặp camera vẫn chạy, đợi UI ngắt
        end
    end
    
    loop UI Polling (Mỗi 250ms)
        Ctrl->>FS: Kiểm tra file last_attendance.json
        FS-->>Ctrl: Có file & Có trạng thái SUCCESS
        Ctrl->>Ctrl: Cập nhật giao diện (Hiện tên, MSV, ảnh)
        Ctrl->>User: Hiển thị Popup "Chấm công thành công"
        Ctrl->>AttCam: proc.terminate() (Đóng Camera)
        Ctrl->>FS: Xóa file last_attendance.json
    end
```

## 4. Sơ đồ chức năng Thống kê và Xuất báo cáo

**Mô tả:** Chức năng này phục vụ cho tab Thống Kê và Báo Cáo. 
- **Khi làm mới thống kê:** Module `attendance_stats` sẽ quét qua toàn bộ dữ liệu ở collection `register` để lấy tổng số sinh viên và đối chiếu với collection `logs` để đếm ra bao nhiêu người đã/chưa điểm danh trong ngày hôm nay. Dữ liệu này được chuyển đổi thành 2 biểu đồ Matplotlib tích hợp sẵn trong UI.
- **Khi xuất báo cáo:** Người dùng chọn định dạng Excel/CSV. Hệ thống truy vấn toàn bộ lịch sử `logs` từ Firestore về thông qua Pandas DataFrame. Cuối cùng, hàm `to_csv` hoặc `to_excel` của Pandas (cùng thư viện bổ trợ openpyxl) sẽ chuyển DataFrame thành file vật lý được lưu trữ ở ổ cứng cục bộ.

```mermaid
sequenceDiagram
    actor User as Người dùng
    participant Ctrl as ctk_controller
    participant StatsApp as attendance_stats
    participant FaceApp as face_attendance
    participant DB as Firebase
    participant Pandas as pandas (Thư viện)
    participant FS as Local FileSystem

    %% Luồng xem thống kê
    User->>Ctrl: Bấm "Làm mới biểu đồ" (refresh_stats)
    Ctrl->>StatsApp: get_today_attendance_stats_distinct()
    StatsApp->>DB: Query collection "register"
    DB-->>StatsApp: Số lượng đăng kí
    StatsApp->>DB: Query collection "logs" (Lọc theo ngày hôm nay)
    DB-->>StatsApp: Danh sách logs hôm nay
    StatsApp->>StatsApp: Tính toán unique MSV (today_marked, unmarked)
    StatsApp-->>Ctrl: Trả về đối tượng TodayAttendanceStats
    Ctrl->>Ctrl: Cập nhật KPI (Tổng số, Đã chấm, Chưa chấm)
    Ctrl->>Ctrl: make_bar_pie_figures() (Matplotlib) -> Cập nhật UI

    %% Luồng xuất Excel/CSV
    User->>Ctrl: Bấm "Xuất báo cáo"
    Ctrl->>User: Mở Popup chọn định dạng (CSV/XLSX) và Nơi lưu
    User->>Ctrl: Chọn cấu hình và bấm "Xuất"
    
    Ctrl->>FaceApp: get_history(msv="")
    FaceApp->>DB: Lấy tất cả logs từ Firestore
    DB-->>FaceApp: Toàn bộ logs
    FaceApp->>Pandas: DataFrame(rows)
    Pandas-->>FaceApp: Trả về df
    FaceApp-->>Ctrl: Trả về df
    
    Ctrl->>Pandas: export_df.to_csv() hoặc to_excel()
    Pandas->>FS: Ghi file (sử dụng openpyxl cho Excel)
    FS-->>Pandas: Ghi xong
    Pandas-->>Ctrl: Trả về kết quả
    Ctrl-->>User: Thông báo "Xuất báo cáo thành công"
```

## 5. Sơ đồ chức năng Xem lịch sử (View History)

**Mô tả:** Thao tác xem lịch sử đơn giản và phản hồi nhanh. Khi người dùng muốn làm mới toàn bộ bảng hoặc cần tra cứu hành tung của một sinh viên cụ thể (Lọc theo MSV), UI sẽ gọi xuống `face_attendance`. File này request một `stream()` toàn bộ bản ghi log trên Firestore, sau đó biến đổi sang định dạng Pandas DataFrame để sắp xếp giảm dần theo thời gian. Cuối cùng UI xóa hết dòng cũ ở bảng TreeView và nạp DataFrame mới này vào để hiển thị.

```mermaid
sequenceDiagram
    actor User as Người dùng
    participant Ctrl as ctk_controller
    participant FaceApp as face_attendance
    participant DB as Firebase (logs)
    participant View as ctk_view (TreeView)

    User->>Ctrl: Nhập MSV và bấm "Lọc" (hoặc "Làm mới")
    Ctrl->>FaceApp: get_history(msv=input_msv)
    
    FaceApp->>DB: db.collection("logs").stream()
    DB-->>FaceApp: Trả về raw docs
    
    FaceApp->>FaceApp: Lặp qua docs, tạo DataFrame
    Note over FaceApp: Nếu input_msv có giá trị, thực hiện <br/>df = df[df["msv"] == input_msv]
    FaceApp->>FaceApp: Sắp xếp theo thời gian giảm dần
    FaceApp-->>Ctrl: Trả về Pandas DataFrame
    
    Ctrl->>View: clear_tree() (Xóa dữ liệu cũ)
    
    loop Duyệt từng hàng trong DataFrame
        Ctrl->>View: tree.insert(hàng mới)
    end
    
    Ctrl-->>User: Giao diện hiển thị danh sách lịch sử mới
```
