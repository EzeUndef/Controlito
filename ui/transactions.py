"""Transactions management view (Gastos e Ingresos)."""
import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, date
from utils.helpers import format_currency, format_date, mes_nombre, mes_numero
from ui.theme import (
    ThemeManager, configure_treeview_style,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS, COLOR_DANGER,
    COLOR_WARNING, BG_CARD, BG_MAIN, TEXT_MAIN, TEXT_MUTED,
    FONT_TITLE, FONT_HEADER, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)


class TransactionsView(ctk.CTkFrame):
    def __init__(self, parent, db, on_data_changed=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_data_changed = on_data_changed

        self.current_page = 0
        self.page_size = 50
        self.sort_column = "fecha"
        self.sort_dir = "DESC"

        self.build_ui()
        self.load_filters()
        self.load_transactions()

    def build_ui(self):
        # Header
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(header_frame, text="💰 Movimientos (Gastos & Ingresos)", font=FONT_TITLE, text_color=TEXT_MAIN)
        title.pack(side="left")

        btn_new = ctk.CTkButton(
            header_frame,
            text="+ Nuevo Movimiento",
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            font=FONT_BODY_BOLD,
            command=self.open_add_dialog
        )
        btn_new.pack(side="right", padx=5)

        # Financial Summary Cards
        summary_cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        summary_cards_frame.pack(fill="x", padx=20, pady=(0, 10))
        summary_cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="tx_kpi")

        self.card_plata_ahora = self._create_summary_card(
            summary_cards_frame, 0, "💵 Plata que tengo ahora", "$ 0", "#38bdf8"
        )
        self.card_gastado_mes = self._create_summary_card(
            summary_cards_frame, 1, "💸 Gastado en el Mes", "$ 0", COLOR_DANGER
        )
        self.card_ingreso_mes = self._create_summary_card(
            summary_cards_frame, 2, "💰 Ingresos del Mes", "$ 0", COLOR_SUCCESS
        )
        self.card_total_quedo = self._create_summary_card(
            summary_cards_frame, 3, "⚖️ Total Quedó (Sobrante)", "$ 0", COLOR_PRIMARY
        )

        # Filters Toolbar
        toolbar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        # Search entry
        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="🔍 Buscar por descripción o categoría...",
            width=260,
            font=FONT_BODY
        )
        self.search_entry.pack(side="left", padx=12, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.apply_filters())

        # Year filter
        ctk.CTkLabel(toolbar, text="Año:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left", padx=(10, 2))
        self.cb_year = ctk.CTkComboBox(toolbar, values=["Todos"], width=95, command=lambda _: self.apply_filters())
        self.cb_year.pack(side="left", padx=5)

        # Month filter
        ctk.CTkLabel(toolbar, text="Mes:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left", padx=(10, 2))
        self.cb_month = ctk.CTkComboBox(toolbar, values=["Todos"] + [mes_nombre(i) for i in range(1, 13)], width=110, command=lambda _: self.apply_filters())
        self.cb_month.pack(side="left", padx=5)

        # Category filter
        ctk.CTkLabel(toolbar, text="Categoría:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left", padx=(10, 2))
        self.cb_category = ctk.CTkComboBox(toolbar, values=["Todas"], width=130, command=lambda _: self.apply_filters())
        self.cb_category.pack(side="left", padx=5)

        # Order by dropdown
        ctk.CTkLabel(toolbar, text="Ordenar:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left", padx=(10, 2))
        self.order_options = {
            "Fecha (Recientes)": ("fecha", "DESC"),
            "Fecha (Antiguos)": ("fecha", "ASC"),
            "Mayor Gasto": ("gasto", "DESC"),
            "Mayor Ingreso": ("ingreso", "DESC"),
            "Descripción (A-Z)": ("descripcion", "ASC"),
            "Categoría (A-Z)": ("categoria", "ASC")
        }
        self.cb_order = ctk.CTkComboBox(
            toolbar,
            values=list(self.order_options.keys()),
            width=150,
            command=self.on_order_dropdown_change
        )
        self.cb_order.set("Fecha (Recientes)")
        self.cb_order.pack(side="left", padx=5)

        # Filter button
        btn_filter = ctk.CTkButton(toolbar, text="Filtrar", width=65, command=self.apply_filters, fg_color=COLOR_PRIMARY)
        btn_filter.pack(side="left", padx=6)

        # Reset button
        btn_reset = ctk.CTkButton(toolbar, text="Limpiar", width=65, command=self.reset_filters, fg_color="#64748b")
        btn_reset.pack(side="left", padx=2)

        curr = ThemeManager.get_current_theme()
        configure_treeview_style(curr)

        # Table container
        table_frame = ctk.CTkFrame(self, fg_color=curr["bg_card"], corner_radius=12, border_width=1, border_color=curr["border"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        columns = ("id", "fecha", "categoria", "descripcion", "ingreso", "gasto")
        self.tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )

        self.update_header_labels()

        self.tree.column("id", width=50, anchor="center")
        self.tree.column("fecha", width=110, anchor="center")
        self.tree.column("categoria", width=140, anchor="w")
        self.tree.column("descripcion", width=340, anchor="w")
        self.tree.column("ingreso", width=115, anchor="e")
        self.tree.column("gasto", width=115, anchor="e")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

        # Double click to edit selected transaction
        self.tree.bind("<Double-1>", lambda e: self.open_edit_dialog())

        # Zebra striping tags configuration
        self.tree.tag_configure("evenrow", background=curr["bg_card"])
        self.tree.tag_configure("oddrow", background=curr.get("bg_card_alt", curr["bg_main"]))

        # Context action buttons (Edit, Delete) & Pagination
        bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=20, pady=(5, 15))

        btn_edit = ctk.CTkButton(bottom_bar, text="✏️ Editar Seleccionado", width=140, command=self.open_edit_dialog, fg_color="#475569")
        btn_edit.pack(side="left", padx=5)

        btn_del = ctk.CTkButton(bottom_bar, text="🗑️ Eliminar", width=100, command=self.delete_selected, fg_color=COLOR_DANGER, hover_color="#b91c1c")
        btn_del.pack(side="left", padx=5)

        # Pagination controls
        self.lbl_page_info = ctk.CTkLabel(bottom_bar, text="Mostrando 0-0 de 0", font=FONT_SMALL, text_color=TEXT_MUTED)
        self.lbl_page_info.pack(side="right", padx=10)

        self.btn_next = ctk.CTkButton(bottom_bar, text="Siguiente ▶", width=80, command=self.next_page, fg_color="#334155")
        self.btn_next.pack(side="right", padx=3)

        self.btn_prev = ctk.CTkButton(bottom_bar, text="◀ Anterior", width=80, command=self.prev_page, fg_color="#334155")
        self.btn_prev.pack(side="right", padx=3)

    def _create_summary_card(self, parent, col, title, initial_value, text_color):
        """Creates a KPI summary card and returns the value label for dynamic updates."""
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10)
        card.grid(row=0, column=col, sticky="nsew", padx=4, pady=2)

        lbl_t = ctk.CTkLabel(card, text=title, font=FONT_SMALL, text_color=TEXT_MUTED)
        lbl_t.pack(anchor="w", padx=12, pady=(8, 2))

        lbl_v = ctk.CTkLabel(card, text=initial_value, font=("Segoe UI", 16, "bold"), text_color=text_color)
        lbl_v.pack(anchor="w", padx=12, pady=(0, 8))
        return lbl_v

    def update_header_labels(self):
        arrow = " ▼" if self.sort_dir == "DESC" else " ▲"
        headers = {
            "id": "ID",
            "fecha": "Fecha",
            "categoria": "Categoría",
            "descripcion": "Descripción",
            "ingreso": "Ingreso (+)",
            "gasto": "Gasto (-)"
        }
        for col, base_label in headers.items():
            display_label = f"{base_label}{arrow}" if col == self.sort_column else base_label
            self.tree.heading(col, text=display_label, command=lambda c=col: self.sort_by_column(c))

    def sort_by_column(self, col):
        if self.sort_column == col:
            self.sort_dir = "ASC" if self.sort_dir == "DESC" else "DESC"
        else:
            self.sort_column = col
            self.sort_dir = "DESC" if col in ("fecha", "gasto", "ingreso") else "ASC"

        self.update_header_labels()
        self.current_page = 0
        self.load_transactions()

    def on_order_dropdown_change(self, val):
        if val in self.order_options:
            col, direction = self.order_options[val]
            self.sort_column = col
            self.sort_dir = direction
            self.update_header_labels()
            self.current_page = 0
            self.load_transactions()

    def load_filters(self, keep_current=False):
        current_year = self.cb_year.get() if keep_current else "Todos"
        current_month = self.cb_month.get() if keep_current else "Todos"
        current_cat = self.cb_category.get() if keep_current else "Todas"

        years = self.db.get_available_years()
        year_vals = ["Todos"] + [str(y) for y in years] if years else ["Todos"]
        self.cb_year.configure(values=year_vals)
        if keep_current and current_year in year_vals:
            self.cb_year.set(current_year)
        else:
            self.cb_year.set("Todos")

        month_vals = ["Todos"] + [mes_nombre(i) for i in range(1, 13)]
        self.cb_month.configure(values=month_vals)
        if keep_current and current_month in month_vals:
            self.cb_month.set(current_month)
        else:
            self.cb_month.set("Todos")

        cats = self.db.get_available_categories()
        cat_vals = ["Todas"] + cats if cats else ["Todas"]
        self.cb_category.configure(values=cat_vals)
        if keep_current and current_cat in cat_vals:
            self.cb_category.set(current_cat)
        else:
            self.cb_category.set("Todas")

    def get_filter_params(self):
        year_str = self.cb_year.get()
        year = int(year_str) if year_str != "Todos" else None

        month_str = self.cb_month.get()
        month = mes_numero(month_str) if month_str != "Todos" else None

        cat_str = self.cb_category.get()
        cat = cat_str if cat_str != "Todas" else None

        search = self.search_entry.get().strip() or None
        return year, month, cat, search

    def apply_filters(self):
        self.current_page = 0
        self.load_transactions()

    def reset_filters(self):
        self.search_entry.delete(0, "end")
        self.cb_year.set("Todos")
        self.cb_month.set("Todos")
        self.cb_category.set("Todas")
        self.current_page = 0
        self.load_transactions()

    def load_transactions(self):
        # Clear tree
        for row in self.tree.get_children():
            self.tree.delete(row)

        year, month, cat, search = self.get_filter_params()
        total_count = self.db.get_transaction_count(year, month, cat, search)

        # Update Summary Cards dynamically
        period_summary = self.db.get_filtered_summary(year, month, cat, search)
        self.card_gastado_mes.configure(text=format_currency(period_summary["gasto"]))
        self.card_ingreso_mes.configure(text=format_currency(period_summary["ingreso"]))
        
        quedo = period_summary["balance"]
        quedo_color = COLOR_SUCCESS if quedo >= 0 else COLOR_DANGER
        self.card_total_quedo.configure(text=format_currency(quedo), text_color=quedo_color)

        # Plata que tengo ahora (Balance del último mes activo)
        cur = self.db.get_current_available_money()
        self.card_plata_ahora.configure(text=format_currency(cur["saldo"]))

        offset = self.current_page * self.page_size
        rows = self.db.get_transactions(
            year, month, cat, search,
            limit=self.page_size, offset=offset,
            order_by=self.sort_column, order_dir=self.sort_dir
        )

        for idx, r in enumerate(rows):
            ing_str = f"+ {format_currency(r['ingreso'])}" if r["ingreso"] > 0 else "-"
            gas_str = f"- {format_currency(r['gasto'])}" if r["gasto"] > 0 else "-"
            tag = "evenrow" if (idx % 2 == 0) else "oddrow"
            self.tree.insert("", "end", values=(
                r["id"],
                format_date(r["fecha"]),
                r["categoria"],
                r["descripcion"],
                ing_str,
                gas_str
            ), tags=(tag,))

        start_idx = offset + 1 if total_count > 0 else 0
        end_idx = min(offset + len(rows), total_count)
        self.lbl_page_info.configure(text=f"Mostrando {start_idx}-{end_idx} de {total_count}")

        self.btn_prev.configure(state="normal" if self.current_page > 0 else "disabled")
        self.btn_next.configure(state="normal" if end_idx < total_count else "disabled")

    def next_page(self):
        self.current_page += 1
        self.load_transactions()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.load_transactions()

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Por favor selecciona un movimiento de la tabla para eliminar.")
            return

        item = self.tree.item(selected[0])
        tid = item["values"][0]
        desc = item["values"][3]

        if messagebox.askyesno("Confirmar eliminación", f"¿Estás seguro de eliminar el movimiento:\n'{desc}'?"):
            self.db.delete_transaction(tid)
            self.load_transactions()
            if self.on_data_changed:
                self.on_data_changed()

    def open_add_dialog(self):
        self._open_transaction_dialog(title="Nuevo Movimiento")

    def open_edit_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Por favor selecciona un movimiento de la tabla para editar.")
            return

        item = self.tree.item(selected[0])
        tid = item["values"][0]

        # Fetch full row from db
        row = self.db.conn.execute("SELECT * FROM transactions WHERE id=?", (tid,)).fetchone()
        if row:
            self._open_transaction_dialog(title="Editar Movimiento", record=row)

    def _open_transaction_dialog(self, title, record=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("450x480")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 225
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 240
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialog, text=title, font=FONT_HEADER, text_color=TEXT_MAIN).pack(pady=(15, 10))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=25, pady=5)

        # Fecha
        ctk.CTkLabel(form, text="Fecha (AAAA-MM-DD):", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ent_fecha = ctk.CTkEntry(form, font=FONT_BODY)
        ent_fecha.pack(fill="x", pady=(2, 10))
        ent_fecha.insert(0, str(record["fecha"]) if record else date.today().isoformat())

        # Categoría
        ctk.CTkLabel(form, text="Categoría:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        cats = self.db.get_available_categories() or ["General", "Sueldo", "Supermercado", "Servicios", "Salida"]
        cb_cat = ctk.CTkComboBox(form, values=cats, font=FONT_BODY)
        cb_cat.pack(fill="x", pady=(2, 10))
        cb_cat.set(record["categoria"] if record else cats[0])

        # Descripción
        ctk.CTkLabel(form, text="Descripción:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ent_desc = ctk.CTkEntry(form, font=FONT_BODY)
        ent_desc.pack(fill="x", pady=(2, 10))
        if record and record["descripcion"]:
            ent_desc.insert(0, record["descripcion"])

        # Amounts: Ingreso ($) and Gasto ($) - editable both
        amounts_frame = ctk.CTkFrame(form, fg_color="transparent")
        amounts_frame.pack(fill="x", pady=(5, 15))
        amounts_frame.grid_columnconfigure((0, 1), weight=1)

        # Ingreso
        ctk.CTkLabel(amounts_frame, text="Ingreso ($):", font=FONT_SMALL, text_color=COLOR_SUCCESS).grid(row=0, column=0, padx=(0, 6), sticky="w")
        ent_ingreso = ctk.CTkEntry(amounts_frame, font=FONT_BODY)
        ent_ingreso.grid(row=1, column=0, padx=(0, 6), pady=(2, 0), sticky="ew")
        init_ingreso = record["ingreso"] if (record and record["ingreso"] > 0) else 0.0
        ent_ingreso.insert(0, str(init_ingreso) if init_ingreso > 0 else "0")

        # Gasto
        ctk.CTkLabel(amounts_frame, text="Gasto ($):", font=FONT_SMALL, text_color=COLOR_DANGER).grid(row=0, column=1, padx=(6, 0), sticky="w")
        ent_gasto = ctk.CTkEntry(amounts_frame, font=FONT_BODY)
        ent_gasto.grid(row=1, column=1, padx=(6, 0), pady=(2, 0), sticky="ew")
        init_gasto = record["gasto"] if (record and record["gasto"] > 0) else 0.0
        ent_gasto.insert(0, str(init_gasto) if init_gasto > 0 else "0")

        def save():
            fecha_str = ent_fecha.get().strip()
            cat_str = cb_cat.get().strip() or "Sin categoría"
            desc_str = ent_desc.get().strip()

            try:
                dt = datetime.strptime(fecha_str, "%Y-%m-%d").date()
            except ValueError:
                messagebox.showerror("Error", "Formato de fecha inválido. Utiliza el formato AAAA-MM-DD.")
                return

            try:
                ingreso = float(ent_ingreso.get().strip().replace("$", "").replace(",", "") or 0)
                gasto = float(ent_gasto.get().strip().replace("$", "").replace(",", "") or 0)
                if ingreso < 0 or gasto < 0:
                    raise ValueError
                if ingreso == 0 and gasto == 0:
                    messagebox.showwarning("Atención", "Debes ingresar al menos un monto en Ingreso o en Gasto.")
                    return
            except ValueError:
                messagebox.showerror("Error", "El ingreso y el gasto deben ser números válidos mayores o iguales a cero.")
                return

            if record:
                self.db.update_transaction(record["id"], dt, cat_str, desc_str, ingreso, gasto)
            else:
                self.db.add_transaction(dt, cat_str, desc_str, ingreso, gasto)

            dialog.destroy()
            self.load_filters(keep_current=True)
            self.load_transactions()
            if self.on_data_changed:
                self.on_data_changed()

        btn_save = ctk.CTkButton(dialog, text="Guardar Movimiento", fg_color=COLOR_SUCCESS, hover_color="#059669", font=FONT_BODY_BOLD, command=save)
        btn_save.pack(pady=10)
