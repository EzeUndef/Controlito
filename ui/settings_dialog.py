"""Settings and preferences modal dialog for Controlito."""
import customtkinter as ctk
from tkinter import messagebox
from ui.theme import (
    ThemeManager, THEMES, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    COLOR_DANGER, BG_CARD, BG_MAIN, TEXT_MAIN, TEXT_MUTED,
    FONT_TITLE, FONT_HEADER, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)


class SettingsDialog(ctk.CTkToplevel):
    def __init__(self, parent, db, on_theme_change=None, on_import_excel=None, on_reset_onboarding=None):
        super().__init__(parent)
        self.db = db
        self.on_theme_change = on_theme_change
        self.on_import_excel = on_import_excel
        self.on_reset_onboarding = on_reset_onboarding

        self.title("⚙️ Configuración y Ajustes — Controlito")
        self.geometry("560x600")
        self.minsize(500, 520)
        self.transient(parent)
        self.grab_set()

        # Center
        self.update_idletasks()
        x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 280
        y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 300
        self.geometry(f"+{max(10, x)}+{max(10, y)}")

        self.build_ui()

    def build_ui(self):
        curr = ThemeManager.get_current_theme()
        self.configure(fg_color=curr["bg_main"])

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 15))

        ctk.CTkLabel(header, text="⚙️ Configuración del Sistema", font=FONT_TITLE, text_color=curr["text_main"]).pack(anchor="w")
        ctk.CTkLabel(
            header,
            text="Personaliza la apariencia, cotizaciones y opciones de tus datos locales.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        ).pack(anchor="w")

        # Scrollable container for settings options
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=(0, 15))

        # --- SECCIÓN 1: TEMAS VISUALES ---
        sec_theme = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=12)
        sec_theme.pack(fill="x", pady=8, padx=5)

        lbl_t_title = ctk.CTkLabel(sec_theme, text="🎨 Temas Visuales y Estética", font=FONT_HEADER, text_color=curr["text_main"])
        lbl_t_title.pack(anchor="w", padx=15, pady=(12, 4))

        lbl_t_desc = ctk.CTkLabel(
            sec_theme,
            text="Selecciona el estilo visual con tipografía Bahnschrift que mejor se adapte a tu gusto:",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        )
        lbl_t_desc.pack(anchor="w", padx=15, pady=(0, 10))

        # Grid of theme buttons
        current_theme_name = self.db.get_setting("theme", ThemeManager._current_theme_name)
        themes_grid = ctk.CTkFrame(sec_theme, fg_color="transparent")
        themes_grid.pack(fill="x", padx=12, pady=(0, 12))
        themes_grid.grid_columnconfigure((0, 1), weight=1)

        for idx, (theme_name, t_data) in enumerate(THEMES.items()):
            row = idx // 2
            col = idx % 2

            card_border = curr["primary"] if theme_name == current_theme_name else curr["border"]
            btn_t = ctk.CTkButton(
                themes_grid,
                text=theme_name,
                font=FONT_BODY_BOLD,
                height=38,
                fg_color=t_data["bg_main"],
                hover_color=t_data["border"],
                border_width=2 if theme_name == current_theme_name else 1,
                border_color=card_border,
                text_color=t_data["text_main"],
                command=lambda name=theme_name: self._apply_theme(name)
            )
            btn_t.grid(row=row, column=col, padx=4, pady=4, sticky="ew")

        # --- SECCIÓN 2: COTIZACIÓN PREFERIDA DEL DÓLAR ---
        sec_dolar = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=12)
        sec_dolar.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(sec_dolar, text="💵 Cotización Dólar Preferida", font=FONT_HEADER, text_color=curr["text_main"]).pack(anchor="w", padx=15, pady=(12, 4))
        ctk.CTkLabel(
            sec_dolar,
            text="Elige qué cotización se usará por defecto para convertir tus ahorros USD a Pesos:",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        ).pack(anchor="w", padx=15, pady=(0, 8))

        dolar_options = [
            ("blue", "Dólar Blue (Paralelo)"),
            ("bolsa", "Dólar MEP / Bolsa"),
            ("oficial", "Dólar Oficial BNA"),
            ("tarjeta", "Dólar Tarjeta"),
            ("cripto", "Dólar Cripto"),
            ("contadoconliqui", "Contado con Liqui (CCL)")
        ]

        current_dolar = self.db.get_setting("dolar_rate_type", "blue")
        self.dolar_var = ctk.StringVar(value=current_dolar)

        for key, label in dolar_options:
            rb = ctk.CTkRadioButton(
                sec_dolar,
                text=label,
                variable=self.dolar_var,
                value=key,
                font=FONT_BODY,
                command=lambda k=key: self._on_dolar_change(k)
            )
            rb.pack(anchor="w", padx=20, pady=3)

        ctk.CTkLabel(sec_dolar, text="", height=4).pack()

        # --- SECCIÓN 3: GESTIÓN DE DATOS ---
        sec_data = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=12)
        sec_data.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(sec_data, text="📂 Base de Datos y Archivos", font=FONT_HEADER, text_color=curr["text_main"]).pack(anchor="w", padx=15, pady=(12, 4))

        data_row = ctk.CTkFrame(sec_data, fg_color="transparent")
        data_row.pack(fill="x", padx=15, pady=(4, 12))

        if self.on_import_excel:
            btn_imp = ctk.CTkButton(
                data_row,
                text="📂 Importar Nuevo Excel",
                font=FONT_BODY_BOLD,
                fg_color=COLOR_PRIMARY,
                command=lambda: [self.destroy(), self.on_import_excel()]
            )
            btn_imp.pack(side="left", padx=(0, 8))

        if self.on_reset_onboarding:
            btn_reset = ctk.CTkButton(
                data_row,
                text="🔄 Reiniciar / Arrancar de 0",
                font=FONT_BODY_BOLD,
                fg_color="#475569",
                hover_color=COLOR_DANGER,
                command=lambda: [self.destroy(), self.on_reset_onboarding()]
            )
            btn_reset.pack(side="left", padx=4)

        # --- SECCIÓN 4: SEGURIDAD OPEN SOURCE ---
        sec_sec = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=12)
        sec_sec.pack(fill="x", pady=8, padx=5)

        ctk.CTkLabel(sec_sec, text="🔒 Seguridad y Privacidad Open Source", font=FONT_HEADER, text_color=curr["text_main"]).pack(anchor="w", padx=15, pady=(12, 4))
        info_security = (
            "• Almacenamiento 100% Offline y Local en SQLite.\n"
            "• Prevención de SQL Injection mediante consultas parametrizadas.\n"
            "• Sin telemetría ni rastreo de tus gastos ni finanzas.\n"
            "• Los archivos de Excel originales nunca se modifican directamente."
        )
        ctk.CTkLabel(
            sec_sec,
            text=info_security,
            font=FONT_SMALL,
            text_color=curr["text_muted"],
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 12))

        # Bottom Close button
        btn_close = ctk.CTkButton(
            self,
            text="Listo / Cerrar",
            font=FONT_BODY_BOLD,
            fg_color=COLOR_SUCCESS,
            hover_color="#059669",
            width=120,
            command=self.destroy
        )
        btn_close.pack(pady=10)

    def _apply_theme(self, name):
        ThemeManager.set_theme(name)
        self.db.set_setting("theme", name)
        if self.on_theme_change:
            self.on_theme_change(name)
        self.destroy()

    def _on_dolar_change(self, key):
        self.db.set_setting("dolar_rate_type", key)
