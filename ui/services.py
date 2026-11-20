"""Services view (Servicios: Gas, Agua, Luz, Cable) with adaptable per-month bill splitting."""
import customtkinter as ctk
from tkinter import ttk, messagebox
from utils.helpers import format_currency, mes_nombre
from ui.theme import (
    ThemeManager, configure_treeview_style,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS, COLOR_DANGER, COLOR_PURPLE, COLOR_WARNING,
    BG_CARD, BG_MAIN, TEXT_MAIN, TEXT_MUTED, FONT_TITLE, FONT_HEADER,
    FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)

MESES_LISTA = [
    "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
    "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
]


class ServicesView(ctk.CTkFrame):
    def __init__(self, parent, db, on_data_changed=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_data_changed = on_data_changed

        years = self.db.get_services_years() or [2025, 2026, 2027]
        self.selected_year = years[-1] if years else 2026

        # Ensure treeview style matches current active theme
        configure_treeview_style()

        self.build_ui()
        self.load_services()

    def build_ui(self):
        curr = ThemeManager.get_current_theme()

        # Header Frame
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        title = ctk.CTkLabel(title_box, text="⚡ Servicios del Hogar & División", font=FONT_TITLE, text_color=curr["text_main"])
        title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box,
            text="Control mensual de servicios y cuotas individuales adaptables por mes.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        )
        lbl_sub.pack(anchor="w")

        # Right header controls (Year selector & Add buttons)
        right_box = ctk.CTkFrame(header, fg_color="transparent")
        right_box.pack(side="right")

        btn_add_month = ctk.CTkButton(
            right_box,
            text="+ Agregar Mes",
            fg_color=curr["primary"],
            hover_color=curr["primary_hover"],
            font=FONT_BODY_BOLD,
            width=120,
            command=self.open_add_month_dialog
        )
        btn_add_month.pack(side="right", padx=(6, 0))

        btn_add_year = ctk.CTkButton(
            right_box,
            text="+ Habilitar Año",
            fg_color=curr["bg_card"],
            hover_color=curr["border"],
            font=FONT_BODY_BOLD,
            width=115,
            command=self.open_add_year_dialog
        )
        btn_add_year.pack(side="right", padx=6)

        years = [str(y) for y in (self.db.get_services_years() or [2025, 2026, 2027])]
        self.cb_year = ctk.CTkComboBox(right_box, values=years, width=95, font=FONT_BODY_BOLD, command=self.on_year_change)
        self.cb_year.set(str(self.selected_year))
        self.cb_year.pack(side="right", padx=6)

        ctk.CTkLabel(right_box, text="Año:", font=FONT_BODY_BOLD, text_color=curr["text_muted"]).pack(side="right", padx=(0, 2))

        # Top KPI Summary Cards (Annual Total, Average Per Person, Highest Month, Active Months)
        kpi_frame = ctk.CTkFrame(self, fg_color="transparent")
        kpi_frame.pack(fill="x", padx=20, pady=(0, 10))
        kpi_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="srv_kpi")

        self.kpi_total_anual = self._create_kpi_card(kpi_frame, 0, "💰 Total Anual Hogar", "$ 0", curr["primary"])
        self.kpi_cuota_promedio = self._create_kpi_card(kpi_frame, 1, "👥 Cuota Promedio x Persona", "$ 0", curr["success"])
        self.kpi_mes_pico = self._create_kpi_card(kpi_frame, 2, "🔥 Mes de Mayor Consumo", "—", curr["warning"])
        self.kpi_meses_cargados = self._create_kpi_card(kpi_frame, 3, "📅 Meses Registrados", "0 de 12", curr["text_accent"])

        # Table Container Card
        table_container = ctk.CTkFrame(self, fg_color=curr["bg_card"], corner_radius=12, border_width=1, border_color=curr["border"])
        table_container.pack(fill="both", expand=True, padx=20, pady=5)

        # Treeview Columns
        cols = ("id", "mes", "gas", "agua", "luz", "cable", "total_sin", "total_con", "personas", "cuota_persona")
        self.tree = ttk.Treeview(
            table_container,
            columns=cols,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )

        # Configure headings with descriptive icons
        self.tree.heading("id", text="#")
        self.tree.heading("mes", text="🗓️ Mes")
        self.tree.heading("gas", text="🔥 Gas ($)")
        self.tree.heading("agua", text="💧 Agua ($)")
        self.tree.heading("luz", text="💡 Luz ($)")
        self.tree.heading("cable", text="📡 Cable / Wi-Fi")
        self.tree.heading("total_sin", text="Total sin Luz")
        self.tree.heading("total_con", text="Total Hogar")
        self.tree.heading("personas", text="👥 Personas")
        self.tree.heading("cuota_persona", text="💰 Cuota x Persona")

        # Column widths & alignments
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("mes", width=110, anchor="w")
        self.tree.column("gas", width=95, anchor="e")
        self.tree.column("agua", width=95, anchor="e")
        self.tree.column("luz", width=100, anchor="e")
        self.tree.column("cable", width=100, anchor="e")
        self.tree.column("total_sin", width=105, anchor="e")
        self.tree.column("total_con", width=115, anchor="e")
        self.tree.column("personas", width=90, anchor="center")
        self.tree.column("cuota_persona", width=130, anchor="e")

        # Scrollbar styled cleanly
        scrollbar = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

        # Double click to edit selected month
        self.tree.bind("<Double-1>", lambda e: self.open_edit_service_dialog())

        # Zebra striping tags configuration with current theme
        self.tree.tag_configure("evenrow", background=curr["bg_card"])
        self.tree.tag_configure("oddrow", background=curr.get("bg_card_alt", curr["bg_main"]))
        self.tree.tag_configure("zerorow", foreground=curr["text_muted"])

        # Bottom Action Bar
        bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=20, pady=(6, 12))

        # Quick action: modify complete month
        btn_edit = ctk.CTkButton(
            bottom_bar,
            text="✏️ Modificar Mes",
            font=FONT_BODY_BOLD,
            fg_color=curr["primary"],
            hover_color=curr["primary_hover"],
            command=self.open_edit_service_dialog
        )
        btn_edit.pack(side="left", padx=4)

        # Quick action: change ONLY the personas for the selected month
        btn_personas_quick = ctk.CTkButton(
            bottom_bar,
            text="👥 Ajustar Personas del Mes",
            font=FONT_BODY_BOLD,
            fg_color=curr["bg_card"],
            hover_color=curr["border"],
            border_width=1,
            border_color=curr["border"],
            text_color=curr["text_accent"],
            command=self.open_quick_personas_dialog
        )
        btn_personas_quick.pack(side="left", padx=4)

        btn_del = ctk.CTkButton(
            bottom_bar,
            text="🗑️ Eliminar Mes",
            font=FONT_BODY,
            fg_color=COLOR_DANGER,
            hover_color="#b91c1c",
            width=110,
            command=self.delete_selected_month
        )
        btn_del.pack(side="left", padx=4)

        # Help hint
        lbl_hint = ctk.CTkLabel(
            bottom_bar,
            text="💡 Tip: Haz doble clic en cualquier mes para editar montos y personas rápidamente.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        )
        lbl_hint.pack(side="right", padx=10)

    def _create_kpi_card(self, parent, col, title, initial_val, text_col):
        curr = ThemeManager.get_current_theme()
        card = ctk.CTkFrame(parent, fg_color=curr["bg_card"], corner_radius=10, border_width=1, border_color=curr["border"])
        card.grid(row=0, column=col, sticky="nsew", padx=4, pady=2)

        lbl_t = ctk.CTkLabel(card, text=title, font=FONT_SMALL, text_color=curr["text_muted"])
        lbl_t.pack(anchor="w", padx=12, pady=(8, 1))

        lbl_v = ctk.CTkLabel(card, text=initial_val, font=("Bahnschrift", 16, "bold"), text_color=text_col)
        lbl_v.pack(anchor="w", padx=12, pady=(0, 8))
        return lbl_v

    def on_year_change(self, _=None):
        try:
            self.selected_year = int(self.cb_year.get())
            self.load_services()
        except ValueError:
            pass

    def load_services(self):
        # Clear treeview
        for row in self.tree.get_children():
            self.tree.delete(row)

        curr = ThemeManager.get_current_theme()
        rows = self.db.get_services(self.selected_year)

        total_anual = 0.0
        cuotas_totales = 0.0
        meses_con_monto = 0
        max_monto = -1
        mes_pico_nombre = "—"

        for idx, r in enumerate(rows):
            con_luz = r["total_con_luz"] if r["total_con_luz"] > 0 else (r["gas"] + r["agua"] + r["luz"] + r["cable"])
            sin_luz = r["total_sin_luz"] if r["total_sin_luz"] > 0 else (r["gas"] + r["agua"] + r["cable"])
            total_anual += con_luz

            # Per-month adaptable personas!
            personas_mes = int(r["personas"]) if r["personas"] and r["personas"] > 0 else 4
            cuota_mes = con_luz / personas_mes if personas_mes > 0 else con_luz

            if con_luz > 0:
                meses_con_monto += 1
                cuotas_totales += cuota_mes
                if con_luz > max_monto:
                    max_monto = con_luz
                    mes_pico_nombre = f"{r['mes']} ({format_currency(con_luz)})"

            # Determine row tag for alternating backgrounds
            tag = "evenrow" if (idx % 2 == 0) else "oddrow"
            if con_luz == 0:
                tag = "zerorow"

            self.tree.insert("", "end", values=(
                r["id"],
                r["mes"],
                format_currency(r["gas"]),
                format_currency(r["agua"]),
                format_currency(r["luz"]),
                format_currency(r["cable"]),
                format_currency(sin_luz),
                format_currency(con_luz),
                f"👥 {personas_mes}",
                format_currency(cuota_mes),
            ), tags=(tag,))

        # Update KPI cards
        self.kpi_total_anual.configure(text=format_currency(total_anual))
        prom_cuota = (cuotas_totales / meses_con_monto) if meses_con_monto > 0 else 0
        self.kpi_cuota_promedio.configure(text=format_currency(prom_cuota))
        self.kpi_mes_pico.configure(text=mes_pico_nombre)
        self.kpi_meses_cargados.configure(text=f"{len(rows)} meses ({meses_con_monto} activos)")

    def open_quick_personas_dialog(self):
        """Allows changing specifically the number of people for the selected month in a single click."""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Por favor selecciona un mes de la tabla para ajustar sus personas.")
            return

        item = self.tree.item(selected[0])
        sid = item["values"][0]
        mes_nombre_sel = item["values"][1]

        row = self.db.conn.execute("SELECT personas, total_con_luz FROM services WHERE id=?", (sid,)).fetchone()
        if not row:
            return

        curr_personas = row["personas"] if row["personas"] and row["personas"] > 0 else 4
        monto_total = row["total_con_luz"] or 0

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"División de {mes_nombre_sel}")
        dialog.geometry("380x280")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 190
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 140
        dialog.geometry(f"+{x}+{y}")

        curr = ThemeManager.get_current_theme()
        dialog.configure(fg_color=curr["bg_main"])

        ctk.CTkLabel(
            dialog,
            text=f"👥 División para {mes_nombre_sel} {self.selected_year}",
            font=FONT_HEADER,
            text_color=curr["text_main"]
        ).pack(pady=(20, 5))

        ctk.CTkLabel(
            dialog,
            text=f"Gasto total del hogar: {format_currency(monto_total)}",
            font=FONT_BODY_BOLD,
            text_color=curr["primary"]
        ).pack(pady=(0, 15))

        form = ctk.CTkFrame(dialog, fg_color=curr["bg_card"], corner_radius=10)
        form.pack(fill="x", padx=25, pady=5)

        ctk.CTkLabel(
            form,
            text="¿Entre cuántas personas se divide este mes puntual?",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        ).pack(pady=(10, 4))

        controls_box = ctk.CTkFrame(form, fg_color="transparent")
        controls_box.pack(pady=(0, 12))

        ent_num = ctk.CTkEntry(controls_box, font=("Bahnschrift", 16, "bold"), width=60, justify="center")
        ent_num.insert(0, str(curr_personas))

        def step(delta):
            try:
                val = max(1, int(ent_num.get().strip()) + delta)
                ent_num.delete(0, "end")
                ent_num.insert(0, str(val))
                update_calc()
            except ValueError:
                pass

        btn_minus = ctk.CTkButton(controls_box, text="−", width=32, font=FONT_BODY_BOLD, fg_color="#334155", command=lambda: step(-1))
        btn_minus.pack(side="left", padx=4)

        ent_num.pack(side="left", padx=4)

        btn_plus = ctk.CTkButton(controls_box, text="+", width=32, font=FONT_BODY_BOLD, fg_color="#334155", command=lambda: step(1))
        btn_plus.pack(side="left", padx=4)

        lbl_result = ctk.CTkLabel(form, text="", font=FONT_BODY_BOLD, text_color=curr["success"])
        lbl_result.pack(pady=(0, 8))

        def update_calc(*_):
            try:
                p = int(ent_num.get().strip())
                if p > 0:
                    cuota = monto_total / p
                    lbl_result.configure(text=f"→ Cada uno paga: {format_currency(cuota)}")
            except ValueError:
                lbl_result.configure(text="")

        update_calc()
        ent_num.bind("<KeyRelease>", update_calc)

        def save_quick():
            try:
                p = max(1, int(ent_num.get().strip()))
                self.db.update_service(sid, personas=p)
                dialog.destroy()
                self.load_services()
                if self.on_data_changed:
                    self.on_data_changed()
            except ValueError:
                messagebox.showerror("Error", "Debes ingresar un número entero válido mayor a 0.")

        btn_save = ctk.CTkButton(
            dialog,
            text="Guardar División de Este Mes",
            font=FONT_BODY_BOLD,
            fg_color=curr["success"],
            hover_color="#059669",
            command=save_quick
        )
        btn_save.pack(pady=15)

    def open_add_year_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Habilitar Nuevo Año para Servicios")
        dialog.geometry("380x230")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        curr = ThemeManager.get_current_theme()
        dialog.configure(fg_color=curr["bg_main"])

        ctk.CTkLabel(dialog, text="Habilitar Año de Servicios", font=FONT_HEADER, text_color=curr["text_main"]).pack(pady=(20, 10))
        ctk.CTkLabel(dialog, text="Ingresa el año a habilitar (ej: 2028, 2029):", font=FONT_SMALL, text_color=curr["text_muted"]).pack()

        ent_year = ctk.CTkEntry(dialog, font=FONT_BODY, width=180, justify="center")
        ent_year.pack(pady=10)

        current_years = self.db.get_services_years() or [2027]
        next_suggested = max(current_years) + 1
        ent_year.insert(0, str(next_suggested))

        def confirm_add():
            val = ent_year.get().strip()
            try:
                y = int(val)
                if y < 2000 or y > 2100:
                    raise ValueError
                self.db.add_services_year(y)

                updated_years = [str(yr) for yr in self.db.get_services_years()]
                self.cb_year.configure(values=updated_years)
                self.cb_year.set(str(y))
                self.selected_year = y
                self.load_services()

                dialog.destroy()
                messagebox.showinfo("Éxito", f"Se habilitó el año {y} con los 12 meses listos para cargar.")
                if self.on_data_changed:
                    self.on_data_changed()
            except ValueError:
                messagebox.showerror("Error", "Por favor ingresa un año válido (ej: 2028).")

        ctk.CTkButton(dialog, text="Habilitar Año", fg_color=curr["success"], font=FONT_BODY_BOLD, command=confirm_add).pack(pady=15)

    def open_add_month_dialog(self):
        """Dialog to add a specific month with its own individual people count."""
        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Agregar Mes a {self.selected_year}")
        dialog.geometry("420x560")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        curr = ThemeManager.get_current_theme()
        dialog.configure(fg_color=curr["bg_main"])

        ctk.CTkLabel(dialog, text=f"Agregar Mes — {self.selected_year}", font=FONT_HEADER, text_color=curr["text_main"]).pack(pady=(15, 10))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=25, pady=5)

        ctk.CTkLabel(form, text="Seleccionar Mes:", font=FONT_SMALL, text_color=curr["text_muted"]).pack(anchor="w")

        existing = self.db.get_services(self.selected_year)
        existing_nums = {r["mes_num"] for r in existing}
        available_months = [m for i, m in enumerate(MESES_LISTA, 1) if i not in existing_nums]

        if not available_months:
            ctk.CTkLabel(form, text="✅ Todos los meses del año ya están registrados.", font=FONT_BODY, text_color=curr["success"]).pack(pady=20)
            ctk.CTkButton(dialog, text="Cerrar", fg_color="#475569", command=dialog.destroy).pack(pady=15)
            return

        cb_mes = ctk.CTkComboBox(form, values=available_months, font=FONT_BODY, width=200)
        cb_mes.set(available_months[0])
        cb_mes.pack(fill="x", pady=(2, 10))

        fields = [
            ("Gas ($):", "gas"),
            ("Agua ($):", "agua"),
            ("Luz ($):", "luz"),
            ("Cable / Internet ($):", "cable"),
        ]

        entries = {}
        for label_text, key in fields:
            ctk.CTkLabel(form, text=label_text, font=FONT_SMALL, text_color=curr["text_muted"]).pack(anchor="w")
            ent = ctk.CTkEntry(form, font=FONT_BODY)
            ent.pack(fill="x", pady=(2, 10))
            ent.insert(0, "0")
            entries[key] = ent

        ctk.CTkLabel(form, text="👥 Personas a dividir para este mes:", font=FONT_SMALL, text_color=curr["text_muted"]).pack(anchor="w")
        ent_personas = ctk.CTkEntry(form, font=FONT_BODY, width=80, justify="center")
        ent_personas.pack(anchor="w", pady=(2, 10))
        ent_personas.insert(0, "4")

        def save():
            mes_name = cb_mes.get().strip()
            mes_num = MESES_LISTA.index(mes_name) + 1

            try:
                g = float(entries["gas"].get().strip() or 0)
                a = float(entries["agua"].get().strip() or 0)
                l = float(entries["luz"].get().strip() or 0)
                c = float(entries["cable"].get().strip() or 0)
                p = max(1, int(ent_personas.get().strip() or 4))

                sin = g + a + c
                con = g + a + l + c

                self.db.add_service(
                    self.selected_year, mes_name, mes_num,
                    personas=p,
                    gas=g, gas_p=round(g / p, 2),
                    agua=a, agua_p=round(a / p, 2),
                    luz=l, luz_p=round(l / p, 2),
                    cable=c, cable_p=round(c / p, 2),
                    total_sin=sin, total_con=con
                )
                dialog.destroy()
                self.load_services()
                if self.on_data_changed:
                    self.on_data_changed()
            except ValueError:
                messagebox.showerror("Error", "Los valores ingresados deben ser numéricos.")

        ctk.CTkButton(dialog, text="Guardar Mes", fg_color=curr["success"], font=FONT_BODY_BOLD, command=save).pack(pady=15)

    def delete_selected_month(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Por favor selecciona un mes de la lista para eliminar.")
            return
        item = self.tree.item(selected[0])
        sid = item["values"][0]
        mes_name = item["values"][1]
        if messagebox.askyesno("Confirmar", f"¿Deseas eliminar los servicios de {mes_name} {self.selected_year}?"):
            self.db.conn.execute("DELETE FROM services WHERE id=?", (int(sid),))
            self.db.conn.commit()
            self.load_services()
            if self.on_data_changed:
                self.on_data_changed()

    def open_edit_service_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Por favor selecciona un mes de la lista para editar.")
            return

        item = self.tree.item(selected[0])
        sid = item["values"][0]

        row = self.db.conn.execute("SELECT * FROM services WHERE id=?", (sid,)).fetchone()
        if not row:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title(f"Editar Servicios - {row['mes']} {row['anio']}")
        dialog.geometry("420x570")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        curr = ThemeManager.get_current_theme()
        dialog.configure(fg_color=curr["bg_main"])

        ctk.CTkLabel(dialog, text=f"Servicios: {row['mes']} {row['anio']}", font=FONT_HEADER, text_color=curr["text_main"]).pack(pady=(15, 10))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=25, pady=5)

        fields = [
            ("Gas ($):", "gas", row["gas"]),
            ("Agua ($):", "agua", row["agua"]),
            ("Luz ($):", "luz", row["luz"]),
            ("Cable / Internet ($):", "cable", row["cable"]),
        ]

        entries = {}
        for label_text, key, val in fields:
            ctk.CTkLabel(form, text=label_text, font=FONT_SMALL, text_color=curr["text_muted"]).pack(anchor="w")
            ent = ctk.CTkEntry(form, font=FONT_BODY)
            ent.pack(fill="x", pady=(2, 10))
            ent.insert(0, str(val) if val > 0 else "0")
            entries[key] = ent

        # Personas specific to this month
        ctk.CTkLabel(form, text=f"👥 Personas a dividir en {row['mes']}:", font=FONT_SMALL, text_color=curr["text_muted"]).pack(anchor="w")
        ent_p = ctk.CTkEntry(form, font=FONT_BODY, width=80, justify="center")
        ent_p.pack(anchor="w", pady=(2, 10))
        current_p = row["personas"] if row["personas"] and row["personas"] > 0 else 4
        ent_p.insert(0, str(current_p))

        def save():
            try:
                g = float(entries["gas"].get().strip() or 0)
                a = float(entries["agua"].get().strip() or 0)
                l = float(entries["luz"].get().strip() or 0)
                c = float(entries["cable"].get().strip() or 0)
                p = max(1, int(ent_p.get().strip() or 4))
                sin = g + a + c
                con = g + a + l + c
                self.db.update_service(
                    sid,
                    gas=g, agua=a, luz=l, cable=c,
                    personas=p,
                    gas_prorrateo=round(g / p, 2),
                    agua_prorrateo=round(a / p, 2),
                    luz_prorrateo=round(l / p, 2),
                    cable_prorrateo=round(c / p, 2),
                    total_sin_luz=sin, total_con_luz=con
                )
                dialog.destroy()
                self.load_services()
                if self.on_data_changed:
                    self.on_data_changed()
            except ValueError:
                messagebox.showerror("Error", "Los valores ingresados deben ser numéricos.")

        ctk.CTkButton(dialog, text="Guardar Cambios", fg_color=curr["success"], font=FONT_BODY_BOLD, command=save).pack(pady=15)
