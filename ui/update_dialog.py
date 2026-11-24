"""Modern update notification popup dialog for Controlito."""
import customtkinter as ctk
from ui.theme import (
    ThemeManager, COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS,
    COLOR_DANGER, BG_CARD, BG_MAIN, TEXT_MAIN, TEXT_MUTED,
    FONT_TITLE, FONT_SUBTITLE, FONT_HEADER, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)
from utils.updater import open_download_page


class UpdateDialog(ctk.CTkToplevel):
    def __init__(self, parent, update_info):
        super().__init__(parent)
        self.update_info = update_info

        self.title("🚀 Actualización Disponible — Controlito")
        self.geometry("520x460")
        self.minsize(460, 400)
        self.transient(parent)
        self.grab_set()

        # Center on parent window
        self.update_idletasks()
        try:
            x = parent.winfo_rootx() + (parent.winfo_width() // 2) - 260
            y = parent.winfo_rooty() + (parent.winfo_height() // 2) - 230
            self.geometry(f"+{max(10, x)}+{max(10, y)}")
        except Exception:
            pass

        self.build_ui()

    def build_ui(self):
        curr = ThemeManager.get_current_theme()
        self.configure(fg_color=curr["bg_main"])

        # Header with rocket icon
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 10))

        lbl_title = ctk.CTkLabel(
            header,
            text="🚀 ¡Nueva Versión Disponible!",
            font=FONT_TITLE,
            text_color=curr["text_main"]
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            header,
            text="Una nueva versión de Controlito está lista para ser descargada e instalada.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        )
        lbl_sub.pack(anchor="w", pady=(2, 0))

        # Version Comparison Card
        card = ctk.CTkFrame(self, fg_color=curr["bg_card"], corner_radius=10, border_width=1, border_color=curr["border"])
        card.pack(fill="x", padx=25, pady=(5, 12))

        ver_row = ctk.CTkFrame(card, fg_color="transparent")
        ver_row.pack(fill="x", padx=16, pady=12)

        lbl_curr = ctk.CTkLabel(
            ver_row,
            text=f"Tu versión: {self.update_info.get('current_version', '')}",
            font=FONT_BODY,
            text_color=curr["text_muted"]
        )
        lbl_curr.pack(side="left")

        lbl_arrow = ctk.CTkLabel(
            ver_row,
            text=" ➔ ",
            font=FONT_BODY_BOLD,
            text_color=curr["primary"]
        )
        lbl_arrow.pack(side="left", padx=8)

        lbl_new = ctk.CTkLabel(
            ver_row,
            text=f"Nueva: {self.update_info.get('latest_version', '')}",
            font=FONT_BODY_BOLD,
            text_color=curr.get("success", "#059669")
        )
        lbl_new.pack(side="left")

        rel_name = self.update_info.get("release_name", "")
        if rel_name:
            lbl_name = ctk.CTkLabel(
                card,
                text=rel_name,
                font=FONT_BODY_BOLD,
                text_color=curr["text_main"],
                anchor="w"
            )
            lbl_name.pack(fill="x", padx=16, pady=(0, 10))

        # Scrollable changelog / release notes
        notes_title = ctk.CTkLabel(
            self,
            text="Novedades de esta versión:",
            font=FONT_BODY_BOLD,
            text_color=curr["text_main"]
        )
        notes_title.pack(anchor="w", padx=25, pady=(0, 4))

        notes_box = ctk.CTkScrollableFrame(self, fg_color=curr["bg_card"], corner_radius=8, height=140)
        notes_box.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        raw_notes = self.update_info.get("release_notes", "").strip() or "Mejoras de rendimiento y correcciones de errores."
        lbl_notes = ctk.CTkLabel(
            notes_box,
            text=raw_notes,
            font=FONT_SMALL,
            text_color=curr["text_muted"],
            justify="left",
            wraplength=430
        )
        lbl_notes.pack(fill="both", expand=True, padx=8, pady=8, anchor="w")

        # Bottom action buttons
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=25, pady=(0, 20))

        btn_download = ctk.CTkButton(
            btn_row,
            text="📥 Descargar Actualización (.exe)",
            font=FONT_BODY_BOLD,
            height=38,
            fg_color=curr["primary"],
            hover_color=curr["primary_hover"],
            command=self._download_now
        )
        btn_download.pack(side="left", fill="x", expand=True, padx=(0, 10))

        btn_later = ctk.CTkButton(
            btn_row,
            text="Más tarde",
            font=FONT_BODY,
            height=38,
            fg_color="transparent",
            border_width=1,
            border_color=curr["border"],
            text_color=curr["text_muted"],
            hover_color=curr["bg_card"],
            command=self.destroy
        )
        btn_later.pack(side="right", padx=(0, 0))

    def _download_now(self):
        download_url = self.update_info.get("download_url") or self.update_info.get("html_url")
        open_download_page(download_url)
        self.destroy()
