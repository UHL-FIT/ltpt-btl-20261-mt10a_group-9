import tkinter as tk
from tkinter import filedialog, messagebox
from utils.logger import setup_logger
from models import face_attendance
import views.ctk_view as ctk_view
import sys
logger = setup_logger("ctk_controller")

def _set_label(ui, key: str, text: str):
    lbl = ui.get(key)
    if lbl is not None:
        try:
            lbl.configure(text=text)
        except Exception:
            pass

def _clear_tree(tree):
    for item in tree.get_children():
        tree.delete(item)

def _load_recent_logs(ui, limit: int = 10):
    # Không còn tree_recent_logs trong Attendance UI mới
    if "tree_recent_logs" not in ui:
        return

    tree = ui["tree_recent_logs"]

    _clear_tree(tree)
    df = face_attendance.get_history()
    if df is None or df.empty:
        return
    df = df.head(limit)
    for _, row in df.iterrows():
        tree.insert("", tk.END, values=[row.get("log_id", ""), row.get("msv", ""), row.get("time", ""), row.get("status", "")])

def _load_history(ui, msv_filter: str = ""):
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
                row.get("msv", ""),
                row.get("time", ""),
                row.get("status", ""),
                row.get("note", ""),
            ],
        )

def _refresh_stats(ui):
    """Refresh stats page charts + KPI."""
    try:
        from models.attendance_stats import get_today_attendance_stats_distinct
        from views.stats_charts import make_bar_pie_figures

        stats_model = get_today_attendance_stats_distinct()
        payload = stats_model.to_dict()

        # Update KPI labels
        sv = ui.get("stats_view")
        if sv is not None:
            sv.set_kpi(
                registered_total=int(payload.get("registered_total", 0) or 0),
                today_marked=int(payload.get("today_marked", 0) or 0),
                today_unmarked=int(payload.get("today_unmarked", 0) or 0),
            )

        # Build charts (matplotlib Figures)
        fig_bar, fig_pie = make_bar_pie_figures(payload)

        # Embed charts into CTk via FigureCanvasTkAgg
        from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

        if sv is None:
            return

        sv.clear_charts()

        bar_body = sv.get_bar_body()
        pie_body = sv.get_pie_body()

        canvas_bar = FigureCanvasTkAgg(fig_bar, master=bar_body)
        canvas_bar.draw()
        canvas_bar.get_tk_widget().pack(fill="both", expand=True)

        canvas_pie = FigureCanvasTkAgg(fig_pie, master=pie_body)
        canvas_pie.draw()
        canvas_pie.get_tk_widget().pack(fill="both", expand=True)

        # Keep references to avoid GC
        ui["_canvas_bar"] = canvas_bar
        ui["_canvas_pie"] = canvas_pie

    except Exception as e:
        # Keep UI responsive even if chart fails
        try:
            messagebox.showerror("Lỗi thống kê", str(e))
        except Exception:
            pass

def chay_ung_dung():
    root, ui = ctk_view.create_main_window()

    # ---------- Xử lý sự kiện cho các Button ----------
    def on_register_student():
        msv = ui["ent_reg_msv"].get().strip().upper()
        name = ui["ent_reg_name"].get().strip()
        lop = ui["ent_reg_lop"].get().strip()
        sdt = ui["ent_reg_sdt"].get().strip()
        face_path = ""

        ok, msg = face_attendance.add_student({"msv": msv, "ho_ten": name, "lop": lop, "sdt": sdt, "face_path": face_path})

        if not ok:
            messagebox.showerror("Lỗi", msg)
            _set_label(ui, "lbl_reg_status", f"Trạng thái: lỗi - {msg}")
            return

        _set_label(ui, "lbl_reg_status", f"Trạng thái: OK - {msg}")
        messagebox.showinfo("Thành công", msg)

    def on_register_face():
        """Mở camera standalone để chụp 1 ảnh đăng ký theo MSV.

        Luồng:
        - Lấy MSV từ ent_reg_msv
        - Mở test_cam.py bằng subprocess, truyền --msv
        - Người dùng nhấn 's' trong cửa sổ cam để lưu ảnh
        - Sau khi subprocess kết thúc: update face_path trong CSV.
        """
        import subprocess
        import os
        import sys

        msv = ui["ent_reg_msv"].get().strip().upper()
        if not msv:
            messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập MSV trước khi đăng ký khuôn mặt")
            return

        # Kiểm tra MSV đã tồn tại trong CSDL
        df_students = face_attendance.load_students()
        if df_students is None or df_students.empty or not (df_students["msv"] == msv).any():
            messagebox.showwarning(
                "Chưa có sinh viên",
                "Vui lòng bấm 'Lưu sinh viên' trước khi 'Đăng ký khuôn mặt'.",
            )
            return

        dataset_path = os.path.join("dataset", f"{msv}.jpg")

        # script_path: test_cam.py ở cùng root dự án
        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "test_cam.py"))
        if not os.path.exists(script_path):
            messagebox.showerror("Lỗi", f"Không tìm thấy file camera: {script_path}")
            return

        # Chạy camera standalone và chờ người dùng bấm 's' để lưu ảnh rồi mới tiếp tục
        try:
            proc = subprocess.run(
                [sys.executable, script_path, "--msv", msv],
                capture_output=True,
                text=True,
            )
        except Exception as e:
            messagebox.showerror("Lỗi", f"Không thể chạy camera: {e}")
            return

        if not os.path.exists(dataset_path):
            err_msg = (proc.stderr or proc.stdout or "").strip() or "Camera chạy nhưng không tạo được ảnh"
            messagebox.showerror("Không tạo được ảnh", f"{err_msg}\nExpected: {dataset_path}")
            return

        ok, msg = face_attendance.register_face(msv, face_path=dataset_path)
        if not ok:
            messagebox.showerror("Lỗi", msg)
            return

        _set_label(ui, "lbl_reg_status", f"Trạng thái: OK - đã đăng ký khuôn mặt")
        messagebox.showinfo("Thành công", msg)

    def on_refresh_stats():
        _refresh_stats(ui)

    def on_hist_refresh():
        ui["ent_hist_msv"].delete(0, tk.END)
        _load_history(ui, msv_filter="")

    def on_hist_filter():
        msv = ui["ent_hist_msv"].get().strip()
        _load_history(ui, msv_filter=msv)

    def on_start_attendance():
        import subprocess
        import os
        import json

        # Reset khung bên phải ngay khi bắt đầu lượt chấm công
        _set_label(ui, "lbl_msv", "---")
        _set_label(ui, "lbl_hoten", "---")
        _set_label(ui, "lbl_lop", "---")
        _set_label(ui, "lbl_sdt", "---")
        _set_label(ui, "lbl_thoigian", "---")

        root_dir = os.path.dirname(os.path.abspath(__file__))
        repo_root = os.path.abspath(os.path.join(root_dir, ".."))

        script_path = os.path.join(repo_root, "attendance_cam.py")
        if not os.path.exists(script_path):
            messagebox.showerror("Lỗi", f"Không tìm thấy file: {script_path}")
            return

        last_json_path = os.path.join(repo_root, "data", "last_attendance.json")
        try:
            if os.path.exists(last_json_path):
                os.remove(last_json_path)
        except Exception:
            pass

        # Spawn camera subprocess dùng đúng interpreter (tránh lệch venv)
        proc = subprocess.Popen([sys.executable, script_path])

        polling_interval_ms = 250

        def poll_once():
            # If user closes process/window manually
            try:
                if proc.poll() is not None:
                    # Camera process ended; still allow UI to reset if needed
                    return
            except Exception:
                return

            payload = None
            if os.path.exists(last_json_path):
                try:
                    with open(last_json_path, "r", encoding="utf-8") as f:
                        payload = json.load(f)
                except Exception:
                    payload = None

            if payload and str(payload.get("status", "")).strip():
                st = str(payload.get("status", "")).strip().upper()

                msv = str(payload.get("msv", "")).strip().upper()
                ho_ten = str(payload.get("ho_ten", "")).strip()
                lop = str(payload.get("lop", "")).strip()
                sdt = str(payload.get("sdt", "")).strip()
                t_str = str(payload.get("time", "")).strip()

                if msv:
                    _set_label(ui, "lbl_msv", msv)
                if ho_ten:
                    _set_label(ui, "lbl_hoten", ho_ten)
                if lop:
                    _set_label(ui, "lbl_lop", lop)
                if sdt:
                    _set_label(ui, "lbl_sdt", sdt)
                if t_str:
                    _set_label(ui, "lbl_thoigian", t_str)

                if st == "SUCCESS":
                    messagebox.showinfo("Thành công", "Chấm công thành công")
                elif st == "ALREADY_MARKED_TODAY":
                    messagebox.showinfo("Thông báo", "Đã chấm công hôm nay")
                else:
                    # Includes ERROR or UNKNOWN
                    err = payload.get("error") or payload.get("message") or "Nhận diện thất bại"
                    messagebox.showerror("Lỗi", str(err))

                # Stop camera only after user acknowledges popup
                try:
                    proc.terminate()
                except Exception:
                    pass

                try:
                    os.remove(last_json_path)
                except Exception:
                    pass
                return

            # continue polling
            try:
                root.after(polling_interval_ms, poll_once)
            except Exception:
                pass

        poll_once()

    
    ui["btn_start_attendance"].configure(command=on_start_attendance)

    ui["btn_register_student"].configure(command=on_register_student)

    ui["btn_register_face"].configure(command=on_register_face)

    ui["btn_refresh_stats"].configure(command=on_refresh_stats)

    ui["btn_hist_refresh"].configure(command=on_hist_refresh)

    ui["btn_hist_filter"].configure(command=on_hist_filter)

    # ---------- Initial load ----------
    _load_recent_logs(ui)
    _load_history(ui)
    _refresh_stats(ui)

    root.mainloop()

