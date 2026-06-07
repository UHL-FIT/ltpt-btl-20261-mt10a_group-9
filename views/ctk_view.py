import customtkinter as ctk
from tkinter import ttk

def create_main_window() -> tuple[ctk.CTk, dict[str, object]]:
    # Set up theme cho UI
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    # Tạo đối tượng GUI gốc
    root = ctk.CTk()
    root.title("Face Attend")
    root.geometry("1200x700")

    # ---------------- Sidebar ----------------
    sidebar = ctk.CTkFrame(root, width=220)
    sidebar.pack(side="left", fill="y")

    ctk.CTkLabel(sidebar, text="Face Attend", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(20, 5))
    ctk.CTkLabel(sidebar, text="Menu", font=ctk.CTkFont(size=15)).pack(pady=(0, 10))

    # ---------------- Content Area ----------------
    content = ctk.CTkFrame(root, corner_radius=12)
    content.pack(side="right", fill="both", expand=True)

    # Tạo các page chức năng
    pages = {
        "attendance": ctk.CTkFrame(content, corner_radius=12),
        "register": ctk.CTkFrame(content, corner_radius=12),
        "stats": ctk.CTkFrame(content, corner_radius=12),
        "history": ctk.CTkFrame(content, corner_radius=12),
    }

    pages["attendance"].place(in_=content, x=0, y=0, relwidth=1, relheight=1)
    pages["register"].place(in_=content, x=0, y=0, relwidth=1, relheight=1)
    pages["stats"].place(in_=content, x=0, y=0, relwidth=1, relheight=1)
    pages["history"].place(in_=content, x=0, y=0, relwidth=1, relheight=1)

    # Ẩn các page
    for p, frame in pages.items():
        frame.place_forget()

    # Hiển thị lại page Attendance, đặt làm mặc định hiển thị
    pages["attendance"].place(in_=content, x=0, y=0, relwidth=1, relheight=1)

    # Hiển thị page tương ứng chọn
    def show_page(page):
        for p, frame in pages.items():
            frame.place_forget()
        pages[page].place(in_=content, x=0, y=0, relwidth=1, relheight=1)

    # Tạo dict quản lý các đối tượng GUI
    ui: dict[str, object] = {"root": root, "show_page": show_page}

    # Sidebar buttons (để các page khác hoạt động)
    ui["btn_nav_att"] = ctk.CTkButton(sidebar, text="Chấm công", command=lambda: show_page("attendance"))
    ui["btn_nav_reg"] = ctk.CTkButton(sidebar, text="Đăng ký", command=lambda: show_page("register"))
    ui["btn_nav_stats"] = ctk.CTkButton(sidebar, text="Thống kê", command=lambda: show_page("stats"))
    ui["btn_nav_history"] = ctk.CTkButton(sidebar, text="Lịch sử", command=lambda: show_page("history"))

    ui["btn_nav_att"].pack(pady=8, padx=14)
    ui["btn_nav_reg"].pack(pady=8, padx=14)
    ui["btn_nav_stats"].pack(pady=8, padx=14)
    ui["btn_nav_history"].pack(pady=8, padx=14)

    ui["btn_about"] = ctk.CTkButton(sidebar, text="ℹ Giới thiệu", fg_color="#FF8C00")
    ui["btn_about"].pack(side="bottom", pady=20, padx=14)

    ui["btn_help"] = ctk.CTkButton(sidebar, text="? Hướng dẫn", fg_color="#22C55E")
    ui["btn_help"].pack(side="bottom", pady=8, padx=14)



    # ---------------- Attendance Page ----------------
    att = pages["attendance"]

    # Chia 2 frame chính: Left ~70% / Right ~30%
    att.grid_columnconfigure(0, weight=7)
    att.grid_columnconfigure(1, weight=3)
    att.grid_rowconfigure(0, weight=1)

    # 2 frame left và right
    left_att = ctk.CTkFrame(att, corner_radius=12)
    left_att.grid(row=0, column=0, padx=14, pady=14, sticky="nsew")
    right_att = ctk.CTkFrame(att, corner_radius=12)
    right_att.grid(row=0, column=1, padx=14, pady=14, sticky="nsew")

    # -------- Left Frame --------
    left_att.grid_rowconfigure(1, weight=1)
    left_att.grid_columnconfigure(0, weight=1)

    # Button Chấm công
    ui["btn_start_attendance"] = ctk.CTkButton(
        left_att,
        text="Chấm công",
        height=52,
        font=ctk.CTkFont(size=22, weight="bold"),
    )
    ui["btn_start_attendance"].grid(row=0, column=0, padx=16, pady=(16, 10), sticky="ew")

    # Vùng mở cam chấm công
    ui["frame_cam_attendance"] = ctk.CTkFrame(
        left_att,
        corner_radius=12,
        fg_color="#1e1e1e",
    )
    ui["frame_cam_attendance"].grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
    
    # -------- Right Frame --------
    ctk.CTkLabel(right_att, text="Thông tin chấm công", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(18, 10))

    # Vùng hiển thị thông tin chấm công
    ui["frame_info_display"] = ctk.CTkFrame(
        right_att,
        corner_radius=12,
        fg_color="#333333",
    )
    ui["frame_info_display"].pack(fill="both", expand=True, padx=14, pady=(0, 14))

    items = [
        ("Mã SV", "---", "lbl_msv"),
        ("Họ tên", "---", "lbl_hoten"),
        ("Lớp", "---", "lbl_lop"),
        ("SĐT", "---", "lbl_sdt"),
        ("Thời gian", "---", "lbl_thoigian"),
    ]

    for r, (title, value, key) in enumerate(items):
        ctk.CTkLabel(
            ui["frame_info_display"],
            text=f"{title}:",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white",
        ).grid(row=r, column=0, sticky="w", padx=(18, 10), pady=(14 if r == 0 else 8, 0))

        ui[key] = ctk.CTkLabel(
            ui["frame_info_display"],
            text=value,
            anchor="w",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff",
        )
        ui[key].grid(row=r, column=1, sticky="w", padx=(0, 18), pady=(14 if r == 0 else 8, 0))


    # ---------------- Register Page ----------------
    reg = pages["register"]
    
    # Chia 2 frame chính: Left / Right = 50%
    reg.grid_columnconfigure(0, weight=1)
    reg.grid_columnconfigure(1, weight=1)

    # 2 frame Left và Right
    left_reg = ctk.CTkFrame(reg, corner_radius=12)
    left_reg.grid(row=0, column=0, padx=14, pady=14, sticky="nsew")
    right_reg = ctk.CTkFrame(reg, corner_radius=12)
    right_reg.grid(row=0, column=1, padx=14, pady=14, sticky="nsew")

    # -------- Left Frame --------
    ctk.CTkLabel(left_reg, text="Đăng ký chấm công", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(18,0))

    # Tạo frame nhập thông tin
    reg_form = ctk.CTkFrame(left_reg, corner_radius=12)
    reg_form.pack(fill="both", expand=True, padx=14, pady=8)

    # Đẩy vùng các ô nhập thông tin ra giữa
    reg_form.grid_columnconfigure(0, weight=1)  # Cân bằng cột bên trái
    reg_form.grid_columnconfigure(1, weight=1)  # Cân bằng cột bên phải
    
    # Cho tất cả 7 hàng tự co giãn để ép cụm nhập liệu vào giữa theo chiều dọc
    for i in range(8):
        reg_form.grid_rowconfigure(i, weight=1)


    # Các ô nhập liệu (Có chỉnh sửa lại padx để thụt lề 2 bên cho cân đối)
    ctk.CTkLabel(reg_form, text="MSV:").grid(row=0, column=0, sticky="w", padx=(50, 10), pady=8)
    ui["ent_reg_msv"] = ctk.CTkEntry(reg_form, width=260)
    ui["ent_reg_msv"].grid(row=0, column=1, sticky="w", padx=(10, 50), pady=8)

    ctk.CTkLabel(reg_form, text="Họ tên:").grid(row=1, column=0, sticky="w", padx=(50, 10), pady=8)
    ui["ent_reg_name"] = ctk.CTkEntry(reg_form, width=260)
    ui["ent_reg_name"].grid(row=1, column=1, sticky="w", padx=(10, 50), pady=8)

    ctk.CTkLabel(reg_form, text="Lớp:").grid(row=2, column=0, sticky="w", padx=(50, 10), pady=8)
    ui["ent_reg_lop"] = ctk.CTkEntry(reg_form, width=260)
    ui["ent_reg_lop"].grid(row=2, column=1, sticky="w", padx=(10, 50), pady=8)

    ctk.CTkLabel(reg_form, text="SĐT:").grid(row=3, column=0, sticky="w", padx=(50, 10), pady=8)
    ui["ent_reg_sdt"] = ctk.CTkEntry(reg_form, width=260)
    ui["ent_reg_sdt"].grid(row=3, column=1, sticky="w", padx=(10, 50), pady=8)

    # Các nút bấm và Trạng thái (Sửa lại padx để thụt lề đồng bộ với ô nhập)
    ui["btn_register_student"] = ctk.CTkButton(reg_form, text="Lưu thông tin", fg_color="#1E90FF")
    ui["btn_register_student"].grid(row=4, column=0, columnspan=2, padx=50, pady=10, sticky="ew")

    ui["btn_register_face"] = ctk.CTkButton(reg_form, text="Đăng ký", fg_color="#A020F0")
    ui["btn_register_face"].grid(row=5, column=0, columnspan=2, padx=50, pady=6, sticky="ew")

    # Nút Xóa sinh viên
    ui["btn_delete_student"] = ctk.CTkButton(reg_form, text="Xóa sinh viên", fg_color="#EF4444")
    ui["btn_delete_student"].grid(row=6, column=0, columnspan=2, padx=50, pady=6, sticky="ew")

    ui["lbl_reg_status"] = ctk.CTkLabel(reg_form, text="Trạng thái: sẵn sàng", anchor="w")

    ui["lbl_reg_status"].grid(row=7, column=0, columnspan=2, padx=50, pady=(12, 0), sticky="w")

    
    # ---------------- Right Frame ----------------
    ui["frame_camera"] = ctk.CTkFrame(
        right_reg,
        corner_radius=10,
        fg_color="#1e1e1e",
    )
    ui["frame_camera"].pack(fill="both", expand=True, padx=14, pady=14)


    # ---------------- Stats Page ----------------
    stats = pages["stats"]

    stats.grid_columnconfigure(0, weight=1)
    stats.grid_columnconfigure(1, weight=1)

    from views.ctk_stats_view import StatsView

    stats_view = StatsView(stats)
    ui["stats_view"] = stats_view

    ui["btn_refresh_stats"] = ctk.CTkButton(stats, text="Làm mới", fg_color="#28A745")
    ui["btn_refresh_stats"].pack(pady=(0, 18))


    # ---------------- History Page ----------------
    his = pages["history"]

    his.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(his, text="Lịch sử chấm công", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=18)

    filter_frame = ctk.CTkFrame(his, corner_radius=12)
    filter_frame.pack(fill="x", padx=18, pady=10)

    ctk.CTkLabel(filter_frame, text="MSV:").grid(row=0, column=0, padx=10, pady=10, sticky="w")

    ui["ent_hist_msv"] = ctk.CTkEntry(filter_frame, width=220)
    ui["ent_hist_msv"].grid(row=0, column=1, padx=10, pady=10, sticky="w")

    ui["btn_hist_filter"] = ctk.CTkButton(filter_frame, text="Lọc", fg_color="#1E90FF")
    ui["btn_hist_filter"].grid(row=0, column=2, padx=10, pady=10)

    ui["btn_hist_refresh"] = ctk.CTkButton(filter_frame, text="Làm mới", fg_color="#28A745")
    ui["btn_hist_refresh"].grid(row=0, column=3, padx=10, pady=10)

    ui["btn_export_report"] = ctk.CTkButton(filter_frame, text="Xuất báo cáo", fg_color="#A020F0")
    ui["btn_export_report"].grid(row=0, column=4, padx=10, pady=10)

    # Tạo bảng lịch sử chấm công: MaSV, HoTen, Lop, SĐT, Time
    history_table = ctk.CTkFrame(his, corner_radius=12)
    history_table.pack(fill="both", expand=True, padx=18, pady=14)

    cols = ["msv", "name", "class", "phone_number", "time"]

    ui["tree_history"] = ttk.Treeview(history_table, columns=cols, show="headings", height=18)
    ui["tree_history"].pack(fill="both", expand=True)

    # Set độ rộng theo cột
    col_width = {
        "msv": 120,
        "name": 180,
        "class": 120,
        "phone_number": 160,
        "time": 240,
    }

    for c in cols:
        ui["tree_history"].heading(c, text=c)
        ui["tree_history"].column(c, width=col_width.get(c, 140))

    return root, ui

