"""Simple Mode view: Natural language conversational chat with the financial database."""
import customtkinter as ctk
from utils.chat_engine import FinancialChatEngine
from ui.theme import (
    COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_SUCCESS, COLOR_DANGER,
    BG_CARD, BG_MAIN, BG_SIDEBAR, TEXT_MAIN, TEXT_MUTED,
    FONT_TITLE, FONT_HEADER, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)


class SimpleChatView(ctk.CTkFrame):
    def __init__(self, parent, db, on_switch_to_data=None, on_theme_change=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_switch_to_data = on_switch_to_data
        self.on_theme_change = on_theme_change
        self.engine = FinancialChatEngine(db)

        self.build_ui()
        # Post initial welcoming bot message
        self.after(200, self.post_welcome_message)

    def build_ui(self):
        from ui.theme import ThemeManager
        curr = ThemeManager.get_current_theme()

        # Header banner
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(15, 10))

        title_box = ctk.CTkFrame(header, fg_color="transparent")
        title_box.pack(side="left")

        lbl_title = ctk.CTkLabel(
            title_box,
            text="💬 Modo Simple — Asistente Financiero",
            font=FONT_TITLE,
            text_color=curr["text_main"]
        )
        lbl_title.pack(anchor="w")

        lbl_sub = ctk.CTkLabel(
            title_box,
            text="Habla directo con tus finanzas en lenguaje natural sin tener que revisar tablas ni números.",
            font=FONT_SMALL,
            text_color=curr["text_muted"]
        )
        lbl_sub.pack(anchor="w")

        # Right actions
        if self.on_switch_to_data:
            right_actions = ctk.CTkFrame(header, fg_color="transparent")
            right_actions.pack(side="right")

            btn_data = ctk.CTkButton(
                right_actions,
                text="📊 Cambiar a Modo Data",
                fg_color=curr["bg_card"],
                hover_color=curr["border"],
                font=FONT_BODY_BOLD,
                command=self.on_switch_to_data
            )
            btn_data.pack(side="right", padx=5)

        # Chat stream scrollable frame
        self.chat_scroll = ctk.CTkScrollableFrame(
            self,
            fg_color=curr.get("bg_sidebar", "#070a12"),
            corner_radius=12
        )
        self.chat_scroll.pack(fill="both", expand=True, padx=25, pady=(5, 10))

        # Suggestion chips container
        chips_frame = ctk.CTkFrame(self, fg_color="transparent")
        chips_frame.pack(fill="x", padx=25, pady=(0, 6))

        chips = [
            "💵 ¿Cuánta plata tengo ahora?",
            "💸 ¿Cuánto gasté este mes?",
            "💳 ¿Por qué gasté más en TC que el mes pasado?",
            "🎯 Oportunidades de mejora",
            "📊 Mostrame un cuadro comparativo de gastos",
            "🔍 ¿Qué día gasté en comprar...",
        ]

        # Put chips in horizontal scroll or flow
        for chip_text in chips:
            btn_chip = ctk.CTkButton(
                chips_frame,
                text=chip_text,
                font=FONT_SMALL,
                height=28,
                fg_color=curr["bg_card"],
                hover_color=curr["border"],
                text_color=curr["text_muted"],
                command=lambda t=chip_text: self.on_chip_click(t)
            )
            btn_chip.pack(side="left", padx=3)

        # Input box toolbar
        input_bar = ctk.CTkFrame(self, fg_color=curr["bg_card"], corner_radius=12)
        input_bar.pack(fill="x", padx=25, pady=(0, 15))

        self.input_entry = ctk.CTkEntry(
            input_bar,
            placeholder_text="Escribe tu consulta aquí... (ej: '¿Por qué gasté más en TC?', '¿Qué día compré un cargador?')",
            font=FONT_BODY,
            height=46,
            fg_color="transparent",
            border_width=0,
            text_color=curr["text_main"]
        )
        self.input_entry.pack(side="left", fill="x", expand=True, padx=(15, 5), pady=4)
        self.input_entry.bind("<Return>", lambda e: self.send_message())

        btn_send = ctk.CTkButton(
            input_bar,
            text="Enviar ➤",
            font=FONT_BODY_BOLD,
            width=90,
            height=38,
            fg_color=curr["primary"],
            hover_color=curr["primary_hover"],
            command=self.send_message
        )
        btn_send.pack(side="right", padx=6, pady=4)

    def post_welcome_message(self):
        welcome_text = (
            "👋 **¡Hola! Bienvenido al Modo Simple de Controlito.**\n\n"
            "Aquí puedes preguntarme cualquier duda sobre tus gastos, ingresos, tarjetas o servicios sin marearte con tablas ni números.\n\n"
            "👉 *Prueba preguntarme cosas como:* \n"
            "• *'¿Cuánta plata tengo ahora?'*\n"
            "• *'¿Cuánto gasté en noviembre?'*\n"
            "• *'¿Por qué gasté más en TC que el mes pasado?'*\n"
            "• *'¿Qué día gasté plata en comprar zapatillas?'*\n"
            "• *'Dame oportunidades de mejora y ahorro'*"
        )
        self.add_chat_bubble(welcome_text, is_user=False)

    def on_chip_click(self, text):
        clean_text = text.split(" ", 1)[-1]  # remove emoji
        if clean_text.endswith("..."):
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, clean_text.replace("...", " "))
            self.input_entry.focus()
        else:
            self.input_entry.delete(0, "end")
            self.input_entry.insert(0, clean_text)
            self.send_message()

    def send_message(self):
        msg = self.input_entry.get().strip()
        if not msg:
            return

        self.input_entry.delete(0, "end")
        # 1. Add User bubble
        self.add_chat_bubble(msg, is_user=True)

        # 2. Process query
        self.after(100, lambda: self._process_bot_reply(msg))

    def _process_bot_reply(self, user_msg):
        reply = self.engine.process_query(user_msg)
        self.add_chat_bubble(reply, is_user=False)

    def add_chat_bubble(self, text, is_user=False):
        from ui.theme import ThemeManager
        curr = ThemeManager.get_current_theme()

        bubble_row = ctk.CTkFrame(self.chat_scroll, fg_color="transparent")
        bubble_row.pack(fill="x", pady=6, padx=10)

        # Left or Right aligned
        side = "right" if is_user else "left"
        bubble_color = curr["primary"] if is_user else curr["bg_card"]
        text_color = "#ffffff" if is_user else curr["text_main"]

        bubble = ctk.CTkFrame(bubble_row, fg_color=bubble_color, corner_radius=12)
        bubble.pack(side=side, anchor="e" if is_user else "w", padx=5)

        prefix = "Tú: " if is_user else "🤖 Controlito: "
        lbl_head = ctk.CTkLabel(
            bubble,
            text=prefix,
            font=FONT_SMALL,
            text_color="#ffffff" if is_user else curr["text_accent"]
        )
        lbl_head.pack(anchor="w", padx=14, pady=(8, 2))

        lbl_text = ctk.CTkLabel(
            bubble,
            text=text,
            font=FONT_BODY,
            text_color=text_color,
            wraplength=680,
            justify="left"
        )
        lbl_text.pack(anchor="w", padx=14, pady=(0, 10))

        # Check if response asks for comparative chart or data, offer quick button
        if not is_user and any(kw in text.lower() for kw in ["cuadro comparativo", "modo data", "desglose"]):
            if self.on_switch_to_data:
                btn_action = ctk.CTkButton(
                    bubble,
                    text="📊 Ver panel completo en Modo Data",
                    font=FONT_SMALL,
                    height=28,
                    fg_color=curr["bg_main"],
                    hover_color=curr["border"],
                    command=self.on_switch_to_data
                )
                btn_action.pack(anchor="w", padx=14, pady=(0, 10))

        # Scroll to bottom
        self.after(50, lambda: self.chat_scroll._parent_canvas.yview_moveto(1.0))
