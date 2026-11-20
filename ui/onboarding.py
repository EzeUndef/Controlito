"""Onboarding / Welcome Screen for Controlito (Cargar Excel o Empezar de Cero)."""
import customtkinter as ctk
from tkinter import filedialog, messagebox
from utils.excel_importer import import_excel
from ui.theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS, BG_CARD,
    TEXT_MAIN, TEXT_MUTED, FONT_TITLE, FONT_HEADER, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)


class OnboardingView(ctk.CTkFrame):
    """First-time setup screen allowing users to either import Excel or start fresh from zero."""

    def __init__(self, parent, db, on_complete):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_complete = on_complete

        self.build_ui()

    def build_ui(self):
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # Welcome Logo & Title
        lbl_logo = ctk.CTkLabel(container, text="🏦 Controlito", font=("Segoe UI", 28, "bold"), text_color="#38bdf8")
        lbl_logo.pack(pady=(0, 4))

        lbl_sub = ctk.CTkLabel(
            container,
            text="Software de Finanzas Personales & Control de Gastos",
            font=FONT_BODY,
            text_color=TEXT_MUTED
        )
        lbl_sub.pack(pady=(0, 25))

        lbl_question = ctk.CTkLabel(
            container,
            text="¿Cómo deseas comenzar?",
            font=("Segoe UI", 16, "bold"),
            text_color=TEXT_MAIN
        )
        lbl_question.pack(pady=(0, 15))

        # Two Main Option Cards Side by Side
        cards_frame = ctk.CTkFrame(container, fg_color="transparent")
        cards_frame.pack(fill="x", pady=10)

        # CARD 1: Cargar Excel con datos
        card_excel = ctk.CTkFrame(cards_frame, fg_color=BG_CARD, corner_radius=14, width=320, height=260)
        card_excel.pack(side="left", padx=12, fill="both")
        card_excel.pack_propagate(False)

        ctk.CTkLabel(card_excel, text="📂", font=("Segoe UI", 36)).pack(pady=(20, 5))
        ctk.CTkLabel(card_excel, text="Cargar Excel con datos", font=FONT_HEADER, text_color=TEXT_MAIN).pack(pady=(0, 4))
        ctk.CTkLabel(
            card_excel,
            text="Si ya tienes una planilla de Excel con tus gastos históricos (o la plantilla de Controlito), impórtala automáticamente con un clic.",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            wraplength=280,
            justify="center"
        ).pack(padx=15, pady=(0, 15))

        btn_excel = ctk.CTkButton(
            card_excel,
            text="Seleccionar archivo Excel",
            font=FONT_BODY_BOLD,
            height=38,
            fg_color=COLOR_PRIMARY,
            hover_color=COLOR_PRIMARY_HOVER,
            command=self.choose_excel_file
        )
        btn_excel.pack(pady=(0, 15))

        # CARD 2: Arrancar de 0 (Base limpia)
        card_fresh = ctk.CTkFrame(cards_frame, fg_color=BG_CARD, corner_radius=14, width=320, height=260)
        card_fresh.pack(side="left", padx=12, fill="both")
        card_fresh.pack_propagate(False)

        ctk.CTkLabel(card_fresh, text="🚀", font=("Segoe UI", 36)).pack(pady=(20, 5))
        ctk.CTkLabel(card_fresh, text="Arrancar de 0 (Base limpia)", font=FONT_HEADER, text_color=TEXT_MAIN).pack(pady=(0, 4))
        ctk.CTkLabel(
            card_fresh,
            text="Inicia una contabilidad totalmente nueva y vacía, con las categorías preconfiguradas para registrar tus finanzas desde hoy.",
            font=FONT_SMALL,
            text_color=TEXT_MUTED,
            wraplength=280,
            justify="center"
        ).pack(padx=15, pady=(0, 15))

        btn_fresh = ctk.CTkButton(
            card_fresh,
            text="Comenzar desde cero",
            font=FONT_BODY_BOLD,
            height=38,
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            command=self.start_from_scratch
        )
        btn_fresh.pack(pady=(0, 15))

        # Bottom Helper info
        lbl_hint = ctk.CTkLabel(
            container,
            text="🔒 Tus datos se almacenan 100% de forma local en tu computadora y nunca salen de tu equipo.",
            font=FONT_SMALL,
            text_color="#64748b"
        )
        lbl_hint.pack(pady=(25, 0))

    def choose_excel_file(self):
        file_path = filedialog.askopenfilename(
            title="Seleccionar archivo Excel para Controlito",
            filetypes=[("Archivos Excel", "*.xlsx *.xls"), ("Todos los archivos", "*.*")]
        )
        if not file_path:
            return

        # Show modal progress dialog
        progress_dlg = ctk.CTkToplevel(self)
        progress_dlg.title("Importando Datos...")
        progress_dlg.geometry("420x160")
        progress_dlg.resizable(False, False)
        progress_dlg.transient(self)
        progress_dlg.grab_set()

        lbl_status = ctk.CTkLabel(progress_dlg, text="Procesando archivo...", font=FONT_BODY)
        lbl_status.pack(pady=(25, 10))

        bar = ctk.CTkProgressBar(progress_dlg, width=320)
        bar.pack(pady=5)
        bar.set(0)

        def progress_cb(pct, msg):
            bar.set(pct)
            lbl_status.configure(text=msg)
            progress_dlg.update()

        try:
            results = import_excel(self.db, file_path, progress_callback=progress_cb)
            progress_dlg.destroy()
            total_imported = sum(v for k, v in results.items() if isinstance(v, int))
            self.db.set_setting("onboarding_completed", "1")
            messagebox.showinfo("¡Importación Exitosa!", f"Se cargaron correctamente {total_imported} registros.")
            self.on_complete()
        except Exception as e:
            progress_dlg.destroy()
            messagebox.showerror("Error de importación", f"No se pudo procesar el archivo:\n{str(e)}")

    def start_from_scratch(self):
        # Clear existing data and seed clean default categories and services
        self.db.clear_all_data()

        # Seed basic standard categories
        default_cats = [
            ("Sueldo", "ingreso", "Ingresos"),
            ("Ingreso Extra", "ingreso", "Ingresos"),
            ("Alquiler", "gasto", "Vivienda"),
            ("Servicios", "gasto", "Vivienda"),
            ("Internet", "gasto", "Vivienda"),
            ("Supermercado", "gasto", "Alimentación"),
            ("Delivery", "gasto", "Alimentación"),
            ("Comida", "gasto", "Alimentación"),
            ("Transporte", "gasto", "Transporte"),
            ("Tarjeta de Crédito", "gasto", "Tarjetas"),
            ("Salidas y Hobbies", "gasto", "Entretenimiento"),
            ("Salud y Farmacia", "gasto", "Salud"),
            ("Gastos Varios", "gasto", "Otros"),
        ]
        for name, tipo, grupo in default_cats:
            self.db.add_category(name, tipo, grupo)

        # Initialize current year services
        from datetime import datetime
        self.db.add_services_year(datetime.now().year)

        # Mark onboarding as completed
        self.db.set_setting("onboarding_completed", "1")

        messagebox.showinfo(
            "Base Limpia Creada",
            "¡Listo! Se ha configurado una base de datos limpia.\nPuedes empezar a registrar tus gastos e ingresos ahora."
        )
        self.on_complete()
