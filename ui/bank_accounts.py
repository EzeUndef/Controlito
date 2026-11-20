"""Bank accounts and savings management view with live Dólar API integration."""
import customtkinter as ctk
from tkinter import messagebox
from utils.helpers import format_currency
from utils.dolar_api import fetch_dolar_rates_async, get_current_rates
from ui.theme import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING,
    BG_CARD, BG_CARD_ALT, TEXT_MAIN, TEXT_MUTED, FONT_TITLE,
    FONT_HEADER, FONT_BODY, FONT_BODY_BOLD, FONT_SMALL, FONT_STAT_NUM
)


# Display names and keys for each rate type
RATE_TYPES = [
    ("oficial", "Dólar Oficial"),
    ("blue", "Dólar Blue"),
    ("bolsa", "Dólar MEP / Bolsa"),
    ("tarjeta", "Dólar Tarjeta"),
    ("cripto", "Dólar Cripto"),
    ("contadoconliqui", "Dólar CCL"),
]


class BankAccountsView(ctk.CTkFrame):
    def __init__(self, parent, db, on_data_changed=None):
        super().__init__(parent, fg_color="transparent")
        self.db = db
        self.on_data_changed = on_data_changed
        self.rate_cards = {}
        self.rate_checkboxes = {}
        self.selected_rate_key = "blue"  # default conversion rate

        # Load saved preference
        saved_rate = self.db.get_setting("dolar_rate_type", "blue")
        if any(k == saved_rate for k, _ in RATE_TYPES):
            self.selected_rate_key = saved_rate

        self.build_ui()
        self.load_data()
        # Auto-fetch live rates on load
        self.after(300, self.refresh_dolar_rates)

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(header, text="🏦 Bancos & Ahorros", font=FONT_TITLE, text_color=TEXT_MAIN)
        title.pack(side="left")

        btn_refresh = ctk.CTkButton(
            header,
            text="🔄 Actualizar Dólar",
            fg_color="#334155",
            hover_color="#475569",
            font=FONT_BODY_BOLD,
            command=self.refresh_dolar_rates
        )
        btn_refresh.pack(side="right", padx=5)

        btn_new_bank = ctk.CTkButton(
            header,
            text="+ Agregar Cuenta",
            fg_color=COLOR_PRIMARY,
            font=FONT_BODY_BOLD,
            command=self.open_add_bank_dialog
        )
        btn_new_bank.pack(side="right", padx=5)

        # Top section: Savings Summary Cards
        savings_frame = ctk.CTkFrame(self, fg_color="transparent")
        savings_frame.pack(fill="x", padx=20, pady=5)
        savings_frame.grid_columnconfigure((0, 1, 2, 3), weight=1, uniform="sav")

        self.card_usd = self._create_card(savings_frame, 0, "💵 Ahorro USD Disponible", "USD 0.00", COLOR_SUCCESS)
        self.card_dolar_rate = self._create_card(savings_frame, 1, "📈 Cotización Seleccionada", "$ 0.00", COLOR_WARNING)
        self.card_usd_in_ars = self._create_card(savings_frame, 2, "🪙 Equivalente en Pesos", "$ 0.00", COLOR_PRIMARY)
        self.card_total_patrimonio = self._create_card(savings_frame, 3, "💎 Patrimonio Ahorrado", "$ 0.00", "#10b981")

        # Live Dólar Rates Section
        dolar_section_title = ctk.CTkLabel(self, text="📊 Cotizaciones del Dólar en Vivo", font=FONT_HEADER, text_color=TEXT_MAIN)
        dolar_section_title.pack(anchor="w", padx=20, pady=(10, 5))

        self.dolar_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dolar_frame.pack(fill="x", padx=20, pady=(0, 10))
        # 6 columns for 6 rate types
        for i in range(len(RATE_TYPES)):
            self.dolar_frame.grid_columnconfigure(i, weight=1, uniform="dolar")

        self.rate_var = ctk.StringVar(value=self.selected_rate_key)

        for idx, (key, display_name) in enumerate(RATE_TYPES):
            card = ctk.CTkFrame(self.dolar_frame, fg_color=BG_CARD, corner_radius=10)
            card.grid(row=0, column=idx, sticky="nsew", padx=4, pady=4)

            lbl_name = ctk.CTkLabel(card, text=display_name, font=FONT_SMALL, text_color=TEXT_MUTED)
            lbl_name.pack(anchor="w", padx=10, pady=(8, 2))

            lbl_compra = ctk.CTkLabel(card, text="Compra: —", font=("Segoe UI", 10), text_color=COLOR_SUCCESS)
            lbl_compra.pack(anchor="w", padx=10)

            lbl_venta = ctk.CTkLabel(card, text="Venta: —", font=("Segoe UI", 10, "bold"), text_color=COLOR_DANGER)
            lbl_venta.pack(anchor="w", padx=10)

            lbl_fecha = ctk.CTkLabel(card, text="", font=("Segoe UI", 8), text_color=TEXT_MUTED)
            lbl_fecha.pack(anchor="w", padx=10, pady=(0, 2))

            # Radio button to select which rate to use for conversion
            rb = ctk.CTkRadioButton(
                card,
                text="Usar para conversión",
                variable=self.rate_var,
                value=key,
                font=("Segoe UI", 9),
                command=lambda k=key: self.on_rate_selected(k)
            )
            rb.pack(anchor="w", padx=10, pady=(2, 8))

            self.rate_cards[key] = {
                "compra": lbl_compra,
                "venta": lbl_venta,
                "fecha": lbl_fecha,
                "card": card,
            }

        # Status label
        self.lbl_dolar_status = ctk.CTkLabel(self, text="⏳ Cargando cotizaciones...", font=FONT_SMALL, text_color=TEXT_MUTED)
        self.lbl_dolar_status.pack(anchor="w", padx=20, pady=(0, 5))

        # Edit Savings Row button
        btn_edit_savings = ctk.CTkButton(
            self,
            text="⚙️ Actualizar Ahorros USD Manualmente",
            fg_color="#334155",
            hover_color="#475569",
            command=self.open_edit_savings_dialog
        )
        btn_edit_savings.pack(anchor="w", padx=20, pady=(5, 10))

        # Bottom section: Bank accounts grid / list
        lbl_accounts = ctk.CTkLabel(self, text="Cuentas Bancarias y Billeteras Virtuales", font=FONT_HEADER, text_color=TEXT_MAIN)
        lbl_accounts.pack(anchor="w", padx=20, pady=(10, 5))

        self.scroll_banks = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll_banks.pack(fill="both", expand=True, padx=20, pady=5)

    def _create_card(self, parent, col, title, initial_value, text_color):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=12)
        card.grid(row=0, column=col, sticky="nsew", padx=5, pady=5)

        lbl_t = ctk.CTkLabel(card, text=title, font=FONT_SMALL, text_color=TEXT_MUTED)
        lbl_t.pack(anchor="w", padx=12, pady=(10, 2))

        lbl_v = ctk.CTkLabel(card, text=initial_value, font=("Segoe UI", 18, "bold"), text_color=text_color)
        lbl_v.pack(anchor="w", padx=12, pady=(0, 10))
        return lbl_v

    def on_rate_selected(self, key):
        self.selected_rate_key = key
        self.db.set_setting("dolar_rate_type", key)
        self.update_savings_display()

    def refresh_dolar_rates(self):
        """Fetch live rates from the API asynchronously."""
        self.lbl_dolar_status.configure(text="⏳ Consultando dolarapi.com...")

        def on_result(success, rates):
            # This callback runs in a background thread, schedule UI update on main thread
            self.after(0, lambda: self._apply_rates(success, rates))

        fetch_dolar_rates_async(callback=on_result)

    def _apply_rates(self, success, rates):
        """Update the rate cards with live data (called on main thread)."""
        for key, widgets in self.rate_cards.items():
            if key in rates:
                r = rates[key]
                compra = r.get("compra", 0)
                venta = r.get("venta", 0)
                fecha = r.get("fecha", "")
                widgets["compra"].configure(text=f"Compra: ${compra:,.2f}" if compra else "Compra: —")
                widgets["venta"].configure(text=f"Venta: ${venta:,.2f}" if venta else "Venta: —")
                if fecha:
                    widgets["fecha"].configure(text=f"Actualizado: {fecha}")

        if success:
            self.lbl_dolar_status.configure(text="✅ Cotizaciones actualizadas en vivo desde dolarapi.com", text_color=COLOR_SUCCESS)
        else:
            self.lbl_dolar_status.configure(text="⚠️ Sin conexión — mostrando última cotización guardada", text_color=COLOR_WARNING)

        self.update_savings_display()

    def update_savings_display(self):
        """Recalculate the savings cards using the selected rate."""
        savings = self.db.get_savings()
        usd_total = 0.0

        for s in savings:
            c = s["concepto"].lower()
            if "restante" in c or "disponible" in c:
                usd_total = s["monto"]
            elif "total ahorro" in c and usd_total == 0:
                usd_total = s["monto"]

        if usd_total == 0 and savings:
            for s in savings:
                if s["moneda"] == "USD":
                    usd_total = s["monto"]
                    break

        # Get the venta rate for the selected type
        rates = get_current_rates()
        rate_data = rates.get(self.selected_rate_key, {})
        venta_rate = rate_data.get("venta", 0) or rate_data.get("compra", 0) or 1525.0
        display_name = dict(RATE_TYPES).get(self.selected_rate_key, "Dólar")

        total_en_pesos = usd_total * venta_rate

        self.card_usd.configure(text=f"USD {usd_total:,.2f}")
        self.card_dolar_rate.configure(text=f"${venta_rate:,.2f} ({display_name})")
        self.card_usd_in_ars.configure(text=format_currency(total_en_pesos))
        self.card_total_patrimonio.configure(text=format_currency(total_en_pesos))

    def load_data(self):
        # 1. Load Savings info
        self.update_savings_display()

        # 2. Load Bank Accounts cards
        for widget in self.scroll_banks.winfo_children():
            widget.destroy()

        accounts = self.db.get_bank_accounts()
        if not accounts:
            lbl_empty = ctk.CTkLabel(self.scroll_banks, text="No hay cuentas registradas. Agrega una con el botón de arriba.", font=FONT_BODY, text_color=TEXT_MUTED)
            lbl_empty.pack(pady=30)
            return

        for acc in accounts:
            card = ctk.CTkFrame(self.scroll_banks, fg_color=BG_CARD, corner_radius=10)
            card.pack(fill="x", pady=6)

            left_box = ctk.CTkFrame(card, fg_color="transparent")
            left_box.pack(side="left", padx=15, pady=10)

            lbl_name = ctk.CTkLabel(left_box, text=f"🏛️ {acc['banco']}", font=FONT_BODY_BOLD, text_color=TEXT_MAIN)
            lbl_name.pack(anchor="w")

            alias_text = f"Alias: {acc['alias']}" if acc['alias'] else "Sin Alias"
            lbl_alias = ctk.CTkLabel(left_box, text=alias_text, font=FONT_SMALL, text_color=TEXT_MUTED)
            lbl_alias.pack(anchor="w")

            mid_box = ctk.CTkFrame(card, fg_color="transparent")
            mid_box.pack(side="left", padx=25, pady=10)

            motivo_text = f"Motivo: {acc['motivo']}" if acc['motivo'] else ""
            lbl_motivo = ctk.CTkLabel(mid_box, text=motivo_text, font=FONT_SMALL, text_color=TEXT_MUTED)
            lbl_motivo.pack(anchor="w")

            cvu_text = f"CBU/CVU: {acc['cvu_cbu']}" if acc['cvu_cbu'] else ""
            lbl_cvu = ctk.CTkLabel(mid_box, text=cvu_text, font=FONT_SMALL, text_color=TEXT_MUTED)
            lbl_cvu.pack(anchor="w")

            # Copy & Action buttons
            actions_box = ctk.CTkFrame(card, fg_color="transparent")
            actions_box.pack(side="right", padx=15, pady=10)

            if acc['alias']:
                btn_copy_alias = ctk.CTkButton(
                    actions_box,
                    text="Copiar Alias",
                    width=90,
                    height=28,
                    fg_color="#334155",
                    command=lambda a=acc['alias']: self.copy_to_clipboard(a, "Alias")
                )
                btn_copy_alias.pack(side="left", padx=3)

            if acc['cvu_cbu']:
                btn_copy_cvu = ctk.CTkButton(
                    actions_box,
                    text="Copiar CBU",
                    width=90,
                    height=28,
                    fg_color="#334155",
                    command=lambda c=acc['cvu_cbu']: self.copy_to_clipboard(c, "CBU/CVU")
                )
                btn_copy_cvu.pack(side="left", padx=3)

            btn_del = ctk.CTkButton(
                actions_box,
                text="✕",
                width=30,
                height=28,
                fg_color=COLOR_DANGER,
                command=lambda bid=acc['id']: self.delete_bank(bid)
            )
            btn_del.pack(side="left", padx=3)

    def copy_to_clipboard(self, text, label):
        self.clipboard_clear()
        self.clipboard_append(text)
        messagebox.showinfo("Copiado", f"{label} copiado al portapapeles: {text}")

    def delete_bank(self, bid):
        if messagebox.askyesno("Confirmar", "¿Deseas eliminar esta cuenta bancaria?"):
            self.db.delete_bank_account(bid)
            self.load_data()

    def open_add_bank_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Nueva Cuenta Bancaria")
        dialog.geometry("400x380")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Agregar Cuenta Bancaria", font=FONT_HEADER, text_color=TEXT_MAIN).pack(pady=(15, 10))
        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=25, pady=5)

        ctk.CTkLabel(form, text="Banco / Entidad (ej: Santander, BNA, MercadoPago):", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ent_banco = ctk.CTkEntry(form, font=FONT_BODY)
        ent_banco.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(form, text="Alias:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ent_alias = ctk.CTkEntry(form, font=FONT_BODY)
        ent_alias.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(form, text="Motivo / Uso (ej: Haberes, Ahorro, Varios):", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ent_motivo = ctk.CTkEntry(form, font=FONT_BODY)
        ent_motivo.pack(fill="x", pady=(2, 8))

        ctk.CTkLabel(form, text="CVU / CBU:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ent_cvu = ctk.CTkEntry(form, font=FONT_BODY)
        ent_cvu.pack(fill="x", pady=(2, 12))

        def save():
            b = ent_banco.get().strip()
            if not b:
                messagebox.showerror("Error", "Debes ingresar el nombre del banco o billetera.")
                return
            a = ent_alias.get().strip()
            m = ent_motivo.get().strip()
            c = ent_cvu.get().strip()
            self.db.add_bank_account(b, a, m, c)
            dialog.destroy()
            self.load_data()

        ctk.CTkButton(dialog, text="Guardar Cuenta", fg_color=COLOR_SUCCESS, font=FONT_BODY_BOLD, command=save).pack(pady=15)

    def open_edit_savings_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Actualizar Ahorros & Cotización")
        dialog.geometry("400x320")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ctk.CTkLabel(dialog, text="Actualizar Ahorros USD", font=FONT_HEADER, text_color=TEXT_MAIN).pack(pady=(15, 10))
        form = ctk.CTkFrame(dialog, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=25, pady=5)

        savings = self.db.get_savings()
        usd_val = 880.17

        for s in savings:
            c = s["concepto"].lower()
            if "restante" in c or "disponible" in c or "total ahorro" in c:
                usd_val = s["monto"]

        ctk.CTkLabel(form, text="Total Ahorro en USD:", font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ent_usd = ctk.CTkEntry(form, font=FONT_BODY)
        ent_usd.pack(fill="x", pady=(2, 10))
        ent_usd.insert(0, str(usd_val))

        ctk.CTkLabel(form, text="💡 La cotización se actualiza automáticamente desde dolarapi.com", font=FONT_SMALL, text_color=COLOR_SUCCESS).pack(anchor="w", pady=(5, 10))

        def save():
            try:
                u = float(ent_usd.get().strip())
                # Update in DB
                self.db.conn.execute("DELETE FROM savings WHERE concepto IN ('Restante USD', 'Total ahorro USD')")
                self.db.add_saving("Restante USD", u, "USD")
                dialog.destroy()
                self.load_data()
                if self.on_data_changed:
                    self.on_data_changed()
            except ValueError:
                messagebox.showerror("Error", "El valor debe ser un número válido.")

        ctk.CTkButton(dialog, text="Guardar Ahorros", fg_color=COLOR_SUCCESS, font=FONT_BODY_BOLD, command=save).pack(pady=15)
