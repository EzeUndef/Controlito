"""Budget management view (Presupuesto mensual adaptado)."""
import customtkinter as ctk
from tkinter import ttk, messagebox
from utils.helpers import format_currency, mes_nombre, mes_numero
from ui.theme import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    BG_CARD, TEXT_MAIN, TEXT_MUTED, FONT_TITLE, FONT_HEADER,
    FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)

DEFAULT_BUDGET_CATEGORIES = [
    ("Casa", "Alquiler"),
    ("Casa", "Luz"),
    ("Casa", "Gas"),
    ("Casa", "Agua impuesto"),
    ("Casa", "Cable-Internet"),
    ("Alimento", "Supermercado"),
    ("Alimento", "Delivery"),
    ("Alimento", "Panaderia/cafeteria"),
    ("Alimento", "Carniceria"),
    ("Transporte", "Transporte público"),
    ("Transporte", "Uber/Didi/Cabify"),
    ("Entretenimiento", "Salida"),
    ("Entretenimiento", "Compras"),
    ("Entretenimiento", "Joda"),
    ("Tarjetas", "Tarjeta Visa"),
    ("Tarjetas", "Tarjeta Amex"),
    ("Tarjetas", "TC"),
    ("Impuestos", "ARCA / AGIP"),
    ("Cuidado Personal", "Farmacia"),
    ("Cuidado Personal", "Peluqueria"),
]


class BudgetView(ctk.CTkFrame):
    def __init__(self, parent, db, on_data_changed=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_data_changed = on_data_changed

        self.selected_year = 2026
        self.selected_month = 11

        self.build_ui()
        self.load_budget()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(header, text="📋 Presupuesto Mensual & Metas", font=FONT_TITLE, text_color=TEXT_MAIN)
        title.pack(side="left")

        # Selectors
        sel_frame = ctk.CTkFrame(header, fg_color="transparent")
        sel_frame.pack(side="right")

        years = [str(y) for y in (self.db.get_available_years() or [2025, 2026, 2027])]
        self.cb_year = ctk.CTkComboBox(sel_frame, values=years, width=95, command=self.on_period_change)
        self.cb_year.set(str(self.selected_year))
        self.cb_year.pack(side="right", padx=5)

        months = [mes_nombre(i) for i in range(1, 13)]
        self.cb_month = ctk.CTkComboBox(sel_frame, values=months, width=120, command=self.on_period_change)
        self.cb_month.set(mes_nombre(self.selected_month))
        self.cb_month.pack(side="right", padx=5)

        # KPI Summary
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=20, pady=5)
        kpi_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="bud_kpi")

        self.card_presupuestado = self._create_card(kpi_frame, 0, "🎯 Total Presupuestado", "$ 0", COLOR_PRIMARY)
        self.card_real = self._create_card(kpi_frame, 1, "💸 Gasto Real del Mes", "$ 0", COLOR_DANGER)
        self.card_desvio = self._create_card(kpi_frame, 2, "⚖️ Margen Disponible", "$ 0", COLOR_SUCCESS)

        # Budget Table
        table_frame = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10)
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        cols = ("grupo", "categoria", "presupuesto", "real", "diferencia", "porcentaje")
        self.tree = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )

        self.tree.heading("grupo", text="Grupo")
        self.tree.heading("categoria", text="Categoría")
        self.tree.heading("presupuesto", text="Presupuesto ($)")
        self.tree.heading("real", text="Gasto Real ($)")
        self.tree.heading("diferencia", text="Disponible / Desvío")
        self.tree.heading("porcentaje", text="% Consumido")

        self.tree.column("grupo", width=130, anchor="w")
        self.tree.column("categoria", width=180, anchor="w")
        self.tree.column("presupuesto", width=130, anchor="e")
        self.tree.column("real", width=130, anchor="e")
        self.tree.column("diferencia", width=150, anchor="e")
        self.tree.column("porcentaje", width=110, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)

        # Actions toolbar
        bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=20, pady=(5, 15))

        btn_set = ctk.CTkButton(
            bottom_bar,
            text="✏️ Asignar / Modificar Presupuesto",
            fg_color=COLOR_PRIMARY,
            command=self.open_edit_budget_dialog
        )
        btn_set.pack(side="left", padx=5)

        btn_init_defaults = ctk.CTkButton(
            bottom_bar,
            text="⚡ Cargar Plantilla de Categorías",
            fg_color="#334155",
            command=self.seed_default_budget
        )
        btn_init_defaults.pack(side="left", padx=5)

    def _create_card(self, parent, col, title, initial_value, text_color):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12)
        card.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)

        lbl_t = ctk.CTkLabel(card, text=title, font=FONT_SMALL, text_color=TEXT_MUTED)
        lbl_t.pack(anchor="w", padx=15, pady=(10, 2))

        lbl_v = ctk.CTkLabel(card, text=initial_value, font=FONT_HEADER, text_color=text_color)
        lbl_v.pack(anchor="w", padx=15, pady=(0, 10))
        return lbl_v

    def on_period_change(self, _=None):
        try:
            self.selected_year = int(self.cb_year.get())
            self.selected_month = mes_numero(self.cb_month.get()) or 1
            self.load_budget()
        except ValueError:
            pass

    def seed_default_budget(self):
        for grupo, cat in DEFAULT_BUDGET_CATEGORIES:
            # Check if exists, else insert with 0
            existing = self.db.conn.execute(
                "SELECT id FROM budget_items WHERE mes=? AND anio=? AND categoria=?",
                (self.selected_month, self.selected_year, cat)
            ).fetchone()
            if not existing:
                self.db.set_budget_item(self.selected_month, self.selected_year, grupo, cat, 0)
        self.load_budget()
        messagebox.showinfo("Plantilla", f"Se cargaron las categorías base para {mes_nombre(self.selected_month)} {self.selected_year}.")

    def load_budget(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        items = self.db.get_budget_vs_real(self.selected_month, self.selected_year)
        total_presupuesto = 0.0
        total_real = 0.0

        for it in items:
            total_presupuesto += it["presupuesto"]
            total_real += it["real"]

            pct_str = f"{it['porcentaje']:.1f}%" if it["presupuesto"] > 0 else "-"
            dif_str = format_currency(it["diferencia"])

            self.tree.insert("", "end", values=(
                it["grupo"],
                it["categoria"],
                format_currency(it["presupuesto"]),
                format_currency(it["real"]),
                dif_str,
                pct_str
            ))

        self.card_presupuestado.configure(text=format_currency(total_presupuesto))
        self.card_real.configure(text=format_currency(total_real))

        disp = total_presupuesto - total_real
        disp_color = COLOR_SUCCESS if disp >= 0 else COLOR_DANGER
        self.card_desvio.configure(text=format_currency(disp), text_color=disp_color)

    def open_edit_budget_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Definir Presupuesto por Categoría")
        dialog.geometry("420x400")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog,
            text=f"Presupuesto: {mes_nombre(self.selected_month)} {self.selected_year}",
            font=FONT_HEADER,
            text_color=TEXT_MAIN
        ).pack(pady=(15, 10))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=25, pady=5)

        # Grupo
        ctk.CTkLabel(form, text="Grupo (ej: Casa, Alimento, Transporte, Tarjeta):", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ent_grupo = ctk.CTkEntry(form, font=FONT_BODY)
        ent_grupo.pack(fill="x", pady=(2, 8))
        ent_grupo.insert(0, "General")

        # Categoría
        ctk.CTkLabel(form, text="Categoría (ej: Supermercado, Alquiler, Luz):", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        cats = self.db.get_available_categories() or ["Supermercado", "Servicios", "Alquiler", "Salida"]
        cb_cat = ctk.CTkComboBox(form, values=cats, font=FONT_BODY)
        cb_cat.pack(fill="x", pady=(2, 8))

        # Monto presupuestado
        ctk.CTkLabel(form, text="Presupuesto Mensual Asignado ($):", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ent_monto = ctk.CTkEntry(form, font=FONT_BODY)
        ent_monto.pack(fill="x", pady=(2, 12))

        def save():
            grupo = ent_grupo.get().strip() or "General"
            cat = cb_cat.get().strip()
            try:
                monto = float(ent_monto.get().strip().replace("$", "").replace(",", ""))
                if monto < 0:
                    raise ValueError
                self.db.set_budget_item(self.selected_month, self.selected_year, grupo, cat, monto)
                dialog.destroy()
                self.load_budget()
            except ValueError:
                messagebox.showerror("Error", "Ingresa un monto válido mayor o igual a 0.")

        ctk.CTkButton(dialog, text="Guardar Presupuesto", fg_color=COLOR_SUCCESS, font=FONT_BODY_BOLD, command=save).pack(pady=15)
