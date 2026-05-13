"""Controller cho UI customtkinter."""
from __future__ import annotations
import tkinter as tk
from tkinter import filedialog, messagebox

from utils.logger import setup_logger
from models import face_attendance
import views.ctk_view as ctk_view

logger = setup_logger("ctk_controller")

def _set_label(ui, key: str, text: str) -> None:
    lbl = ui.get(key)
    if lbl is not None:
        try:
            lbl.configure(text=text)
        except Exception:
            pass


def _clear_tree(tree) -> None:
    for item in tree.get_children():
        tree.delete(item)


def _load_students_to_tree(ui) -> None:
    tree = ui["tree_students"]
    _clear_tree(tree)
    df = face_attendance.load_students()
    for _, row in df.iterrows():
        tree.insert("", tk.END, values=[row.get("msv", ""), row.get("ho_ten", ""), row.get("lop", ""), row.get("sdt", "")])


def _load_recent_logs(ui, limit: int = 10) -> None:
    tree = ui["tree_recent_logs"]
    _clear_tree(tree)
    df = face_attendance.get_history()
    if df is None or df.empty:
        return
    df = df.head(limit)
    for _, row in df.iterrows():
        tree.insert("", tk.END, values=[row.get("log_id", ""), row.get("msv", ""), row.get("time", ""), row.get("status", "")])


def _load_history(ui, msv_filter: str = "") -> None:
    tree = ui["tree_history"]
    _clear_tree(tree)
    df = face_attendance.get_history(msv=msv_filter)
    if df is None or df.empty:
        return
    for _, row in df.iterrows():
        tree.insert(
            "",
            tk.END,
            values=[
                row.get("log_id", ""),
                row.get("msv", ""),
                row.get("time", ""),
                row.get("status", ""),
                row.get("note", ""),
            ],
        )


def _refresh_stats(ui) -> None:
    stats = face_attendance.get_stats()
    ui["lbl_stat_total"].configure(text=f"Tổng log: {stats.get('total_logs', 0)}")
    ui["lbl_stat_ok"].configure(text=f"OK: {stats.get('ok', 0)}")
    ui["lbl_stat_today"].configure(text=f"Hôm nay: {stats.get('today_logs', 0)}")
    ui["lbl_stat_today_ok"].configure(text=f"Hôm nay OK: {stats.get('today_ok', 0)}")


def chay_ung_dung() -> None:
    root, ui = ctk_view.create_main_window()

    # ---------- Button bindings ----------
    def on_start_recog():
        _set_label(ui, "lbl_att_status", "Trạng thái: đang nhận diện (demo) ...")
        messagebox.showinfo("Demo", "Nút nhận diện đang là placeholder. Bạn có thể nhập MSV và bấm 'Chấm công'.")
        _set_label(ui, "lbl_att_status", "Trạng thái: sẵn sàng")

    def on_mark_att():
        msv = ui["ent_att_msv"].get().strip().upper()
        if not msv:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập MSV")
            return
        ok, msg = face_attendance.do_attendance(msv, status="OK")
        if not ok:
            messagebox.showerror("Lỗi", msg)
            _set_label(ui, "lbl_att_status", f"Trạng thái: lỗi - {msg}")
            return
        _set_label(ui, "lbl_att_status", f"Trạng thái: OK - {msg}")
        _load_recent_logs(ui)
        _load_history(ui, msv_filter="")
        _refresh_stats(ui)

    def on_upload_face():
        # Chọn ảnh làm placeholder
        path = filedialog.askopenfilename(
            title="Chọn ảnh",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.webp"), ("All files", "*.*")],
        )
        if not path:
            return
        ui["ent_face_path"].delete(0, tk.END)
        ui["ent_face_path"].insert(0, path)
        _set_label(ui, "lbl_reg_status", "Đã chọn ảnh (demo)")

    def on_register_student():
        msv = ui["ent_reg_msv"].get().strip().upper()
        name = ui["ent_reg_name"].get().strip()
        lop = ui["ent_reg_lop"].get().strip()
        sdt = ui["ent_reg_sdt"].get().strip()
        face_path = ui["ent_face_path"].get().strip()

        ok, msg = face_attendance.add_student({"msv": msv, "ho_ten": name, "lop": lop, "sdt": sdt, "face_path": face_path})
        if not ok:
            messagebox.showerror("Lỗi", msg)
            _set_label(ui, "lbl_reg_status", f"Trạng thái: lỗi - {msg}")
            return

        _set_label(ui, "lbl_reg_status", f"Trạng thái: OK - {msg}")
        _load_students_to_tree(ui)
        messagebox.showinfo("Thành công", msg)

    def on_register_face():
        msv = ui["ent_reg_msv"].get().strip().upper()
        face_path = ui["ent_face_path"].get().strip()
        if not msv:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập MSV")
            return
        if not face_path:
            # vẫn cho phép register face nếu chưa chọn ảnh
            face_path = ""

        ok, msg = face_attendance.register_face(msv, face_path=face_path)
        if not ok:
            messagebox.showerror("Lỗi", msg)
            _set_label(ui, "lbl_reg_status", f"Trạng thái: lỗi - {msg}")
            return
        _set_label(ui, "lbl_reg_status", f"Trạng thái: OK - {msg}")
        messagebox.showinfo("Register", msg)

    def on_refresh_stats():
        _refresh_stats(ui)

    def on_hist_refresh():
        ui["ent_hist_msv"].delete(0, tk.END)
        _load_history(ui, msv_filter="")

    def on_hist_filter():
        msv = ui["ent_hist_msv"].get().strip()
        _load_history(ui, msv_filter=msv)

    ui["btn_start_recog"].configure(command=on_start_recog)
    ui["btn_mark_attendance"].configure(command=on_mark_att)

    ui["btn_upload_face"].configure(command=on_upload_face)
    ui["btn_register_student"].configure(command=on_register_student)
    ui["btn_register_face"].configure(command=on_register_face)

    ui["btn_refresh_stats"].configure(command=on_refresh_stats)
    ui["btn_hist_refresh"].configure(command=on_hist_refresh)
    ui["btn_hist_filter"].configure(command=on_hist_filter)

    # ---------- Initial load ----------
    _load_students_to_tree(ui)
    _load_recent_logs(ui)
    _load_history(ui)
    _refresh_stats(ui)

    root.mainloop()

