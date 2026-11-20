"""Theme and styling configuration for Controlito UI with Next-Gen Aesthetics & Bahnschrift Typography."""
import tkinter as tk
from tkinter import ttk

THEMES = {
    "💎 Next-Gen Obsidian": {
        "name": "💎 Next-Gen Obsidian",
        "primary": "#6366f1",         # Electric Indigo
        "primary_hover": "#4f46e5",
        "secondary": "#475569",
        "success": "#10b981",         # Emerald Green
        "danger": "#f43f5e",          # Rose Red
        "warning": "#f59e0b",         # Amber
        "purple": "#8b5cf6",
        "bg_sidebar": "#070a12",      # Pure Midnight
        "bg_main": "#0b0f19",         # Deep Obsidian
        "bg_card": "#131b2c",         # Slate Glass Card
        "bg_card_alt": "#0d1422",     # Slightly darker card for zebra rows
        "bg_input": "#080c14",
        "border": "#1e293d",
        "text_main": "#f8fafc",
        "text_muted": "#94a3b8",
        "text_accent": "#38bdf8",
        "chart_bg": "#131b2c",
        "chart_palette": ["#6366f1", "#10b981", "#f43f5e", "#f59e0b", "#06b6d4", "#8b5cf6"]
    },
    "🌌 Cyber Neon": {
        "name": "🌌 Cyber Neon",
        "primary": "#00f5d4",         # Neon Cyan
        "primary_hover": "#00bbf9",
        "secondary": "#7b2cbf",
        "success": "#00f5d4",
        "danger": "#f72585",          # Hot Pink / Magenta
        "warning": "#fee440",
        "purple": "#7209b7",
        "bg_sidebar": "#07060e",      # Deep Void
        "bg_main": "#0e0d1a",
        "bg_card": "#18142e",         # Synthwave Dark Violet
        "bg_card_alt": "#120e24",
        "bg_input": "#090814",
        "border": "#3b2c6e",
        "text_main": "#f8fafc",
        "text_muted": "#b8aee8",
        "text_accent": "#00f5d4",
        "chart_bg": "#18142e",
        "chart_palette": ["#00f5d4", "#f72585", "#7209b7", "#fee440", "#4cc9f0", "#b5179e"]
    },
    "🌲 Nordic Pine": {
        "name": "🌲 Nordic Pine",
        "primary": "#10b981",         # Emerald Green
        "primary_hover": "#059669",
        "secondary": "#2d6a4f",
        "success": "#2ec4b6",
        "danger": "#e76f51",
        "warning": "#f4a261",
        "purple": "#52b788",
        "bg_sidebar": "#06140e",      # Deep Pine Wood
        "bg_main": "#0d1f17",
        "bg_card": "#173124",         # Forest Card
        "bg_card_alt": "#10241b",
        "bg_input": "#08160f",
        "border": "#284f3a",
        "text_main": "#e8f5e9",
        "text_muted": "#95d5b2",
        "text_accent": "#52b788",
        "chart_bg": "#173124",
        "chart_palette": ["#2ec4b6", "#52b788", "#f4a261", "#e76f51", "#74c69d", "#b7e4c7"]
    },
    "☕ Espresso Gold": {
        "name": "☕ Espresso Gold",
        "primary": "#d97706",         # Rich Amber Caramel
        "primary_hover": "#b45309",
        "secondary": "#78350f",
        "success": "#10b981",
        "danger": "#dc2626",
        "warning": "#f59e0b",
        "purple": "#c2410c",
        "bg_sidebar": "#120f0d",      # Roasted Dark
        "bg_main": "#1c1612",
        "bg_card": "#2a221b",         # Warm Coffee Glass
        "bg_card_alt": "#211a14",
        "bg_input": "#100d0b",
        "border": "#45372c",
        "text_main": "#fef3c7",
        "text_muted": "#d4b89e",
        "text_accent": "#fbbf24",
        "chart_bg": "#2a221b",
        "chart_palette": ["#fbbf24", "#d97706", "#f59e0b", "#10b981", "#ef4444", "#a16207"]
    },
    "🌊 Midnight Blue": {
        "name": "🌊 Midnight Blue",
        "primary": "#3b82f6",         # Electric Cobalt
        "primary_hover": "#2563eb",
        "secondary": "#64748b",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#f59e0b",
        "purple": "#8b5cf6",
        "bg_sidebar": "#0a101d",      # Abyss Blue
        "bg_main": "#0f172a",
        "bg_card": "#1e293b",         # Navy Slate Card
        "bg_card_alt": "#162032",
        "bg_input": "#0a101d",
        "border": "#334155",
        "text_main": "#f8fafc",
        "text_muted": "#94a3b8",
        "text_accent": "#38bdf8",
        "chart_bg": "#1e293b",
        "chart_palette": ["#3b82f6", "#10b981", "#ef4444", "#f59e0b", "#8b5cf6", "#06b6d4"]
    },
    "🌸 Dracula Velvet": {
        "name": "🌸 Dracula Velvet",
        "primary": "#bd93f9",         # Vampire Purple
        "primary_hover": "#a777e3",
        "secondary": "#6272a4",
        "success": "#50fa7b",
        "danger": "#ff5555",
        "warning": "#f1fa8c",
        "purple": "#ff79c6",          # Hot Neon Pink
        "bg_sidebar": "#100e17",
        "bg_main": "#191622",         # Velvet Matte
        "bg_card": "#242038",         # Purple Slate Card
        "bg_card_alt": "#1c182c",
        "bg_input": "#13101d",
        "border": "#3b345a",
        "text_main": "#f8f8f2",
        "text_muted": "#a599c2",
        "text_accent": "#ff79c6",
        "chart_bg": "#242038",
        "chart_palette": ["#bd93f9", "#ff79c6", "#50fa7b", "#ff5555", "#8be9fd", "#f1fa8c"]
    },
    "🍊 Sunset Crimson": {
        "name": "🍊 Sunset Crimson",
        "primary": "#f97316",         # Fire Orange
        "primary_hover": "#ea580c",
        "secondary": "#7c2d12",
        "success": "#10b981",
        "danger": "#ef4444",
        "warning": "#fbbf24",
        "purple": "#d946ef",
        "bg_sidebar": "#110b0e",
        "bg_main": "#1a1215",         # Warm Carbon
        "bg_card": "#261a20",         # Ruby Dark Card
        "bg_card_alt": "#1e1419",
        "bg_input": "#0e090b",
        "border": "#4a2d39",
        "text_main": "#fff1f2",
        "text_muted": "#c9a6b1",
        "text_accent": "#f97316",
        "chart_bg": "#261a20",
        "chart_palette": ["#f97316", "#ef4444", "#fbbf24", "#10b981", "#d946ef", "#06b6d4"]
    },
    "❄️ Arctic Frost": {
        "name": "❄️ Arctic Frost",
        "primary": "#06b6d4",         # Glacial Cyan
        "primary_hover": "#0891b2",
        "secondary": "#475569",
        "success": "#10b981",
        "danger": "#f43f5e",
        "warning": "#f59e0b",
        "purple": "#6366f1",
        "bg_sidebar": "#090d16",
        "bg_main": "#0f172a",         # Deep Glacial
        "bg_card": "#182238",         # Titanium Glass
        "bg_card_alt": "#121b2d",
        "bg_input": "#0a101c",
        "border": "#233352",
        "text_main": "#f0f9ff",
        "text_muted": "#8ec1dc",
        "text_accent": "#06b6d4",
        "chart_bg": "#182238",
        "chart_palette": ["#06b6d4", "#38bdf8", "#10b981", "#6366f1", "#f43f5e", "#f59e0b"]
    }
}


def configure_treeview_style(theme=None):
    """Configures high-end modern styling for all ttk.Treeview tables in the app."""
    if theme is None:
        theme = ThemeManager.get_current_theme()

    style = ttk.Style()
    # Force 'clam' theme which reliably supports complete custom coloring on Windows
    try:
        style.theme_use("clam")
    except Exception:
        pass

    bg_card = theme.get("bg_card", "#131b2c")
    bg_alt = theme.get("bg_card_alt", "#0b0f19")
    primary = theme.get("primary", "#6366f1")
    text_main = theme.get("text_main", "#f8fafc")
    text_muted = theme.get("text_muted", "#94a3b8")
    header_bg = theme.get("bg_sidebar", "#070a12")
    border_col = theme.get("border", "#1e293d")

    # Base Treeview styling
    style.configure(
        "Custom.Treeview",
        background=bg_card,
        foreground=text_main,
        rowheight=34,
        fieldbackground=bg_card,
        borderwidth=0,
        relief="flat",
        font=("Segoe UI", 10)
    )

    # Column Headings styling
    style.configure(
        "Custom.Treeview.Heading",
        background=header_bg,
        foreground=primary,
        relief="flat",
        font=("Bahnschrift", 10, "bold"),
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
    _current_theme_name = "💎 Next-Gen Obsidian"
    _listeners = []

    @classmethod
    def get_current_theme(cls):
        return THEMES.get(cls._current_theme_name, THEMES["💎 Next-Gen Obsidian"])

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
_default = THEMES["💎 Next-Gen Obsidian"]
COLOR_PRIMARY = _default["primary"]
COLOR_PRIMARY_HOVER = _default["primary_hover"]
COLOR_SECONDARY = _default["secondary"]
COLOR_SUCCESS = _default["success"]
COLOR_DANGER = _default["danger"]
COLOR_WARNING = _default["warning"]
COLOR_INFO = "#06b6d4"
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

# High-End Typography: Bahnschrift for Numbers & Headers, Segoe UI for Body
FONT_FAMILY_TITLE = "Bahnschrift"
FONT_FAMILY_BODY = "Segoe UI"

FONT_TITLE = (FONT_FAMILY_TITLE, 22, "bold")
FONT_SUBTITLE = (FONT_FAMILY_TITLE, 16, "bold")
FONT_HEADER = (FONT_FAMILY_TITLE, 14, "bold")
FONT_BODY = (FONT_FAMILY_BODY, 11)
FONT_BODY_BOLD = (FONT_FAMILY_BODY, 11, "bold")
FONT_SMALL = (FONT_FAMILY_BODY, 10)
FONT_STAT_NUM = (FONT_FAMILY_TITLE, 24, "bold")
