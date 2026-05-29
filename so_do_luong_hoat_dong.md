# SƠ ĐỒ LUỒNG HOẠT ĐỘNG HỆ THỐNG ĐIỂM DANH KHUÔN MẶT

Tài liệu này chứa các sơ đồ luồng hoạt động (Activity Flowcharts) chi tiết của toàn bộ hệ thống điểm danh bằng khuôn mặt tích hợp cơ sở dữ liệu Cloud Firestore. 

> [!TIP]
> Tất cả các sơ đồ dưới đây đã được cấu hình tăng kích thước chữ lên **18px** và **tự động in đậm (bold)**. Khi xuất ra file ảnh chèn vào Word, chữ sẽ hiển thị cực kỳ to, rõ ràng và dễ đọc ngay cả khi thu nhỏ biểu đồ.

---

## 1. SƠ ĐỒ LUỒNG TỔNG QUAN CƠ BẢN (High-Level Overview Flow) - KHUYÊN DÙNG ĐỂ KHỞI ĐẦU BÁO CÁO

Đây là sơ đồ mức độ cao (High-Level) mô tả tổng quát 4 nhánh tính năng chính của hệ thống một cách đơn giản, dễ hiểu theo đúng trải nghiệm của người dùng:

```mermaid
%%{init: {'themeVariables': { 'fontSize': '18px', 'fontFamily': 'Segoe UI, Arial' }, 'themeCSS': '.node text { font-weight: bold; }'}}%%
graph TD
    %% Định nghĩa phong cách (Styles)
    classDef startEnd fill:#F3F4F6,stroke:#374151,stroke-width:2px,rx:10px,ry:10px;
    classDef process fill:#EFF6FF,stroke:#3B82F6,stroke-width:2px;
    classDef db fill:#FEF3C7,stroke:#D97706,stroke-width:2px;

    Start([Người dùng mở ứng dụng]) --> MainUI[Giao diện chính - Chọn chức năng]

    %% Nhánh 1: Đăng ký
    MainUI -->|1. Tab Đăng ký| RegFlow[Đăng ký thông tin cá nhân & Chụp ảnh khuôn mặt]
    RegFlow --> dbStore[(Lưu trữ vào Firestore database)]

    %% Nhánh 2: Điểm danh
    MainUI -->|2. Tab Điểm danh| CamFlow[Camera nhận diện khuôn mặt dựa trên dataset]
    dbStore -.->|Đối chiếu dữ liệu ảnh| CamFlow
    CamFlow --> Notification[Hiển thị thông báo kết quả chấm công trên giao diện]

    %% Nhánh 3: Lịch sử
    MainUI -->|3. Tab Lịch sử| HistFlow[Xem lịch sử chấm công & Xuất báo cáo Excel/CSV]
    dbStore -.->|Lấy dữ liệu logs| HistFlow

    %% Nhánh 4: Thống kê
    MainUI -->|4. Tab Thống kê| StatsFlow[Xem biểu đồ KPI trực quan hóa dữ liệu chấm công]
    dbStore -.->|Tổng hợp dữ liệu| StatsFlow

    class Start startEnd;
    class MainUI,RegFlow,CamFlow,Notification,HistFlow,StatsFlow process;
    class dbStore db;
```

### Giải thích sơ đồ luồng tổng quan cơ bản:
*   **Bước khởi đầu:** Người dùng mở ứng dụng giao diện chính và lựa chọn 1 trong 4 tab chức năng.
*   **Nhánh Đăng ký:** Cho phép nhập thông tin cá nhân và liên kết ảnh khuôn mặt (chụp từ Webcam), toàn bộ dữ liệu này được đẩy trực tiếp lên Cloud Firestore để lưu giữ.
*   **Nhánh Điểm danh:** Hệ thống mở camera, trích xuất dữ liệu ảnh và so khớp với các mẫu đặc trưng khuôn mặt (dataset) đã lưu trên Firestore. Khi có kết quả, hệ thống hiển thị hộp thoại thông báo thành công hoặc cảnh báo trùng lặp.
*   **Nhánh Lịch sử:** Truy xuất danh sách log điểm danh từ database để hiển thị lên bảng tìm kiếm và cho phép kết xuất ra file Excel/CSV báo cáo.
*   **Nhánh Thống kê:** Tổng hợp dữ liệu chấm công thực tế để vẽ biểu đồ trực quan giúp quản lý theo dõi dễ dàng.

---

## 2. SƠ ĐỒ LUỒNG KIẾN TRÚC KỸ THUẬT HỆ THỐNG (Technical Architecture Flow)

Sơ đồ này mô tả chi tiết hơn về cách các tiến trình Python kết hợp với nhau cùng cơ sở dữ liệu:

```mermaid
%%{init: {'themeVariables': { 'fontSize': '18px', 'fontFamily': 'Segoe UI, Arial' }, 'themeCSS': '.node text { font-weight: bold; }'}}%%
graph TD
    %% Định nghĩa phong cách (Styles)
    classDef startEnd fill:#F3F4F6,stroke:#374151,stroke-width:2px,rx:10px,ry:10px;
    classDef process fill:#EFF6FF,stroke:#3B82F6,stroke-width:2px;
    classDef db fill:#FEF3C7,stroke:#D97706,stroke-width:2px;
    classDef decision fill:#ECFDF5,stroke:#10B981,stroke-width:2px;
    classDef subprocess fill:#F5F3FF,stroke:#8B5CF6,stroke-width:2px;

    Start([Khởi động Ứng dụng GUI]) --> MainUI[Giao diện chính CustomTkinter]
    
    %% Tab 1: Đăng ký
    MainUI -->|Tab Đăng ký| RegForm[Nhập thông tin MSV, Họ tên, Lớp, SĐT]
    RegForm --> SaveStudent[Lưu thông tin Sinh viên]
    SaveStudent --> dbRegister[(Firestore: Collection 'register')]
    
    RegForm --> RegFace[Đăng ký khuôn mặt]
    RegFace -->|Chạy Subprocess| CamTestCam[Camera Chụp Ảnh test_cam.py]
    CamTestCam -->|Nhấn 's' để lưu| SaveImg[Lưu ảnh vào dataset/MSV.jpg]
    SaveImg --> LinkFace[Liên kết đường dẫn face_path]
    LinkFace --> dbRegister

    %% Tab 2: Điểm danh
    MainUI -->|Tab Điểm danh| StartCam[Bắt đầu Điểm danh]
    StartCam -->|Chạy Subprocess| CamAttendance[Camera Nhận Diện attendance_cam.py]
    
    %% Camera Process
    CamAttendance --> LoadDB[Tải dữ liệu đăng ký & log hôm nay từ Firestore]
    dbRegister -.-> LoadDB
    dbLogs -.-> LoadDB
    
    LoadDB --> FrameLoop[Xử lý từng khung hình Camera]
    FrameLoop --> MatchFace{Khớp Khuôn Mặt?}
    MatchFace -->|Không khớp| LabelUnknown[Hiển thị nhãn UNKNOWN]
    MatchFace -->|Khớp SV| CheckMarked{Đã chấm công hôm nay?}
    
    CheckMarked -->|Đã chấm| ShowAlreadyMarked[Hiển thị DA CHAM HOM NAY & báo về UI]
    CheckMarked -->|Chưa chấm| SaveAttendance[Ghi log điểm danh mới]
    SaveAttendance --> dbLogs[(Firestore: Collection 'logs')]
    SaveAttendance --> UpdateUI[Báo Chấm công thành công & hiện Popup UI]

    %% Tab 3 & 4: Lịch sử & Thống kê
    MainUI -->|Tab Lịch sử| ViewHistory[Xem lịch sử & Tìm kiếm theo Mã SV]
    dbLogs -.-> ViewHistory
    ViewHistory --> Export[Xuất báo cáo Excel/CSV với Tiêu đề Tiếng Việt]
    
    MainUI -->|Tab Thống kê| ViewStats[Tính toán KPI & Vẽ biểu đồ bằng Matplotlib]
    dbRegister -.-> ViewStats
    dbLogs -.-> ViewStats

    class Start startEnd;
    class RegForm,RegFace,SaveStudent,SaveImg,LinkFace,FrameLoop,LabelUnknown,ShowAlreadyMarked,ViewHistory,ViewStats,Export,UpdateUI process;
    class dbRegister,dbLogs db;
    class MatchFace,CheckMarked decision;
    class CamTestCam,CamAttendance subprocess;
```

---

## 3. Luồng chi tiết: Đăng ký Sinh viên & Khuôn mặt (Student & Face Registration)

Mô tả chi tiết luồng xử lý dữ liệu khi người dùng thêm thông tin sinh viên mới và chụp ảnh khuôn mặt:

```mermaid
%%{init: {'themeVariables': { 'fontSize': '18px', 'fontFamily': 'Segoe UI, Arial' }, 'themeCSS': '.node text { font-weight: bold; }'}}%%
graph TD
    classDef startEnd fill:#F3F4F6,stroke:#374151,stroke-width:2px,rx:10px,ry:10px;
    classDef process fill:#EFF6FF,stroke:#3B82F6,stroke-width:2px;
    classDef db fill:#FEF3C7,stroke:#D97706,stroke-width:2px;
    classDef decision fill:#ECFDF5,stroke:#10B981,stroke-width:2px;

    Start([Bắt đầu Đăng ký]) --> InputInfo[Nhập MSV, Họ tên, Lớp, SĐT]
    InputInfo --> ClickSave[Nhấn nút 'Lưu sinh viên']
    ClickSave --> CheckFields{Các trường hợp lệ?}
    
    CheckFields -->|Trống thông tin| ErrEmpty[Hiển thị thông báo lỗi trên UI]
    CheckFields -->|Hợp lệ| CheckExist{Kiểm tra tồn tại trên Firestore?}
    dbRegister[(Firestore: Collection 'register')] -.-> CheckExist
    
    CheckExist -->|Đã tồn tại MSV| ErrExist[Báo lỗi: MSV đã tồn tại]
    CheckExist -->|Chưa tồn tại| WriteFirestore[Ghi document mới với ID = MSV]
    WriteFirestore --> dbRegister
    WriteFirestore --> SuccessSave[Báo lưu thông tin thành công]
    
    SuccessSave --> ClickCam[Nhấn nút 'Đăng ký khuôn mặt']
    ClickCam --> CheckSaved{MSV đã được lưu trước đó?}
    CheckSaved -->|Chưa lưu| ErrNotSaved[Yêu cầu 'Lưu sinh viên' trước]
    CheckSaved -->|Đã lưu| OpenCam[Mở tiến trình Camera test_cam.py]
    
    OpenCam --> ShowPreview[Xem hình ảnh trực tiếp từ Webcam]
    ShowPreview --> PressKey{Nhấn phím?}
    PressKey -->|Phím ESC hoặc q| CloseCam[Đóng Camera không lưu]
    PressKey -->|Phím s| Capture[Chụp ảnh khuôn mặt]
    
    Capture --> SaveDataset[Lưu tệp ảnh vào dataset/MSV.jpg]
    SaveDataset --> UpdateFacePath[Cập nhật trường face_path vào Firestore]
    UpdateFacePath --> dbRegister
    UpdateFacePath --> FinalSuccess([Hoàn thành Đăng ký Sinh viên & Khuôn mặt])

    class Start,FinalSuccess startEnd;
    class InputInfo,ClickSave,ErrEmpty,ErrExist,WriteFirestore,SuccessSave,ClickCam,ErrNotSaved,OpenCam,ShowPreview,CloseCam,Capture,SaveDataset,UpdateFacePath process;
    class dbRegister db;
    class CheckFields,CheckExist,CheckSaved,PressKey decision;
```

---

## 4. Luồng chi tiết: Điểm danh bằng Nhận diện khuôn mặt (Face Attendance Check-in)

Mô tả logic nhận diện và đối chiếu với danh sách chấm công để chống trùng lặp trong ngày:

```mermaid
%%{init: {'themeVariables': { 'fontSize': '18px', 'fontFamily': 'Segoe UI, Arial' }, 'themeCSS': '.node text { font-weight: bold; }'}}%%
graph TD
    classDef startEnd fill:#F3F4F6,stroke:#374151,stroke-width:2px,rx:10px,ry:10px;
    classDef process fill:#EFF6FF,stroke:#3B82F6,stroke-width:2px;
    classDef db fill:#FEF3C7,stroke:#D97706,stroke-width:2px;
    classDef decision fill:#ECFDF5,stroke:#10B981,stroke-width:2px;

    Start([Nhấn nút 'Bắt đầu Điểm danh']) --> OpenCam[Mở Camera Điểm danh attendance_cam.py]
    OpenCam --> InitApp[Khởi tạo tiến trình Camera]
    
    InitApp --> FetchRegister[Đọc danh sách sinh viên & trích xuất đặc trưng ảnh khuôn mặt]
    dbRegister[(Firestore: Collection 'register')] -.-> FetchRegister
    
    InitApp --> FetchLogs[Tải danh sách các ID sinh viên đã chấm công ngày hôm nay]
    dbLogs[(Firestore: Collection 'logs')] -.-> FetchLogs
    
    FetchLogs --> StartLoop[Bắt đầu vòng lặp đọc khung hình từ Webcam]
    StartLoop --> ReadFrame[Đọc và lật khung hình BGR sang RGB]
    ReadFrame --> DetectFaces[Phát hiện vị trí các khuôn mặt trong khung hình]
    DetectFaces --> ExtractEmbeddings[Trích xuất Vector đặc trưng khuôn mặt]
    
    ExtractEmbeddings --> CompareFace{So sánh đặc trưng với cơ sở dữ liệu?}
    CompareFace -->|Sai lệch > 0.6| ShowUnknown[Hiển thị nhãn UNKNOWN khung màu đỏ]
    CompareFace -->|Sai lệch <= 0.6| FindBestMatch[Xác định sinh viên khớp tốt nhất]
    
    FindBestMatch --> CheckMarked{Mã sinh viên có trong danh sách đã chấm hôm nay?}
    
    CheckMarked -->|CÓ| ShowAlready[Vẽ nhãn DA CHAM HOM NAY - Gửi trạng thái ALREADY_MARKED_TODAY]
    ShowAlready --> PopupAlert[Giao diện chính hiện hộp thoại cảnh báo: Đã chấm công hôm nay]
    PopupAlert --> Terminate([Đóng tiến trình Camera])

    CheckMarked -->|KHÔNG| RecordLog[Ghi log chấm công mới lên Firestore]
    RecordLog --> dbLogs
    RecordLog --> AddMarked[Thêm mã sinh viên vào danh sách đã chấm trong phiên chạy]
    AddMarked --> ShowSuccess[Vẽ nhãn OK - Gửi trạng thái SUCCESS]
    ShowSuccess --> PopupSuccess[Giao diện chính hiện hộp thoại: Chấm công thành công]
    PopupSuccess --> Terminate

    class Start,Terminate startEnd;
    class OpenCam,InitApp,FetchRegister,FetchLogs,StartLoop,ReadFrame,DetectFaces,ExtractEmbeddings,ShowUnknown,FindBestMatch,ShowAlready,PopupAlert,RecordLog,AddMarked,ShowSuccess,PopupSuccess process;
    class dbRegister,dbLogs db;
    class CompareFace,CheckMarked decision;
```

---

## 5. Luồng chi tiết: Thống kê & Xuất báo cáo (Stats & Export Report)

Mô tả cách ứng dụng hiển thị báo cáo trực quan dưới dạng đồ thị và xuất báo cáo:

```mermaid
%%{init: {'themeVariables': { 'fontSize': '18px', 'fontFamily': 'Segoe UI, Arial' }, 'themeCSS': '.node text { font-weight: bold; }'}}%%
graph TD
    classDef startEnd fill:#F3F4F6,stroke:#374151,stroke-width:2px,rx:10px,ry:10px;
    classDef process fill:#EFF6FF,stroke:#3B82F6,stroke-width:2px;
    classDef db fill:#FEF3C7,stroke:#D97706,stroke-width:2px;
    classDef decision fill:#ECFDF5,stroke:#10B981,stroke-width:2px;

    Start([Người dùng vào Tab Thống kê / Lịch sử]) --> InitStats[Tự động tải lại dữ liệu]
    
    %% Thống kê
    InitStats --> LoadRegister[Tải danh sách đăng ký trong register]
    dbRegister[(Firestore: Collection 'register')] -.-> LoadRegister
    
    InitStats --> LoadLogs[Tải danh sách log điểm danh trong logs]
    dbLogs[(Firestore: Collection 'logs')] -.-> LoadLogs
    
    LoadRegister & LoadLogs --> ComputeKPIs[Tính toán KPI: Tổng SV, Đã chấm hôm nay, Chưa chấm]
    ComputeKPIs --> Matplotlib[Dùng thư viện Matplotlib dựng Biểu đồ cột & Biểu đồ tròn]
    Matplotlib --> RenderUI[Nhúng đồ thị trực tiếp vào giao diện CustomTkinter]

    %% Xuất báo cáo
    InitStats --> ClickExport[Nhấn nút 'Xuất báo cáo']
    ClickExport --> ShowDialog[Hiển thị hộp thoại hiện đại CTkToplevel]
    ShowDialog --> Config[Người dùng chọn định dạng Excel/CSV & đường dẫn lưu file]
    Config --> ClickDoExport[Nhấn nút 'Xuất']
    
    ClickDoExport --> LoadFullLogs[Truy vấn toàn bộ logs từ Firestore]
    LoadFullLogs --> FilterCols[Lọc đúng 5 cột: Mã SV, Họ tên, Lớp, Số điện thoại, Thời gian]
    FilterCols --> WriteFile{Ghi file ra đĩa thành công?}
    
    WriteFile -->|Thành công| SuccessMsg[Báo thành công & hiển thị đường dẫn tệp tin]
    WriteFile -->|Lỗi ghi/quyền| ErrMsg[Hiển thị thông báo lỗi ghi file]
    
    SuccessMsg & ErrMsg --> End([Kết thúc tác vụ])

    class Start,End startEnd;
    class InitStats,LoadRegister,LoadLogs,ComputeKPIs,Matplotlib,RenderUI,ClickExport,ShowDialog,Config,ClickDoExport,LoadFullLogs,FilterCols,SuccessMsg,ErrMsg process;
    class dbRegister,dbLogs db;
    class WriteFile decision;
```
