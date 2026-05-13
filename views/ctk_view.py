from __future__ import annotations
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

    # ---------------- Attendance Page ----------------
    att = pages["attendance"]
    att.grid_columnconfigure(0, weight=1)
    att.grid_columnconfigure(1, weight=1)

    card_left = ctk.CTkFrame(att, corner_radius=12)
    card_left.grid(row=0, column=0, padx=14, pady=14, sticky="nsew")
    card_right = ctk.CTkFrame(att, corner_radius=12)
    card_right.grid(row=0, column=1, padx=14, pady=14, sticky="nsew")

    ctk.CTkLabel(card_left, text="Chấm công", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(18, 8))

    ui: Dict[str, object] = {"root": root}

    ui["btn_nav_att"] = ctk.CTkButton(sidebar, text="Chấm công", command=lambda: show_page("attendance"))
    ui["btn_nav_reg"] = ctk.CTkButton(sidebar, text="Đăng ký", command=lambda: show_page("register"))
    ui["btn_nav_stats"] = ctk.CTkButton(sidebar, text="Thống kê", command=lambda: show_page("stats"))
    ui["btn_nav_history"] = ctk.CTkButton(sidebar, text="Lịch sử", command=lambda: show_page("history"))

    ui["btn_nav_att"].pack(pady=8, padx=14)
    ui["btn_nav_reg"].pack(pady=8, padx=14)
    ui["btn_nav_stats"].pack(pady=8, padx=14)
    ui["btn_nav_history"].pack(pady=8, padx=14)

    # Attendance controls
    form = ctk.CTkFrame(card_left, corner_radius=12)
    form.pack(fill="both", expand=True, padx=14, pady=14)

    ctk.CTkLabel(form, text="MSV:").grid(row=0, column=0, sticky="w", padx=10, pady=8)
    ui["ent_att_msv"] = ctk.CTkEntry(form, width=260)
    ui["ent_att_msv"].grid(row=0, column=1, padx=10, pady=8)

    ui["btn_start_recog"] = ctk.CTkButton(form, text="Bắt đầu nhận diện (demo)")
    ui["btn_start_recog"].grid(row=1, column=0, columnspan=2, padx=10, pady=(10, 6), sticky="ew")

    ui["btn_mark_attendance"] = ctk.CTkButton(form, text="Chấm công", fg_color="#1CB57A")
    ui["btn_mark_attendance"].grid(row=2, column=0, columnspan=2, padx=10, pady=8, sticky="ew")

    ui["lbl_att_status"] = ctk.CTkLabel(form, text="Trạng thái: sẵn sàng", anchor="w")
    ui["lbl_att_status"].grid(row=3, column=0, columnspan=2, padx=10, pady=(12, 0), sticky="w")

    # Right side: recent logs
    ctk.CTkLabel(card_right, text="Gần đây", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(18, 8), padx=14, anchor="w")

    tree_frame = ctk.CTkFrame(card_right, corner_radius=10)
    tree_frame.pack(fill="both", expand=True, padx=14, pady=14)

    cols = ["log_id", "msv", "time", "status"]
    tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=14)
    for c in cols:
        tree.heading(c, text=c)
        tree.column(c, width=120 if c != "time" else 220)
    tree.pack(fill="both", expand=True)

    ui["tree_recent_logs"] = tree
    ui["cols_recent_logs"] = cols


    # ---------------- Register Page ----------------
    reg = pages["register"]
    reg.grid_columnconfigure(0, weight=1)
    reg.grid_columnconfigure(1, weight=1)

    card_reg_left = ctk.CTkFrame(reg, corner_radius=12)
    card_reg_left.grid(row=0, column=0, padx=14, pady=14, sticky="nsew")
    card_reg_right = ctk.CTkFrame(reg, corner_radius=12)
    card_reg_right.grid(row=0, column=1, padx=14, pady=14, sticky="nsew")

    ctk.CTkLabel(card_reg_left, text="Đăng ký khuôn mặt (demo)", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=(18, 8))

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

    ui["btn_upload_face"] = ctk.CTkButton(reg_form, text="Chọn file ảnh (demo)")
    ui["btn_upload_face"].grid(row=4, column=0, columnspan=2, padx=10, pady=(12, 6), sticky="ew")

    ui["ent_face_path"] = ctk.CTkEntry(reg_form, placeholder_text="Đường dẫn ảnh sẽ hiện ở đây", width=340)
    ui["ent_face_path"].grid(row=5, column=0, columnspan=2, padx=10, pady=6, sticky="ew")

    ui["btn_register_student"] = ctk.CTkButton(reg_form, text="Lưu sinh viên", fg_color="#1E90FF")

    ui["btn_register_student"].grid(row=6, column=0, columnspan=2, padx=10, pady=10, sticky="ew")

    ui["btn_register_face"] = ctk.CTkButton(reg_form, text="Register face (demo)", fg_color="#A020F0")

    ui["btn_register_face"].grid(row=7, column=0, columnspan=2, padx=10, pady=6, sticky="ew")

    ui["lbl_reg_status"] = ctk.CTkLabel(reg_form, text="Trạng thái: sẵn sàng", anchor="w")
    ui["lbl_reg_status"].grid(row=8, column=0, columnspan=2, padx=10, pady=(12, 0), sticky="w")

    # Register list
    ctk.CTkLabel(card_reg_right, text="Danh sách sinh viên", font=ctk.CTkFont(size=14, weight="bold")).pack(pady=(18, 8), padx=14, anchor="w")
    reg_tree_frame = ctk.CTkFrame(card_reg_right, corner_radius=10)
    reg_tree_frame.pack(fill="both", expand=True, padx=14, pady=14)

    reg_cols = ["msv", "ho_ten", "lop", "sdt"]
    reg_tree = ttk.Treeview(reg_tree_frame, columns=reg_cols, show="headings", height=16)
    for c in reg_cols:
        reg_tree.heading(c, text=c)
        reg_tree.column(c, width=140 if c != "ho_ten" else 220)
    reg_tree.pack(fill="both", expand=True)

    ui["tree_students"] = reg_tree

    # ---------------- Stats Page ----------------
    stats = pages["stats"]
    stats.grid_columnconfigure(0, weight=1)
    stats.grid_columnconfigure(1, weight=1)

    ctk.CTkLabel(stats, text="Thống kê", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=18)

    top_cards = ctk.CTkFrame(stats, corner_radius=12)
    top_cards.pack(fill="x", padx=18, pady=10)

    ui["lbl_stat_total"] = ctk.CTkLabel(top_cards, text="Tổng log: 0", font=ctk.CTkFont(size=14, weight="bold"))
    ui["lbl_stat_total"].grid(row=0, column=0, padx=14, pady=14, sticky="w")

    ui["lbl_stat_ok"] = ctk.CTkLabel(top_cards, text="OK: 0", font=ctk.CTkFont(size=14, weight="bold"))
    ui["lbl_stat_ok"].grid(row=0, column=1, padx=14, pady=14, sticky="w")

    ui["lbl_stat_today"] = ctk.CTkLabel(top_cards, text="Hôm nay: 0", font=ctk.CTkFont(size=14, weight="bold"))
    ui["lbl_stat_today"].grid(row=1, column=0, padx=14, pady=14, sticky="w")

    ui["lbl_stat_today_ok"] = ctk.CTkLabel(top_cards, text="Hôm nay OK: 0", font=ctk.CTkFont(size=14, weight="bold"))
    ui["lbl_stat_today_ok"].grid(row=1, column=1, padx=14, pady=14, sticky="w")

    ui["btn_refresh_stats"] = ctk.CTkButton(stats, text="Làm mới", fg_color="#28A745")

    ui["btn_refresh_stats"].pack(pady=10)

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

    table_frame = ctk.CTkFrame(his, corner_radius=12)
    table_frame.pack(fill="both", expand=True, padx=18, pady=14)

    hist_cols = ["log_id", "msv", "time", "status", "note"]
    hist_tree = ttk.Treeview(table_frame, columns=hist_cols, show="headings", height=18)
    for c in hist_cols:
        hist_tree.heading(c, text=c)
        hist_tree.column(c, width=140 if c != "time" and c != "note" else 240)
    hist_tree.pack(fill="both", expand=True)

    ui["tree_history"] = hist_tree

    ui["show_page"] = show_page

    return root, ui

