"""Dashboard view for Controlito."""
import customtkinter as ctk
from datetime import datetime
import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from utils.helpers import format_currency, mes_nombre, mes_numero, MESES
from ui.theme import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    BG_CARD, BG_MAIN, TEXT_MAIN, TEXT_MUTED, FONT_TITLE, FONT_STAT_NUM,
    FONT_HEADER, FONT_BODY, FONT_SMALL
)


class DashboardView(ctk.CTkFrame):
    def __init__(self, parent, db, on_navigate=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_navigate = on_navigate

        # Default to current year and month or latest available
        available_years = self.db.get_available_years()
        now = datetime.now()
        self.selected_year = now.year if now.year in available_years else (available_years[-1] if available_years else 2026)
        self.selected_month = now.month

        self.canvas_donut = None
        self.canvas_bars = None

        self.build_ui()
        self.load_data()

    def build_ui(self):
        # Header with filters
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        title_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        title_box.pack(side="left")

        title_label = ctk.CTkLabel(
            title_box,
            text="📊 Panel de Control Financiero",
            font=FONT_TITLE,
            text_color=TEXT_MAIN
        )
        title_label.pack(anchor="w")

        tx_count = self.db.get_transaction_count()
        lbl_subtitle = ctk.CTkLabel(
            title_box,
            text=f"✨ {tx_count:,} movimientos registrados • Finanzas personales al día",
            font=FONT_SMALL,
            text_color=COLOR_PRIMARY
        )
        lbl_subtitle.pack(anchor="w")

        filter_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        filter_frame.pack(side="right")

        # Year dropdown
        years = [str(y) for y in self.db.get_available_years()] or [str(datetime.now().year)]
        self.year_cb = ctk.CTkComboBox(
            filter_frame,
            values=years,
            width=100,
            command=self.on_filter_change
        )
        self.year_cb.set(str(self.selected_year))
        self.year_cb.pack(side="right", padx=5)

        # Month dropdown
        months = [mes_nombre(i) for i in range(1, 13)]
        self.month_cb = ctk.CTkComboBox(
            filter_frame,
            values=months,
            width=130,
            command=self.on_filter_change
        )
        self.month_cb.set(mes_nombre(self.selected_month))
        self.month_cb.pack(side="right", padx=5)

        # KPI Cards Frame
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=20, pady=10)
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="kpi")

        self.card_ingreso = self._create_kpi_card(kpi_frame, 0, "💰 Ingresos del Mes", "$ 0", COLOR_SUCCESS)
        self.card_gasto = self._create_kpi_card(kpi_frame, 1, "💸 Gastos del Mes", "$ 0", COLOR_DANGER)
        self.card_balance = self._create_kpi_card(kpi_frame, 2, "⚖️ Balance Neto", "$ 0", COLOR_PRIMARY)
        self.card_ahorro = self._create_kpi_card(kpi_frame, 3, "💵 Ahorro Total USD", "USD 0", COLOR_WARNING)

        # Split frame for Charts
        charts_frame = ctk.CTkFrame(self, fg_color="transparent")
        charts_frame.pack(fill="both", expand=True, padx=20, pady=10)
        charts_frame.grid_columnconfigure((0, 1), weight=1, uniform="chart")
        charts_frame.grid_rowconfigure(0, weight=1)

        # Donut Chart Card
        self.chart_card_left = ctk.CTkFrame(charts_frame, fg_color=BG_CARD, corner_radius=12)
        self.chart_card_left.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=5)
        
        lbl_donut = ctk.CTkLabel(self.chart_card_left, text="Distribución de Gastos por Categoría", font=FONT_HEADER, text_color=TEXT_MAIN)
        lbl_donut.pack(anchor="w", padx=15, pady=(10, 5))

        self.donut_container = ctk.CTkFrame(self.chart_card_left, fg_color="transparent")
        self.donut_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Bar Chart Card
        self.chart_card_right = ctk.CTkFrame(charts_frame, fg_color=BG_CARD, corner_radius=12)
        self.chart_card_right.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=5)

        lbl_bars = ctk.CTkLabel(self.chart_card_right, text="Evolución Mensual (Ingresos vs Gastos)", font=FONT_HEADER, text_color=TEXT_MAIN)
        lbl_bars.pack(anchor="w", padx=15, pady=(10, 5))

        self.bars_container = ctk.CTkFrame(self.chart_card_right, fg_color="transparent")
        self.bars_container.pack(fill="both", expand=True, padx=10, pady=5)

        # Quick Insights Bar at bottom
        self.insights_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10, height=45)
        self.insights_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        self.lbl_insight = ctk.CTkLabel(
            self.insights_frame,
            text="💡 Tip Financiero: Monitorea tus gastos fijos de servicios para no superar el 30% de tus ingresos.",
            font=FONT_BODY,
            text_color=TEXT_MAIN
        )
        self.lbl_insight.pack(side="left", padx=15, pady=8)

    def _create_kpi_card(self, parent, col, title, initial_value, text_color):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12)
        card.grid(row=0, column=col, sticky="nsew", padx=6, pady=5)

        lbl_title = ctk.CTkLabel(card, text=title, font=FONT_BODY, text_color=TEXT_MUTED)
        lbl_title.pack(anchor="w", padx=15, pady=(12, 4))

        lbl_val = ctk.CTkLabel(card, text=initial_value, font=FONT_STAT_NUM, text_color=text_color)
        lbl_val.pack(anchor="w", padx=15, pady=(0, 12))
        return lbl_val

    def on_filter_change(self, _=None):
        try:
            self.selected_year = int(self.year_cb.get())
            self.selected_month = mes_numero(self.month_cb.get()) or 1
            self.load_data()
        except ValueError:
            pass

    def load_data(self):
        # 1. Update KPIs
        summary = self.db.get_monthly_summary(self.selected_year, self.selected_month)
        ingreso = summary["ingreso"]
        gasto = summary["gasto"]
        balance = summary["balance"]

        self.card_ingreso.configure(text=format_currency(ingreso))
        self.card_gasto.configure(text=format_currency(gasto))
        
        bal_text = format_currency(balance)
        bal_color = COLOR_SUCCESS if balance >= 0 else COLOR_DANGER
        self.card_balance.configure(text=bal_text, text_color=bal_color)

        # Savings USD total
        savings = self.db.get_savings()
        usd_total = 0.0
        for s in savings:
            if s["moneda"] == "USD" and "gasto" not in s["concepto"].lower():
                usd_total = s["monto"]
                break
        if usd_total == 0:
            usd_total = sum(s["monto"] for s in savings if s["moneda"] == "USD")
        self.card_ahorro.configure(text=f"USD {usd_total:,.2f}")

        # Update Insights
        if gasto > ingreso and ingreso > 0:
            self.lbl_insight.configure(
                text=f"⚠️ Alerta: Los gastos de {mes_nombre(self.selected_month)} superan los ingresos en {format_currency(gasto - ingreso)}."
            )
        elif ingreso > 0:
            tasa_ahorro = ((ingreso - gasto) / ingreso) * 100
            self.lbl_insight.configure(
                text=f"✅ Excelente: Este mes mantuviste una tasa de superávit del {tasa_ahorro:.1f}% ({format_currency(balance)} sobrantes)."
            )
        else:
            self.lbl_insight.configure(
                text=f"ℹ️ Mes {mes_nombre(self.selected_month)} {self.selected_year}: Registra ingresos o gastos para ver métricas."
            )

        # 2. Render Donut Chart
        self._render_donut(self.selected_year, self.selected_month)

        # 3. Render Bar Chart
        self._render_bars(self.selected_year)

    def _render_donut(self, year, month):
        from ui.theme import ThemeManager
        t = ThemeManager.get_current_theme()

        # Close previous figure to prevent memory leak
        if hasattr(self, "canvas_donut") and self.canvas_donut is not None:
            try:
                self.canvas_donut.get_tk_widget().destroy()
                self.canvas_donut.figure.clf()
            except Exception:
                pass
            self.canvas_donut = None

        for widget in self.donut_container.winfo_children():
            widget.destroy()

        cat_summary = self.db.get_category_summary(year, month)
        # Filter top 5 categories by gasto > 0
        gastos = [c for c in cat_summary if c["gasto"] > 0]
        
        fig = Figure(figsize=(4.2, 3.2), dpi=90, facecolor=t["chart_bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(t["chart_bg"])

        if not gastos:
            ax.text(0.5, 0.5, "Sin gastos registrados\nen este mes", color=t["text_muted"],
                    ha="center", va="center", fontsize=11)
            ax.axis("off")
        else:
            top_cats = gastos[:5]
            otros_monto = sum(c["gasto"] for c in gastos[5:])
            labels = [c["categoria"] for c in top_cats]
            values = [c["gasto"] for c in top_cats]
            if otros_monto > 0:
                labels.append("Otros")
                values.append(otros_monto)

            colors = t["chart_palette"]
            wedges, texts, autotexts = ax.pie(
                values,
                labels=labels,
                autopct="%1.0f%%",
                startangle=140,
                colors=colors[:len(values)],
                textprops={"color": t["text_main"], "fontsize": 8},
                wedgeprops={"width": 0.5, "edgecolor": t["bg_sidebar"]}
            )
            for autotext in autotexts:
                autotext.set_color("#ffffff")
                autotext.set_fontsize(8)

        fig.tight_layout()
        self.canvas_donut = FigureCanvasTkAgg(fig, master=self.donut_container)
        self.canvas_donut.draw()
        self.canvas_donut.get_tk_widget().pack(fill="both", expand=True)

    def _render_bars(self, year):
        from ui.theme import ThemeManager
        t = ThemeManager.get_current_theme()

        # Close previous figure to prevent memory leak
        if hasattr(self, "canvas_bars") and self.canvas_bars is not None:
            try:
                self.canvas_bars.get_tk_widget().destroy()
                self.canvas_bars.figure.clf()
            except Exception:
                pass
            self.canvas_bars = None

        for widget in self.bars_container.winfo_children():
            widget.destroy()

        yearly = self.db.get_yearly_summary(year)
        
        fig = Figure(figsize=(4.8, 3.2), dpi=90, facecolor=t["chart_bg"])
        ax = fig.add_subplot(111)
        ax.set_facecolor(t["bg_main"])

        if not yearly:
            ax.text(0.5, 0.5, f"Sin datos para el año {year}", color=t["text_muted"],
                    ha="center", va="center", fontsize=11)
            ax.axis("off")
        else:
            meses_indices = [y["mes"] for y in yearly]
            meses_nombres = [mes_nombre(m)[:3] for m in meses_indices]
            ingresos = [y["ingreso"] for y in yearly]
            gastos = [y["gasto"] for y in yearly]

            import numpy as np
            x = np.arange(len(meses_indices))
            width = 0.35

            ax.bar(x - width/2, [i / 1000 for i in ingresos], width, label="Ingreso (k$)", color=t["success"])
            ax.bar(x + width/2, [g / 1000 for g in gastos], width, label="Gasto (k$)", color=t["danger"])

            ax.set_xticks(x)
            ax.set_xticklabels(meses_nombres, color=t["text_muted"], fontsize=8)
            ax.tick_params(colors=t["text_muted"], labelsize=8)
            ax.legend(facecolor=t["chart_bg"], edgecolor=t["border"], labelcolor=t["text_main"], fontsize=8)
            ax.spines['bottom'].set_color(t["border"])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(t["border"])
            ax.grid(axis='y', linestyle='--', alpha=0.3, color=t["text_muted"])

        fig.tight_layout()
        self.canvas_bars = FigureCanvasTkAgg(fig, master=self.bars_container)
        self.canvas_bars.draw()
        self.canvas_bars.get_tk_widget().pack(fill="both", expand=True)
