"""Sidebar navigation menu for Controlito."""
import customtkinter as ctk
from ui.theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, BG_SIDEBAR, TEXT_MAIN, TEXT_MUTED,
    FONT_TITLE, FONT_BODY_BOLD, FONT_SMALL
)
from ui.settings_dialog import SettingsDialog


class Sidebar(ctk.CTkFrame):
    def __init__(self, parent, on_navigate, on_import_excel=None, on_toggle_mode=None, on_theme_change=None, initial_theme=None, on_reset_onboarding=None, db=None):
        super().__init__(parent, fg_color=BG_SIDEBAR, width=220, corner_radius=0)
        self.on_navigate = on_navigate
        self.on_import_excel = on_import_excel
        self.on_toggle_mode = on_toggle_mode
        self.on_theme_change = on_theme_change
        self.initial_theme = initial_theme or "🌊 Midnight Blue"
        self.on_reset_onboarding = on_reset_onboarding
        self.db = db
        self.buttons = {}
        self.active_tab = "dashboard"

        self.build_ui()

    def build_ui(self):
        from ui.theme import ThemeManager
        curr = ThemeManager.get_current_theme()

        # App branding header
        brand_frame = ctk.CTkFrame(self, fg_color="transparent")
        brand_frame.pack(fill="x", padx=15, pady=(20, 15))

        lbl_logo = ctk.CTkLabel(brand_frame, text="🏦 Controlito", font=FONT_TITLE, text_color=curr.get("primary", "#6366f1"))
        lbl_logo.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(brand_frame, text="Gestión Financiera v1.2", font=FONT_SMALL, text_color=TEXT_MUTED)
        lbl_sub.pack(anchor="w")

        # Mode Selector (Modo Simple vs Modo Data)
        lbl_mode = ctk.CTkLabel(self, text="EXPERIENCIA:", font=("Segoe UI", 9, "bold"), text_color=TEXT_MUTED)
        lbl_mode.pack(anchor="w", padx=15, pady=(0, 2))

        self.mode_var = ctk.StringVar(value="📊 Modo Data")
        self.mode_seg = ctk.CTkSegmentedButton(
            self,
            values=["💬 Simple", "📊 Data"],
            variable=self.mode_var,
            font=FONT_SMALL,
            command=self._on_mode_change
        )
        self.mode_seg.set("📊 Data")
        self.mode_seg.pack(fill="x", padx=12, pady=(0, 15))

        # Navigation menu items (including new Categories CRUD)
        nav_items = [
            ("chat", "💬 Chat Asistente"),
            ("dashboard", "📊 Dashboard"),
            ("transactions", "💰 Movimientos"),
            ("categories", "🏷️ Categorías"),
            ("services", "⚡ Servicios"),
            ("bank_accounts", "🏦 Bancos & Ahorros"),
            ("budget", "📋 Presupuesto"),
            ("advisor", "🧠 Asesor & Detective"),
        ]

        for key, label in nav_items:
            btn = ctk.CTkButton(
                self,
                text=label,
                anchor="w",
                font=FONT_BODY_BOLD,
                height=38,
                corner_radius=8,
                fg_color=curr["primary"] if key == self.active_tab else "transparent",
                text_color=curr["text_main"] if key == self.active_tab else curr["text_muted"],
                hover_color=curr["primary_hover"],
                command=lambda k=key: self.select_tab(k)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.buttons[key] = btn

        # Spacer to push bottom utilities down
        spacer = ctk.CTkFrame(self, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # Settings and Utilities section at the bottom
        bottom_frame = ctk.CTkFrame(self, fg_color="transparent")
        bottom_frame.pack(fill="x", padx=12, pady=(5, 15))

        # Settings button that opens the dedicated Settings modal
        btn_settings = ctk.CTkButton(
            bottom_frame,
            text="⚙️ Configuración / Ajustes",
            font=FONT_BODY_BOLD,
            height=36,
            corner_radius=8,
            fg_color=curr["bg_card"],
            hover_color=curr["border"],
            text_color=curr["text_main"],
            command=self.open_settings_dialog
        )
        btn_settings.pack(fill="x", pady=(0, 8))

        # Quick Theme Selector in Sidebar
        theme_box = ctk.CTkFrame(bottom_frame, fg_color=curr["bg_card"], corner_radius=8)
        theme_box.pack(fill="x", pady=(0, 8))

        lbl_theme = ctk.CTkLabel(theme_box, text="🎨 Tema:", font=("Segoe UI", 9, "bold"), text_color=curr["text_muted"])
        lbl_theme.pack(anchor="w", padx=10, pady=(6, 2))

        self.cb_theme = ctk.CTkComboBox(
            theme_box,
            values=ThemeManager.get_theme_names(),
            font=FONT_SMALL,
            height=28,
            command=self._on_theme_selected
        )
        self.cb_theme.set(self.initial_theme)
        self.cb_theme.pack(fill="x", padx=8, pady=(0, 8))

        # Open Source Privacy badge
        lbl_sec = ctk.CTkLabel(
            bottom_frame,
            text="🔒 100% Local & Open Source",
            font=("Segoe UI", 9),
            text_color=curr["text_muted"],
            justify="center"
        )
        lbl_sec.pack(pady=(2, 0))

    def open_settings_dialog(self):
        if not self.db:
            return
        SettingsDialog(
            self.winfo_toplevel(),
            self.db,
            on_theme_change=self.on_theme_change,
            on_import_excel=self.on_import_excel,
            on_reset_onboarding=self.on_reset_onboarding
        )

    def _on_theme_selected(self, val):
        from ui.theme import ThemeManager
        ThemeManager.set_theme(val)
        if self.db:
            self.db.set_setting("theme", val)
        if self.on_theme_change:
            self.on_theme_change(val)

    def _on_mode_change(self, val):
        if self.on_toggle_mode:
            mode = "simple" if "Simple" in val else "data"
            self.on_toggle_mode(mode)

    def select_tab(self, key):
        self.active_tab = key
        from ui.theme import ThemeManager
        curr = ThemeManager.get_current_theme()
        for k, btn in self.buttons.items():
            if k == key:
                btn.configure(fg_color=curr["primary"], text_color=curr["text_main"])
            else:
                btn.configure(fg_color="transparent", text_color=curr["text_muted"])
        self.on_navigate(key)
