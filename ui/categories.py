"""Categories CRUD management view for Controlito."""
import customtkinter as ctk
from tkinter import ttk, messagebox
import sqlite3
from utils.helpers import format_currency
from ui.theme import (
    ThemeManager, configure_treeview_style,
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS, COLOR_DANGER,
    COLOR_WARNING, BG_CARD, BG_MAIN, TEXT_MAIN, TEXT_MUTED,
    FONT_TITLE, FONT_HEADER, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)

PRESET_COLORS = [
    "#3b82f6", "#10b981", "#f43f5e", "#f59e0b", "#8b5cf6",
    "#06b6d4", "#ec4899", "#14b8a6", "#6366f1", "#84cc16",
    "#e11d48", "#d97706", "#64748b"
]


class CategoriesView(ctk.CTkFrame):
    def __init__(self, parent, db, on_data_changed=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_data_changed = on_data_changed

        self.build_ui()
        self.load_categories()

    def build_ui(self):
        from ui.theme import ThemeManager
        curr = ThemeManager.get_current_theme()

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        title = ctk.CTkLabel(title_box, text="🏷️ Gestión de Categorías", font=FONT_TITLE, text_color=TEXT_MAIN)
        title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box,
            text="Administra, crea, edita y clasifica tus gastos e ingresos.",
            font=FONT_SMALL,
            text_color=TEXT_MUTED
        )
        lbl_sub.pack(anchor="w")

        # Action buttons in header
        btn_box = ctk.CTkFrame(header, fg_color="transparent")
        btn_box.pack(side="right")

        btn_new = ctk.CTkButton(
            btn_box,
            text="+ Nueva Categoría",
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            font=FONT_BODY_BOLD,
            command=self.open_add_dialog
        )
        btn_new.pack(side="right", padx=(4, 0))

        btn_normalize = ctk.CTkButton(
            btn_box,
            text="🪄 Unificar Sinónimos",
            fg_color="#334155",
            hover_color="#475569",
            font=FONT_BODY_BOLD,
            command=self.confirm_normalize_categories
        )
        btn_normalize.pack(side="right", padx=4)

        # Filters toolbar
        toolbar = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=10)
        toolbar.pack(fill="x", padx=20, pady=(0, 10))

        self.search_entry = ctk.CTkEntry(
            toolbar,
            placeholder_text="🔍 Buscar categoría o grupo...",
            width=260,
            font=FONT_BODY
        )
        self.search_entry.pack(side="left", padx=12, pady=10)
        self.search_entry.bind("<Return>", lambda e: self.load_categories())
        self.search_entry.bind("<KeyRelease>", lambda e: self.load_categories())

        ctk.CTkLabel(toolbar, text="Grupo:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left", padx=(10, 2))
        groups = ["Todos"] + self.db.get_category_groups()
        self.cb_group = ctk.CTkComboBox(toolbar, values=groups, width=150, command=lambda _: self.load_categories())
        self.cb_group.set("Todos")
        self.cb_group.pack(side="left", padx=5)

        btn_refresh = ctk.CTkButton(toolbar, text="Actualizar", width=80, command=self.load_categories, fg_color=COLOR_PRIMARY)
        btn_refresh.pack(side="left", padx=6)

        # Categories Table Frame
        configure_treeview_style(curr)
        table_frame = ctk.CTkFrame(self, fg_color=curr["bg_card"], corner_radius=12, border_width=1, border_color=curr["border"])
        table_frame.pack(fill="both", expand=True, padx=20, pady=5)

        cols = ("id", "nombre", "tipo", "grupo", "color", "trans_count", "total_gasto", "total_ingreso")
        self.tree = ttk.Treeview(
            table_frame,
            columns=cols,
            show="headings",
            style="Custom.Treeview",
            selectmode="browse"
        )

        self.tree.heading("id", text="#")
        self.tree.heading("nombre", text="🏷️ Categoría")
        self.tree.heading("tipo", text="Tipo")
        self.tree.heading("grupo", text="📁 Grupo / Rubro")
        self.tree.heading("color", text="Color")
        self.tree.heading("trans_count", text="📊 Movimientos")
        self.tree.heading("total_gasto", text="Total Gastado")
        self.tree.heading("total_ingreso", text="Total Ingresado")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("nombre", width=180, anchor="w")
        self.tree.column("tipo", width=95, anchor="center")
        self.tree.column("grupo", width=140, anchor="w")
        self.tree.column("color", width=90, anchor="center")
        self.tree.column("trans_count", width=105, anchor="center")
        self.tree.column("total_gasto", width=125, anchor="e")
        self.tree.column("total_ingreso", width=125, anchor="e")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side="left", fill="both", expand=True, padx=(8, 0), pady=8)
        scrollbar.pack(side="right", fill="y", padx=(0, 8), pady=8)

        # Double click to edit selected category
        self.tree.bind("<Double-1>", lambda e: self.open_edit_dialog())

        # Zebra striping
        self.tree.tag_configure("evenrow", background=curr["bg_card"])
        self.tree.tag_configure("oddrow", background=curr.get("bg_card_alt", curr["bg_main"]))

        # Context action buttons (Edit, Delete)
        bottom_bar = ctk.CTkFrame(self, fg_color="transparent")
        bottom_bar.pack(fill="x", padx=20, pady=(5, 15))

        btn_edit = ctk.CTkButton(
            bottom_bar,
            text="✏️ Editar Categoría",
            width=140,
            command=self.open_edit_dialog,
            fg_color="#475569"
        )
        btn_edit.pack(side="left", padx=5)

        btn_del = ctk.CTkButton(
            bottom_bar,
            text="🗑️ Eliminar Categoría",
            width=140,
            command=self.delete_selected,
            fg_color=COLOR_DANGER,
            hover_color="#b91c1c"
        )
        btn_del.pack(side="left", padx=5)

        self.lbl_stats = ctk.CTkLabel(bottom_bar, text="", font=FONT_SMALL, text_color=TEXT_MUTED)
        self.lbl_stats.pack(side="right", padx=10)

    def load_categories(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        search = self.search_entry.get().strip() or None
        group = self.cb_group.get()
        if group == "Todos":
            group = None

        rows = self.db.get_categories_with_stats(search=search, grupo=group)

        tipo_display = {
            "gasto": "🔴 Gasto",
            "ingreso": "🟢 Ingreso",
            "ambos": "🔄 Ambos"
        }

        for idx, r in enumerate(rows):
            t_str = tipo_display.get(r["tipo"], r["tipo"])
            gasto_str = format_currency(r["total_gasto"]) if r["total_gasto"] > 0 else "-"
            ingreso_str = format_currency(r["total_ingreso"]) if r["total_ingreso"] > 0 else "-"
            tag = "evenrow" if (idx % 2 == 0) else "oddrow"
            self.tree.insert("", "end", values=(
                r["id"],
                r["nombre"],
                t_str,
                r["grupo"],
                r["color"],
                f"{r['trans_count']:,}",
                gasto_str,
                ingreso_str
            ), tags=(tag,))

        self.lbl_stats.configure(text=f"Total: {len(rows)} categorías registradas")

    def confirm_normalize_categories(self):
        msg = (
            "¿Deseas unificar sinónimos y estandarizar las categorías?\n\n"
            "• Agrupará variantes como 'TC', 'Tarjeta Visa/Master' en 'Tarjetas de Crédito'.\n"
            "• Unificará 'Comida', 'Delivery', 'Super' en 'Supermercado & Alimentos'.\n"
            "• Consolidará 'Salud & Psicología', 'Salidas & Ocio', etc.\n"
            "• Las transacciones existentes se reasignarán a la categoría canónica correspondiente."
        )
        if messagebox.askyesno("Estandarizar Categorías", msg):
            tx_updated, cat_count = self.db.normalize_categories()
            self.load_categories()
            # Update filter dropdown
            updated_groups = ["Todos"] + self.db.get_category_groups()
            self.cb_group.configure(values=updated_groups)
            messagebox.showinfo(
                "Categorías Estandarizadas",
                f"✅ Se consolidaron las categorías en {cat_count} categorías canónicas limpias.\n"
                f"Se actualizaron {tx_updated} transacciones con sus sinónimos unificados."
            )
            if self.on_data_changed:
                self.on_data_changed()

    def open_add_dialog(self):
        self._open_category_dialog(title="Nueva Categoría")

    def open_edit_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Por favor selecciona una categoría de la tabla para editar.")
            return

        item = self.tree.item(selected[0])
        cid = item["values"][0]

        cat = self.db.get_category_by_id(cid)
        if cat:
            self._open_category_dialog(title="Editar Categoría", record=cat)

    def _open_category_dialog(self, title, record=None):
        dialog = ctk.CTkToplevel(self)
        dialog.title(title)
        dialog.geometry("420x460")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        # Center dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - 210
        y = self.winfo_rooty() + (self.winfo_height() // 2) - 230
        dialog.geometry(f"+{x}+{y}")

        ctk.CTkLabel(dialog, text=title, font=FONT_HEADER, text_color=TEXT_MAIN).pack(pady=(15, 10))

        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=25, pady=5)

        # Nombre
        ctk.CTkLabel(form, text="Nombre de la Categoría:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ent_nombre = ctk.CTkEntry(form, font=FONT_BODY)
        ent_nombre.pack(fill="x", pady=(2, 10))
        if record:
            ent_nombre.insert(0, record["nombre"])

        # Tipo
        ctk.CTkLabel(form, text="Tipo de Movimiento:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        cb_tipo = ctk.CTkComboBox(form, values=["ambos", "gasto", "ingreso"], font=FONT_BODY)
        cb_tipo.pack(fill="x", pady=(2, 10))
        cb_tipo.set(record["tipo"] if record else "ambos")

        # Grupo / Rubro
        ctk.CTkLabel(form, text="Grupo / Rubro:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        available_groups = self.db.get_category_groups()
        cb_grupo = ctk.CTkComboBox(form, values=available_groups, font=FONT_BODY)
        cb_grupo.pack(fill="x", pady=(2, 10))
        cb_grupo.set(record["grupo"] if record else (available_groups[0] if available_groups else "General"))

        # Color
        ctk.CTkLabel(form, text="Color identificador:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        color_frame = ctk.CTkFrame(form, fg_color="transparent")
        color_frame.pack(fill="x", pady=(2, 10))

        selected_color = ctk.StringVar(value=record["color"] if record else PRESET_COLORS[0])
        ent_color = ctk.CTkEntry(color_frame, textvariable=selected_color, width=90, font=FONT_BODY)
        ent_color.pack(side="left", padx=(0, 10))

        color_preview = ctk.CTkFrame(color_frame, width=28, height=28, fg_color=selected_color.get(), corner_radius=6)
        color_preview.pack(side="left")

        def update_preview(*_):
            try:
                c = selected_color.get().strip()
                if c.startswith("#") and len(c) in (4, 7):
                    color_preview.configure(fg_color=c)
            except Exception:
                pass

        selected_color.trace_add("write", update_preview)

        # Color swatches
        swatches_frame = ctk.CTkFrame(form, fg_color="transparent")
        swatches_frame.pack(fill="x", pady=(0, 15))
        for hex_col in PRESET_COLORS[:8]:
            btn_col = ctk.CTkButton(
                swatches_frame,
                text="",
                width=24,
                height=24,
                fg_color=hex_col,
                hover_color=hex_col,
                corner_radius=4,
                command=lambda c=hex_col: selected_color.set(c)
            )
            btn_col.pack(side="left", padx=2)

        def save():
            nom = ent_nombre.get().strip()
            if not nom:
                messagebox.showerror("Error", "Debes ingresar un nombre para la categoría.")
                return

            tip = cb_tipo.get().strip()
            grp = cb_grupo.get().strip() or "General"
            col = selected_color.get().strip() or "#3498db"

            try:
                if record:
                    self.db.update_category(record["id"], nom, tip, grp, col, sync_transactions=True)
                else:
                    self.db.add_category(nom, tip, grp, col)

                dialog.destroy()
                self.load_categories()
                # Update groups filter in case a new group was added
                updated_groups = ["Todos"] + self.db.get_category_groups()
                self.cb_group.configure(values=updated_groups)

                if self.on_data_changed:
                    self.on_data_changed()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", f"Ya existe una categoría llamada '{nom}'.")
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar: {str(e)}")

        btn_save = ctk.CTkButton(
            dialog,
            text="Guardar Categoría",
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            font=FONT_BODY_BOLD,
            command=save
        )
        btn_save.pack(pady=15)

    def delete_selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Atención", "Por favor selecciona una categoría de la tabla para eliminar.")
            return

        item = self.tree.item(selected[0])
        cid = item["values"][0]
        nombre = item["values"][1]
        movs = item["values"][5]

        msg = (
            f"¿Estás seguro de eliminar la categoría '{nombre}'?\n\n"
            f"Tiene {movs} movimiento(s) asociado(s).\n"
            "Los movimientos no se borrarán: pasarán a llamarse 'Sin categoría'."
        )
        if messagebox.askyesno("Confirmar Eliminación", msg):
            self.db.delete_category(cid, reassign_to="Sin categoría")
            self.load_categories()
            if self.on_data_changed:
                self.on_data_changed()
