"""Theme and styling configuration for Controlito UI with Corporate Enterprise Aesthetics & Segoe UI Typography."""
import tkinter as tk
from tkinter import ttk

THEMES = {
    "💼 Corporate Slate": {
        "name": "💼 Corporate Slate",
        "primary": "#2563eb",         # Modern Enterprise Blue
        "primary_hover": "#1d4ed8",
        "secondary": "#475569",       # Slate Gray
        "success": "#059669",         # Corporate Emerald
        "danger": "#dc2626",          # Refined Crimson
        "warning": "#d97706",         # Executive Amber
        "purple": "#7c3aed",
        "bg_sidebar": "#0b1120",      # Deep Slate 950
        "bg_main": "#0f172a",         # Slate 900
        "bg_card": "#1e293b",         # Slate 800 Card
        "bg_card_alt": "#172033",     # Slate Row Alt
        "bg_input": "#0b1120",
        "border": "#334155",
        "text_main": "#f8fafc",
        "text_muted": "#94a3b8",
        "text_accent": "#38bdf8",
        "chart_bg": "#1e293b",
        "chart_palette": ["#2563eb", "#059669", "#dc2626", "#d97706", "#7c3aed", "#0891b2"]
    },
    "🏛️ Executive Charcoal": {
        "name": "🏛️ Executive Charcoal",
        "primary": "#3b82f6",         # Cobalt Blue
        "primary_hover": "#2563eb",
        "secondary": "#52525b",       # Zinc Gray
        "success": "#10b981",         # Emerald
        "danger": "#ef4444",          # Ruby
        "warning": "#f59e0b",         # Amber
        "purple": "#8b5cf6",
        "bg_sidebar": "#101114",      # Dark Charcoal
        "bg_main": "#16171c",         # Deep Graphite
        "bg_card": "#21222a",         # Fine Charcoal Card
        "bg_card_alt": "#1a1b22",     # Subtle Alt Row
        "bg_input": "#101114",
        "border": "#2c2e39",
        "text_main": "#f4f4f5",
        "text_muted": "#a1a1aa",
        "text_accent": "#60a5fa",
        "chart_bg": "#21222a",
        "chart_palette": ["#3b82f6", "#10b981", "#ef4444", "#f59e0b", "#8b5cf6", "#06b6d4"]
    },
    "🌊 Midnight Navy": {
        "name": "🌊 Midnight Navy",
        "primary": "#0284c7",         # Sky Blue Enterprise
        "primary_hover": "#0369a1",
        "secondary": "#334155",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "purple": "#6366f1",
        "bg_sidebar": "#080e1a",      # Pure Navy Abyss
        "bg_main": "#0d1527",         # Midnight Blue
        "bg_card": "#16233d",         # Deep Navy Card
        "bg_card_alt": "#111b2f",
        "bg_input": "#080e1a",
        "border": "#223558",
        "text_main": "#f0f9ff",
        "text_muted": "#8ec1dc",
        "text_accent": "#38bdf8",
        "chart_bg": "#16233d",
        "chart_palette": ["#0284c7", "#10b981", "#ef4444", "#f59e0b", "#6366f1", "#38bdf8"]
    },
    "🌲 Nordic Enterprise": {
        "name": "🌲 Nordic Enterprise",
        "primary": "#059669",         # Emerald Green
        "primary_hover": "#047857",
        "secondary": "#2d6a4f",
        "success": "#10b981",
        "danger": "#e11d48",
        "warning": "#d97706",
        "purple": "#52b788",
        "bg_sidebar": "#06130d",      # Pine Charcoal
        "bg_main": "#0b1e15",         # Nordic Slate
        "bg_card": "#132d20",         # Forest Card
        "bg_card_alt": "#0e2319",
        "bg_input": "#06130d",
        "border": "#1e4331",
        "text_main": "#ecfdf5",
        "text_muted": "#86efac",
        "text_accent": "#34d399",
        "chart_bg": "#132d20",
        "chart_palette": ["#059669", "#34d399", "#d97706", "#e11d48", "#10b981", "#6ee7b7"]
    },
    "💎 Obsidian Tech": {
        "name": "💎 Obsidian Tech",
        "primary": "#6366f1",         # Electric Indigo
        "primary_hover": "#4f46e5",
        "secondary": "#475569",
        "success": "#10b981",
        "danger": "#f43f5e",
        "warning": "#f59e0b",
        "purple": "#8b5cf6",
        "bg_sidebar": "#070a12",      # Pure Midnight
        "bg_main": "#0b0f19",         # Deep Obsidian
        "bg_card": "#131b2c",         # Slate Glass Card
        "bg_card_alt": "#0d1422",
        "bg_input": "#080c14",
        "border": "#1e293d",
        "text_main": "#f8fafc",
        "text_muted": "#94a3b8",
        "text_accent": "#38bdf8",
        "chart_bg": "#131b2c",
        "chart_palette": ["#6366f1", "#10b981", "#f43f5e", "#f59e0b", "#06b6d4", "#8b5cf6"]
    },
    "☕ Warm Executive": {
        "name": "☕ Warm Executive",
        "primary": "#b45309",         # Warm Amber Bronze
        "primary_hover": "#92400e",
        "secondary": "#78350f",
        "success": "#059669",
        "danger": "#b91c1c",
        "warning": "#d97706",
        "purple": "#c2410c",
        "bg_sidebar": "#120f0d",      # Roasted Slate
        "bg_main": "#1a1614",         # Executive Coffee
        "bg_card": "#26201c",         # Warm Card
        "bg_card_alt": "#1f1a16",
        "bg_input": "#100d0b",
        "border": "#3d332c",
        "text_main": "#fef3c7",
        "text_muted": "#d4b89e",
        "text_accent": "#f59e0b",
        "chart_bg": "#26201c",
        "chart_palette": ["#b45309", "#d97706", "#059669", "#b91c1c", "#f59e0b", "#78350f"]
    },
    "❄️ Arctic Corporate": {
        "name": "❄️ Arctic Corporate",
        "primary": "#0891b2",         # Cyan Enterprise
        "primary_hover": "#0e7490",
        "secondary": "#475569",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "purple": "#6366f1",
        "bg_sidebar": "#090d16",
        "bg_main": "#0f172a",
        "bg_card": "#182238",         # Titanium Slate
        "bg_card_alt": "#121b2d",
        "bg_input": "#0a101c",
        "border": "#233352",
        "text_main": "#f0f9ff",
        "text_muted": "#8ec1dc",
        "text_accent": "#06b6d4",
        "chart_bg": "#182238",
        "chart_palette": ["#0891b2", "#06b6d4", "#10b981", "#6366f1", "#ef4444", "#f59e0b"]
    },
    "🏢 Office Steel": {
        "name": "🏢 Office Steel",
        "primary": "#3b82f6",         # Steel Blue
        "primary_hover": "#1d4ed8",
        "secondary": "#64748b",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "purple": "#8b5cf6",
        "bg_sidebar": "#111827",      # Cool Gray 900
        "bg_main": "#1f2937",         # Cool Gray 800
        "bg_card": "#374151",         # Cool Gray 700
        "bg_card_alt": "#2c3543",
        "bg_input": "#111827",
        "border": "#4b5563",
        "text_main": "#f9fafb",
        "text_muted": "#9ca3af",
        "text_accent": "#60a5fa",
        "chart_bg": "#374151",
        "chart_palette": ["#3b82f6", "#10b981", "#ef4444", "#f59e0b", "#8b5cf6", "#64748b"]
    }
}


def configure_treeview_style(theme=None):
    """Configures high-end corporate styling for all ttk.Treeview tables in the app."""
    if theme is None:
        theme = ThemeManager.get_current_theme()

    style = ttk.Style()
    # Force 'clam' theme which reliably supports complete custom coloring on Windows
    try:
        style.theme_use("clam")
    except Exception:
        pass

    bg_card = theme.get("bg_card", "#1e293b")
    bg_alt = theme.get("bg_card_alt", "#172033")
    primary = theme.get("primary", "#2563eb")
    text_main = theme.get("text_main", "#f8fafc")
    text_muted = theme.get("text_muted", "#94a3b8")
    header_bg = theme.get("bg_sidebar", "#0b1120")
    border_col = theme.get("border", "#334155")

    # Base Treeview styling
    style.configure(
        "Custom.Treeview",
        background=bg_card,
        foreground=text_main,
        rowheight=32,
        fieldbackground=bg_card,
        borderwidth=0,
        relief="flat",
        font=("Segoe UI", 10)
    )

    # Column Headings styling with clean corporate look
    style.configure(
        "Custom.Treeview.Heading",
        background=header_bg,
        foreground=primary,
        relief="flat",
        font=("Segoe UI Semibold", 10, "bold"),
        padding=(10, 8),
        borderwidth=0
    )

    # Hover and selected behaviors
    style.map(
        "Custom.Treeview.Heading",
        background=[("active", border_col)],
        foreground=[("active", text_main)]
    )

    style.map(
        "Custom.Treeview",
        background=[("selected", primary)],
        foreground=[("selected", "#ffffff")]
    )


class ThemeManager:
    """Manages dynamic UI styling and theme switching."""
    _current_theme_name = "💼 Corporate Slate"
    _listeners = []

    @classmethod
    def get_current_theme(cls):
        return THEMES.get(cls._current_theme_name, THEMES["💼 Corporate Slate"])

    @classmethod
    def get_theme_names(cls):
        return list(THEMES.keys())

    @classmethod
    def set_theme(cls, name):
        if name in THEMES:
            cls._current_theme_name = name
            t = THEMES[name]
            global COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SECONDARY
            global COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING, COLOR_PURPLE
            global BG_SIDEBAR, BG_MAIN, BG_CARD, BG_CARD_ALT, BG_INPUT, BORDER_COLOR
            global TEXT_MAIN, TEXT_MUTED, TEXT_ACCENT

            COLOR_PRIMARY = t["primary"]
            COLOR_PRIMARY_HOVER = t["primary_hover"]
            COLOR_SECONDARY = t["secondary"]
            COLOR_SUCCESS = t["success"]
            COLOR_DANGER = t["danger"]
            COLOR_WARNING = t["warning"]
            COLOR_PURPLE = t["purple"]
            BG_SIDEBAR = t["bg_sidebar"]
            BG_MAIN = t["bg_main"]
            BG_CARD = t["bg_card"]
            BG_CARD_ALT = t.get("bg_card_alt", t["bg_main"])
            BG_INPUT = t["bg_input"]
            BORDER_COLOR = t["border"]
            TEXT_MAIN = t["text_main"]
            TEXT_MUTED = t["text_muted"]
            TEXT_ACCENT = t["text_accent"]

            # Reconfigure Treeview table styles globally
            try:
                configure_treeview_style(t)
            except Exception:
                pass

            for listener in cls._listeners:
                try:
                    listener(t)
                except Exception:
                    pass

    @classmethod
    def subscribe(cls, listener):
        if listener not in cls._listeners:
            cls._listeners.append(listener)


# Initial constants
_default = THEMES["💼 Corporate Slate"]
COLOR_PRIMARY = _default["primary"]
COLOR_PRIMARY_HOVER = _default["primary_hover"]
COLOR_SECONDARY = _default["secondary"]
COLOR_SUCCESS = _default["success"]
COLOR_DANGER = _default["danger"]
COLOR_WARNING = _default["warning"]
COLOR_INFO = "#0284c7"
COLOR_PURPLE = _default["purple"]

BG_SIDEBAR = _default["bg_sidebar"]
BG_MAIN = _default["bg_main"]
BG_CARD = _default["bg_card"]
BG_CARD_ALT = _default.get("bg_card_alt", _default["bg_main"])
BG_INPUT = _default["bg_input"]
BORDER_COLOR = _default["border"]

TEXT_MAIN = _default["text_main"]
TEXT_MUTED = _default["text_muted"]
TEXT_ACCENT = _default["text_accent"]

# Enterprise Corporate Typography: Segoe UI Semibold for Titles & Headers, Segoe UI for Body & Tables
FONT_FAMILY_TITLE = "Segoe UI Semibold"
FONT_FAMILY_BODY = "Segoe UI"

FONT_TITLE = (FONT_FAMILY_TITLE, 20, "bold")
FONT_SUBTITLE = (FONT_FAMILY_TITLE, 15, "bold")
FONT_HEADER = (FONT_FAMILY_TITLE, 13, "bold")
FONT_BODY = (FONT_FAMILY_BODY, 11)
FONT_BODY_BOLD = (FONT_FAMILY_TITLE, 11)
FONT_SMALL = (FONT_FAMILY_BODY, 9)
FONT_STAT_NUM = (FONT_FAMILY_TITLE, 22, "bold")
