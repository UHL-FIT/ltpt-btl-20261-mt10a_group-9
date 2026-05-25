import customtkinter as ctk
from tkinter import ttk
from typing import Dict

# Set up theme cho UI
def setup_ctk_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

def create_main_window() -> tuple[ctk.CTk, Dict[str, object]]:
    setup_ctk_theme()

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
    content.pack(side="right", fill="both", expand=True, padx=12, pady=12)

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
    for k, frame in pages.items():
        frame.place_forget()
    pages["attendance"].place(in_=content, x=0, y=0, relwidth=1, relheight=1)

    # Hiển thị page tương ứng chọn
    def show_page(page):
        for k, frame in pages.items():
            frame.place_forget()
        pages[page].place(in_=content, x=0, y=0, relwidth=1, relheight=1)


    # ---------------- Attendance Page (CustomTkinter layout) ----------------
    att = pages["attendance"]

    # 2 cột chính: Left ~70% / Right ~30%
    att.grid_columnconfigure(0, weight=7)
    att.grid_columnconfigure(1, weight=3)
    att.grid_rowconfigure(0, weight=1)

    # Frame tổng (chứa 2 cột)
    left_frame = ctk.CTkFrame(att, corner_radius=12)
    left_frame.grid(row=0, column=0, padx=14, pady=14, sticky="nsew")

    right_frame = ctk.CTkFrame(att, corner_radius=12)
    right_frame.grid(row=0, column=1, padx=14, pady=14, sticky="nsew")

    # -------- Left Frame --------
    left_frame.grid_rowconfigure(1, weight=1)
    left_frame.grid_columnconfigure(0, weight=1)

    ui: Dict[str, object] = {"root": root}

    # Button Chấm công
    ui["btn_start_attendance"] = ctk.CTkButton(
        left_frame,
        text="Chấm công",
        height=52,
        font=ctk.CTkFont(size=22, weight="bold"),
    )
    ui["btn_start_attendance"].grid(row=0, column=0, padx=16, pady=(16, 10), sticky="ew")

    # Vùng mở cam chấm công
    ui["frame_cam_attendance"] = ctk.CTkFrame(
        left_frame,
        corner_radius=12,
        fg_color="#1e1e1e",
    )
    ui["frame_cam_attendance"].grid(row=1, column=0, padx=16, pady=(0, 16), sticky="nsew")
    ui["frame_cam_attendance"].grid_rowconfigure(0, weight=1)
    ui["frame_cam_attendance"].grid_columnconfigure(0, weight=1)

    ui["label_cam_state"] = ctk.CTkLabel(
        ui["frame_cam_attendance"],
        text="Camera đang tắt - Nhấn nút để chấm công",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#d0d0d0",
        fg_color="#1e1e1e",
        justify="center",
        wraplength=420,
    )
    ui["label_cam_state"].grid(row=0, column=0, padx=12, pady=12, sticky="nsew")

    # -------- Right side (Info) --------
    right_frame.grid_rowconfigure(0, weight=1)
    right_frame.grid_columnconfigure(0, weight=1)

    ctk.CTkLabel(right_frame, text="Thông tin chấm công", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(18, 8))

    # Vùng hiển thị thông tin chấm công
    ui["frame_info_display"] = ctk.CTkFrame(
        right_frame,
        corner_radius=12,
        fg_color="#333333",
    )
    ui["frame_info_display"].pack(fill="both", expand=True, padx=14, pady=14)

    items = [
        ("Mã SV", "---", "lbl_msv"),
        ("Họ tên", "---", "lbl_hoten"),
        ("Lớp", "---", "lbl_lop"),
        ("SĐT", "---", "lbl_sdt"),
        ("Thời gian", "---", "lbl_thoigian"),
    ]

    for r, (title, value, key) in enumerate(items):
        grid_r = r + 1
        ctk.CTkLabel(
            ui["frame_info_display"],
            text=f"{title}:",
            anchor="w",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#eaeaea",
        ).grid(row=grid_r, column=0, sticky="w", padx=(18, 10), pady=(14 if r == 0 else 8, 0))

        ui[key] = ctk.CTkLabel(
            ui["frame_info_display"],
            text=value,
            anchor="w",
            font=ctk.CTkFont(size=14),
            text_color="#ffffff",
        )
        ui[key].grid(row=grid_r, column=1, sticky="w", padx=(0, 18), pady=(14 if r == 0 else 8, 0))

    # Sidebar buttons (để các page khác hoạt động)
    ui["btn_nav_att"] = ctk.CTkButton(sidebar, text="Chấm công", command=lambda: show_page("attendance"))
    ui["btn_nav_reg"] = ctk.CTkButton(sidebar, text="Đăng ký", command=lambda: show_page("register"))
    ui["btn_nav_stats"] = ctk.CTkButton(sidebar, text="Thống kê", command=lambda: show_page("stats"))
    ui["btn_nav_history"] = ctk.CTkButton(sidebar, text="Lịch sử", command=lambda: show_page("history"))

    ui["btn_nav_att"].pack(pady=8, padx=14)
    ui["btn_nav_reg"].pack(pady=8, padx=14)
    ui["btn_nav_stats"].pack(pady=8, padx=14)
    ui["btn_nav_history"].pack(pady=8, padx=14)


    # ---------------- Register Page ----------------
    reg = pages["register"]
    reg.grid_columnconfigure(0, weight=1)
    reg.grid_columnconfigure(1, weight=1)

    card_reg_left = ctk.CTkFrame(reg, corner_radius=12)
    card_reg_left.grid(row=0, column=0, padx=14, pady=14, sticky="nsew")
    card_reg_right = ctk.CTkFrame(reg, corner_radius=12)
    card_reg_right.grid(row=0, column=1, padx=14, pady=14, sticky="nsew")

    ctk.CTkLabel(card_reg_left, text="Đăng ký chấm công", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(18, 8))

    reg_form = ctk.CTkFrame(card_reg_left, corner_radius=12)
    reg_form.pack(fill="both", expand=True, padx=14, pady=14)

    ctk.CTkLabel(reg_form, text="MSV:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
    ui["ent_reg_msv"] = ctk.CTkEntry(reg_form, width=260)
    ui["ent_reg_msv"].grid(row=0, column=1, padx=10, pady=8)

    ctk.CTkLabel(reg_form, text="Họ tên:").grid(row=1, column=0, sticky="w", padx=10, pady=8)
    ui["ent_reg_name"] = ctk.CTkEntry(reg_form, width=260)
    ui["ent_reg_name"].grid(row=1, column=1, padx=10, pady=8)

    ctk.CTkLabel(reg_form, text="Lớp:").grid(row=2, column=0, sticky="w", padx=10, pady=8)
    ui["ent_reg_lop"] = ctk.CTkEntry(reg_form, width=260)
    ui["ent_reg_lop"].grid(row=2, column=1, padx=10, pady=8)

    ctk.CTkLabel(reg_form, text="SĐT:").grid(row=3, column=0, sticky="w", padx=10, pady=8)
    ui["ent_reg_sdt"] = ctk.CTkEntry(reg_form, width=260)
    ui["ent_reg_sdt"].grid(row=3, column=1, padx=10, pady=8)

    ui["btn_register_student"] = ctk.CTkButton(reg_form, text="Lưu sinh viên", fg_color="#1E90FF")
    ui["btn_register_student"].grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    ui["btn_register_face"] = ctk.CTkButton(reg_form, text="Đăng ký", fg_color="#A020F0")
    ui["btn_register_face"].grid(row=5, column=0, columnspan=2, padx=10, pady=6, sticky="ew")

    ui["lbl_reg_status"] = ctk.CTkLabel(reg_form, text="Trạng thái: sẵn sàng", anchor="w")
    ui["lbl_reg_status"].grid(row=6, column=0, columnspan=2, padx=10, pady=(12, 0), sticky="w")


    # ---------------- Camera frame (Register Page - Right side) ----------------
    frame_camera = ctk.CTkFrame(
        card_reg_right,
        corner_radius=10,
        fg_color="#2b2b2b",
    )
    frame_camera.pack(fill="both", expand=True, padx=14, pady=14)

    ui["frame_camera"] = frame_camera

    ui["label_video"] = ctk.CTkLabel(
        frame_camera,
        text="Hệ thống sẵn sàng - Nhấn Đăng ký để mở Camera",
        font=ctk.CTkFont(size=16, weight="bold"),
        text_color="#00E5FF",
        justify="center",
        wraplength=800,
    )
    ui["label_video"].pack(expand=True, fill="both")


    # ---------------- Stats Page ----------------
    stats = pages["stats"]
    stats.grid_columnconfigure(0, weight=1)
    stats.grid_columnconfigure(1, weight=1)

    # Stats UI (2 charts + KPI)
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

    # Export báo cáo
    ui["btn_export_report"] = ctk.CTkButton(filter_frame, text="Xuất báo cáo", fg_color="#0ea5e9")
    ui["btn_export_report"].grid(row=0, column=4, padx=10, pady=10)


    table_frame = ctk.CTkFrame(his, corner_radius=12)
    table_frame.pack(fill="both", expand=True, padx=18, pady=14)

    # Lịch sử chấm công: MaSV, HoTen, Lop, SĐT, Time
    hist_cols = ["msv", "name", "class", "phone_number", "time"]
    hist_tree = ttk.Treeview(table_frame, columns=hist_cols, show="headings", height=18)
    # độ rộng theo cột
    col_width = {
        "msv": 120,
        "name": 180,
        "class": 120,
        "phone_number": 160,
        "time": 240,
    }
    for c in hist_cols:
        hist_tree.heading(c, text=c)
        hist_tree.column(c, width=col_width.get(c, 140))

    hist_tree.pack(fill="both", expand=True)

    ui["tree_history"] = hist_tree


    ui["show_page"] = show_page

    return root, ui

