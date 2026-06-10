import customtkinter as ctk
from tkinter import Frame

def _clear_container(container: ctk.CTkFrame) -> None:
    for child in list(container.winfo_children()):
        try:
            child.destroy()
        except Exception:
            pass

class StatsView:
    def __init__(self, parent: ctk.CTkFrame):
        self.parent = parent
        self.chart_bar_container = None
        self.chart_pie_container = None
        self.kpi_labels: dict[str, ctk.CTkLabel] = {}
        self._build()

    def _build(self) -> None:
        # Layout
        self.parent.grid_rowconfigure(0, weight=0)
        self.parent.grid_rowconfigure(1, weight=0)
        self.parent.grid_rowconfigure(2, weight=1)

        title = ctk.CTkLabel(
            self.parent,
            text="Thống kê chấm công",
            font=ctk.CTkFont(size=22, weight="bold"),
        )
        title.pack(pady=(18, 10))

        charts_wrapper = ctk.CTkFrame(self.parent, corner_radius=12)
        charts_wrapper.pack(fill="both", expand=True, padx=18, pady=10)

        charts_wrapper.grid_columnconfigure(0, weight=1)
        charts_wrapper.grid_columnconfigure(1, weight=1)
        charts_wrapper.grid_rowconfigure(0, weight=1)
        charts_wrapper.grid_rowconfigure(1, weight=0)

        # Chart containers
        self.chart_bar_container = ctk.CTkFrame(charts_wrapper, corner_radius=10, fg_color="#1f2937")
        self.chart_bar_container.grid(row=0, column=0, padx=(14, 7), pady=14, sticky="nsew")
        self.chart_bar_container.grid_rowconfigure(0, weight=1)
        self.chart_bar_container.grid_columnconfigure(0, weight=1)

        bar_title = ctk.CTkLabel(
            self.chart_bar_container,
            text="Chấm công hôm nay",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e5e7eb",
        )
        bar_title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

        bar_body = ctk.CTkFrame(self.chart_bar_container, corner_radius=8, fg_color="#111827")
        bar_body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        bar_body.grid_rowconfigure(0, weight=1)
        bar_body.grid_columnconfigure(0, weight=1)
        # store target body for matplotlib canvas
        self.chart_bar_container._bar_body = bar_body  # type: ignore[attr-defined]

        self.chart_pie_container = ctk.CTkFrame(charts_wrapper, corner_radius=10, fg_color="#1f2937")
        self.chart_pie_container.grid(row=0, column=1, padx=(7, 14), pady=14, sticky="nsew")
        self.chart_pie_container.grid_rowconfigure(0, weight=1)
        self.chart_pie_container.grid_columnconfigure(0, weight=1)

        pie_title = ctk.CTkLabel(
            self.chart_pie_container,
            text="Tỷ lệ chấm công",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#e5e7eb",
        )
        pie_title.grid(row=0, column=0, sticky="w", padx=12, pady=(12, 6))

        pie_body = ctk.CTkFrame(self.chart_pie_container, corner_radius=8, fg_color="#111827")
        pie_body.grid(row=1, column=0, sticky="nsew", padx=12, pady=(0, 12))
        pie_body.grid_rowconfigure(0, weight=1)
        pie_body.grid_columnconfigure(0, weight=1)
        self.chart_pie_container._pie_body = pie_body  # type: ignore[attr-defined]

        # KPI wrapper
        kpi_wrapper = ctk.CTkFrame(self.parent, corner_radius=12, fg_color="#0f172a")
        kpi_wrapper.pack(fill="x", padx=18, pady=(10, 18))
        kpi_wrapper.grid_columnconfigure(0, weight=1)
        kpi_wrapper.grid_columnconfigure(1, weight=1)
        kpi_wrapper.grid_columnconfigure(2, weight=1)

        self.kpi_labels["registered_total"] = self._make_kpi_cell(kpi_wrapper, 0, "Tổng đăng ký")
        self.kpi_labels["today_marked"] = self._make_kpi_cell(kpi_wrapper, 1, "Đã chấm hôm nay")
        self.kpi_labels["today_unmarked"] = self._make_kpi_cell(kpi_wrapper, 2, "Chưa chấm hôm nay")

    def _make_kpi_cell(self, parent: ctk.CTkFrame, col: int, label: str) -> ctk.CTkLabel:
        cell = ctk.CTkFrame(parent, corner_radius=10, fg_color="#111827")
        cell.grid(row=0, column=col, padx=10, pady=12, sticky="nsew")
        cell.grid_columnconfigure(0, weight=1)
        cell.grid_rowconfigure(0, weight=1)
        cell.grid_rowconfigure(1, weight=0)

        lbl_title = ctk.CTkLabel(
            cell,
            text=label,
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#9ca3af",
        )
        lbl_title.grid(row=0, column=0, sticky="w", padx=12, pady=(10, 6))

        value_lbl = ctk.CTkLabel(
            cell,
            text="0",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff",
        )
        value_lbl.grid(row=1, column=0, sticky="w", padx=12, pady=(0, 12))
        return value_lbl

    def set_kpi(self, registered_total: int, today_marked: int, today_unmarked: int) -> None:
        self.kpi_labels["registered_total"].configure(text=str(registered_total))
        self.kpi_labels["today_marked"].configure(text=str(today_marked))
        self.kpi_labels["today_unmarked"].configure(text=str(today_unmarked))

    def clear_charts(self) -> None:
        if self.chart_bar_container is not None:
            _clear_container(self.chart_bar_container._bar_body)  # type: ignore[attr-defined]
        if self.chart_pie_container is not None:
            _clear_container(self.chart_pie_container._pie_body)  # type: ignore[attr-defined]

    def get_bar_body(self) -> ctk.CTkFrame:
        return self.chart_bar_container._bar_body  # type: ignore[attr-defined]

    def get_pie_body(self) -> ctk.CTkFrame:
        return self.chart_pie_container._pie_body  # type: ignore[attr-defined]

