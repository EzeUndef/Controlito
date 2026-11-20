"""Settings and preferences view for Controlito."""
import os
import subprocess
import customtkinter as ctk
from tkinter import messagebox
from ui.theme import (
    ThemeManager, THEMES, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    COLOR_DANGER, BG_CARD, BG_MAIN, TEXT_MAIN, TEXT_MUTED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADER, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)
from utils.category_normalizer import normalize_database_categories


class SettingsView(ctk.CTkFrame):
    def __init__(self, parent, db, on_theme_change=None, on_import_excel=None, on_reset_onboarding=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_theme_change = on_theme_change
        self.on_import_excel = on_import_excel
        self.on_reset_onboarding = on_reset_onboarding

        self.build_ui()

    def build_ui(self):
        curr = ThemeManager.get_current_theme()

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 15))

        lbl_title = ctk.CTkLabel(
            header,
            text="⚙️ Configuración y Preferencias",
            font=FONT_TITLE,
            text_color=curr["text_main"]
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            header,
            text="Personaliza la apariencia corporativa, cotizaciones de divisas y administración de tus datos locales.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        )
        lbl_sub.pack(anchor="w")

        # Scrollable container
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        # --- SECCIÓN 1: APARIENCIA Y ESTILO EMPRESARIAL ---
        sec_theme = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=10)
        sec_theme.pack(fill="x", pady=(0, 15), padx=5)

        lbl_t_title = ctk.CTkLabel(sec_theme, text="🎨 Temas y Estética Empresarial", font=FONT_HEADER, text_color=curr["text_main"])
        lbl_t_title.pack(anchor="w", padx=20, pady=(15, 4))

        lbl_t_desc = ctk.CTkLabel(
            sec_theme,
            text="Elige el estilo visual corporativo. La tipografía estándar empresarial es Segoe UI / Segoe UI Semibold.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        )
        lbl_t_desc.pack(anchor="w", padx=20, pady=(0, 12))

        current_theme_name = self.db.get_setting("theme", ThemeManager._current_theme_name) if self.db else ThemeManager._current_theme_name

        # Grid of themes
        themes_grid = ctk.CTkFrame(sec_theme, fg_color="transparent")
        themes_grid.pack(fill="x", padx=15, pady=(0, 15))
        themes_grid.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for idx, (theme_name, t_data) in enumerate(THEMES.items()):
            row = idx // 4
            col = idx % 4
            is_active = (theme_name == current_theme_name)

            card = ctk.CTkFrame(
                themes_grid,
                fg_color=t_data["bg_main"],
                border_width=2 if is_active else 1,
                border_color=curr["primary"] if is_active else t_data["border"],
                corner_radius=8
            )
            card.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")

            btn = ctk.CTkButton(
                card,
                text=f"{'✓ ' if is_active else ''}{theme_name}",
                font=FONT_BODY_BOLD,
                height=38,
                fg_color="transparent",
                hover_color=t_data["bg_card"],
                text_color=t_data["text_main"],
                command=lambda name=theme_name: self._apply_theme(name)
            )
            btn.pack(fill="both", expand=True, padx=4, pady=4)

        # --- SECCIÓN 2: COTIZACIÓN PREFERIDA DEL DÓLAR ---
        sec_dolar = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=10)
        sec_dolar.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(sec_dolar, text="💵 Cotización Dólar Preferida para Ahorros", font=FONT_HEADER, text_color=curr["text_main"]).pack(anchor="w", padx=20, pady=(15, 4))
        ctk.CTkLabel(
            sec_dolar,
            text="Selecciona qué cotización en tiempo real se usará para convertir y calcular tus saldos en dólares a pesos:",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        ).pack(anchor="w", padx=20, pady=(0, 10))

        dolar_options = [
            ("blue", "Dólar Blue (Mercado Paralelo)"),
            ("bolsa", "Dólar MEP / Bolsa (Mercado de Capitales)"),
            ("oficial", "Dólar Oficial BNA (Banco de la Nación Argentina)"),
            ("tarjeta", "Dólar Tarjeta / Turista"),
            ("cripto", "Dólar Cripto (USDT / USDC)"),
            ("contadoconliqui", "Contado con Liquidación (CCL)")
        ]

        current_dolar = self.db.get_setting("dolar_rate_type", "blue") if self.db else "blue"
        self.dolar_var = ctk.StringVar(value=current_dolar)

        dolar_grid = ctk.CTkFrame(sec_dolar, fg_color="transparent")
        dolar_grid.pack(fill="x", padx=15, pady=(0, 15))
        dolar_grid.grid_columnconfigure((0, 1), weight=1)

        for idx, (key, label) in enumerate(dolar_options):
            row = idx // 2
            col = idx % 2
            rb = ctk.CTkRadioButton(
                dolar_grid,
                text=label,
                variable=self.dolar_var,
                value=key,
                font=FONT_BODY,
                text_color=curr["text_main"],
                command=lambda k=key: self._on_dolar_change(k)
            )
            rb.grid(row=row, column=col, padx=10, pady=6, sticky="w")

        # --- SECCIÓN 3: GESTIÓN DE BASE DE DATOS Y CATEGORÍAS ---
        sec_data = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=10)
        sec_data.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(sec_data, text="📂 Administración de Datos y Archivos", font=FONT_HEADER, text_color=curr["text_main"]).pack(anchor="w", padx=20, pady=(15, 4))
        ctk.CTkLabel(
            sec_data,
            text="Operaciones de respaldo, importación masiva y optimización de base de datos local SQLite.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        ).pack(anchor="w", padx=20, pady=(0, 12))

        btn_row = ctk.CTkFrame(sec_data, fg_color="transparent")
        btn_row.pack(fill="x", padx=20, pady=(0, 15))

        if self.on_import_excel:
            btn_imp = ctk.CTkButton(
                btn_row,
                text="📂 Importar Nuevo Excel",
                font=FONT_BODY_BOLD,
                height=36,
                fg_color=curr["primary"],
                hover_color=curr["primary_hover"],
                command=self.on_import_excel
            )
            btn_imp.pack(side="left", padx=(0, 10))

        btn_norm = ctk.CTkButton(
            btn_row,
            text="🪄 Unificar Sinónimos",
            font=FONT_BODY_BOLD,
            height=36,
            fg_color=curr.get("secondary", "#475569"),
            hover_color=curr["border"],
            command=self._normalize_categories
        )
        btn_norm.pack(side="left", padx=(0, 10))

        btn_open_folder = ctk.CTkButton(
            btn_row,
            text="📁 Abrir Carpeta de Datos",
            font=FONT_BODY_BOLD,
            height=36,
            fg_color="transparent",
            border_width=1,
            border_color=curr["border"],
            text_color=curr["text_main"],
            hover_color=curr["bg_main"],
            command=self._open_data_folder
        )
        btn_open_folder.pack(side="left", padx=(0, 10))

        if self.on_reset_onboarding:
            btn_reset = ctk.CTkButton(
                btn_row,
                text="⚠️ Reiniciar a Pantalla Inicial",
                font=FONT_BODY_BOLD,
                height=36,
                fg_color=curr["danger"],
                hover_color="#b91c1c",
                command=self.on_reset_onboarding
            )
            btn_reset.pack(side="right")

        # --- SECCIÓN 4: INFORMACIÓN DE SEGURIDAD & ENTERPRISE ---
        sec_info = ctk.CTkFrame(scroll, fg_color=curr["bg_card"], corner_radius=10)
        sec_info.pack(fill="x", pady=(0, 15), padx=5)

        ctk.CTkLabel(sec_info, text="🛡️ Información del Sistema y Licencia", font=FONT_HEADER, text_color=curr["text_main"]).pack(anchor="w", padx=20, pady=(15, 4))

        info_text = (
            "• Versión: Controlito v1.2.0 Empresarial\n"
            "• Privacidad: 100% Local. Toda la información financiera reside exclusivamente en tu equipo.\n"
            "• Motor de Datos: SQLite 3 con modo WAL (Write-Ahead Logging) de alto rendimiento.\n"
            "• Tipografía: Segoe UI / Segoe UI Semibold (Windows Fluent Enterprise Typography).\n"
            "• Licencia: Código Abierto (MIT License). Gratuito y auditable.\n"
            "• Repositorio Oficial: https://github.com/EzeUndef/Controlito"
        )
        lbl_info = ctk.CTkLabel(
            sec_info,
            text=info_text,
            font=FONT_BODY,
            text_color=curr["text_muted"],
            justify="left"
        )
        lbl_info.pack(anchor="w", padx=20, pady=(0, 15))

    def _apply_theme(self, name):
        ThemeManager.set_theme(name)
        if self.db:
            self.db.set_setting("theme", name)
        if self.on_theme_change:
            self.on_theme_change(name)

    def _on_dolar_change(self, val):
        if self.db:
            self.db.set_setting("dolar_rate_type", val)

    def _normalize_categories(self):
        if not self.db:
            return
        updated_count = normalize_database_categories(self.db)
        messagebox.showinfo(
            "Normalización de Categorías",
            f"Proceso completado con éxito.\nSe actualizaron {updated_count} movimientos a categorías canónicas sinónimas."
        )

    def _open_data_folder(self):
        try:
            folder = os.path.join(os.path.expanduser("~"), ".controlito")
            os.makedirs(folder, exist_ok=True)
            subprocess.run(f'explorer "{folder}"', shell=True)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir la carpeta de datos:\n{str(e)}")
