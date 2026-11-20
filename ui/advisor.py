"""Financial Advisor and Detective Tools (Detective de Gastos, Deudas, Hábitos, Presupuesto 50/30/20)."""
import customtkinter as ctk
from tkinter import messagebox
from utils.helpers import format_currency
from ui.theme import (
    COLOR_PRIMARY, COLOR_SUCCESS, COLOR_DANGER, COLOR_WARNING, COLOR_PURPLE,
    BG_CARD, BG_MAIN, TEXT_MAIN, TEXT_MUTED, FONT_TITLE, FONT_HEADER,
    FONT_BODY, FONT_BODY_BOLD, FONT_SMALL
)


class AdvisorView(ctk.CTkFrame):
    def __init__(self, parent, db):
        super().__init__(parent, fg_color="transparent")
        self.db = db

        self.build_ui()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(header, text="🧠 Detective Financiero & Asesor Inteligente", font=FONT_TITLE, text_color=TEXT_MAIN)
        title.pack(side="left")

        # Tabview for all modules
        self.tabs = ctk.CTkTabview(self, fg_color=BG_CARD)
        self.tabs.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        self.tab_detective = self.tabs.add("🔍 Detective de Gastos")
        self.tab_deudas = self.tabs.add("💳 Estrategia Deudas")
        self.tab_503020 = self.tabs.add("📐 Regla 50/30/20")
        self.tab_ingresos = self.tabs.add("💼 Fuentes de Ingreso (12 Meses)")
        self.tab_habitos = self.tabs.add("🎯 Hábitos & Reto 30 Días")
        self.tab_ahorro = self.tabs.add("🛡️ Fondo de Emergencia")

        self._build_detective_tab()
        self._build_deudas_tab()
        self._build_503020_tab()
        self._build_ingresos_tab()
        self._build_habitos_tab()
        self._build_ahorro_tab()

    # ==========================================
    # 1. DETECTIVE DE GASTOS
    # ==========================================
    def _build_detective_tab(self):
        container = ctk.CTkScrollableFrame(self.tab_detective, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Intro Card
        banner = ctk.CTkFrame(container, fg_color="#1e293b", corner_radius=10)
        banner.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(
            banner,
            text="🕵️‍♂️ Detector de Fugas y Gastos Hormiga",
            font=FONT_HEADER,
            text_color="#38bdf8"
        ).pack(anchor="w", padx=15, pady=(10, 2))
        ctk.CTkLabel(
            banner,
            text="Analiza compras repetitivas de poco monto, delivery y servicios. Recuerda: Un gasto hormiga de $5.000 repetido 20 veces al mes representa $100.000/mes ($1.200.000 al año).",
            font=FONT_BODY,
            text_color=TEXT_MUTED,
            wraplength=800,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))

        # Run Scan Button
        btn_scan = ctk.CTkButton(
            container,
            text="🔎 Ejecutar Auditoría de Gastos Hormiga",
            fg_color=COLOR_PRIMARY,
            font=FONT_BODY_BOLD,
            command=self._run_detective_scan
        )
        btn_scan.pack(anchor="w", pady=5)

        self.detective_results = ctk.CTkFrame(container, fg_color="transparent")
        self.detective_results.pack(fill="both", expand=True, pady=10)
        self._run_detective_scan()

    def _run_detective_scan(self):
        for w in self.detective_results.winfo_children():
            w.destroy()

        repetitivos = self.db.get_gastos_repetitivos(limit=8)
        if not repetitivos:
            ctk.CTkLabel(self.detective_results, text="No se encontraron suficientes patrones de gastos repetitivos.", font=FONT_BODY, text_color=TEXT_MUTED).pack(pady=20)
            return

        total_anual_potencial = 0.0

        for r in repetitivos:
            card = ctk.CTkFrame(self.detective_results, fg_color="#1e293b", corner_radius=8)
            card.pack(fill="x", pady=4)

            veces = r["veces"]
            promedio = r["promedio"]
            total = r["total"]
            anual_estimado = promedio * veces * 1.5
            total_anual_potencial += anual_estimado

            left = ctk.CTkFrame(card, fg_color="transparent")
            left.pack(side="left", padx=12, pady=8)

            lbl_title = ctk.CTkLabel(left, text=f"• {r['descripcion']} ({r['categoria']})", font=FONT_BODY_BOLD, text_color=TEXT_MAIN)
            lbl_title.pack(anchor="w")
            lbl_sub = ctk.CTkLabel(left, text=f"Frecuencia detectada: {veces} veces | Promedio: {format_currency(promedio)}", font=FONT_SMALL, text_color=TEXT_MUTED)
            lbl_sub.pack(anchor="w")

            right = ctk.CTkFrame(card, fg_color="transparent")
            right.pack(side="right", padx=15, pady=8)
            ctk.CTkLabel(right, text=f"Gasto Acumulado: {format_currency(total)}", font=FONT_BODY_BOLD, text_color=COLOR_DANGER).pack(anchor="e")
            ctk.CTkLabel(right, text=f"Impacto Anual Proyectado: {format_currency(anual_estimado)}", font=FONT_SMALL, text_color=COLOR_WARNING).pack(anchor="e")

        summary_box = ctk.CTkFrame(self.detective_results, fg_color="#0f172a", corner_radius=10)
        summary_box.pack(fill="x", pady=15)
        ctk.CTkLabel(
            summary_box,
            text=f"🎯 Potencial de Ahorro Anual si optimizas estos gastos repetitivos: {format_currency(total_anual_potencial)}",
            font=FONT_HEADER,
            text_color=COLOR_SUCCESS
        ).pack(padx=15, pady=12)

    # ==========================================
    # 2. ESTRATEGIA DE PAGO DE DEUDAS
    # ==========================================
    def _build_deudas_tab(self):
        container = ctk.CTkScrollableFrame(self.tab_deudas, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(container, text="Comparador de Métodos para Liquidar Deudas y Tarjetas", font=FONT_HEADER, text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            container,
            text="Compara Bola de Nieve (mayor impulso psicológico) vs Avalancha (menor interés pagado) vs Híbrido.",
            font=FONT_BODY,
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        # Calculator form
        form = ctk.CTkFrame(container, fg_color="#1e293b", corner_radius=10)
        form.pack(fill="x", pady=5)
        form.grid_columnconfigure((0, 1, 2), weight=1)

        ctk.CTkLabel(form, text="Presupuesto Adicional Mensual ($):", font=FONT_SMALL, text_color=TEXT_MUTED).grid(row=0, column=0, padx=10, pady=(10, 2), sticky="w")
        self.ent_extra_debt = ctk.CTkEntry(form, font=FONT_BODY)
        self.ent_extra_debt.insert(0, "50000")
        self.ent_extra_debt.grid(row=1, column=0, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Deuda Tarjeta Visa / TC ($):", font=FONT_SMALL, text_color=TEXT_MUTED).grid(row=0, column=1, padx=10, pady=(10, 2), sticky="w")
        self.ent_debt_visa = ctk.CTkEntry(form, font=FONT_BODY)
        self.ent_debt_visa.insert(0, "150000")
        self.ent_debt_visa.grid(row=1, column=1, padx=10, pady=(0, 10), sticky="ew")

        ctk.CTkLabel(form, text="Deuda Préstamo / Amex ($):", font=FONT_SMALL, text_color=TEXT_MUTED).grid(row=0, column=2, padx=10, pady=(10, 2), sticky="w")
        self.ent_debt_other = ctk.CTkEntry(form, font=FONT_BODY)
        self.ent_debt_other.insert(0, "250000")
        self.ent_debt_other.grid(row=1, column=2, padx=10, pady=(0, 10), sticky="ew")

        btn_calc_debt = ctk.CTkButton(container, text="Calcular Estrategias", fg_color=COLOR_PRIMARY, font=FONT_BODY_BOLD, command=self._calculate_debt_methods)
        btn_calc_debt.pack(anchor="w", pady=10)

        self.debt_results = ctk.CTkFrame(container, fg_color="transparent")
        self.debt_results.pack(fill="both", expand=True, pady=5)
        self._calculate_debt_methods()

    def _calculate_debt_methods(self):
        for w in self.debt_results.winfo_children():
            w.destroy()

        try:
            extra = float(self.ent_extra_debt.get().strip() or 0)
            d1 = float(self.ent_debt_visa.get().strip() or 0)
            d2 = float(self.ent_debt_other.get().strip() or 0)
        except ValueError:
            return

        total_deuda = d1 + d2
        if total_deuda <= 0:
            ctk.CTkLabel(self.debt_results, text="No hay deudas pendientes registradas.", font=FONT_BODY, text_color=COLOR_SUCCESS).pack(pady=20)
            return

        # Methods cards
        methods_frame = ctk.CTkFrame(self.debt_results, fg_color="transparent")
        methods_frame.pack(fill="x", pady=5)
        methods_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="m")

        # 1. Snowball
        self._create_method_card(
            methods_frame, 0,
            "1. Método Bola de Nieve",
            "Prioridad: Deuda menor primero",
            f"Meses estimados: ~{max(1, int(total_deuda / max(1, extra + 20000)))} meses",
            "✅ Ventaja: Rápida satisfacción emocional al tachar una deuda completa.\n❌ Desventaja: Se paga ligeramente más intereses totales.",
            "#3b82f6"
        )

        # 2. Avalanche
        self._create_method_card(
            methods_frame, 1,
            "2. Método Avalancha",
            "Prioridad: Mayor tasa de interés",
            f"Meses estimados: ~{max(1, int(total_deuda / max(1, extra + 25000)))} meses",
            "✅ Ventaja: Maximiza el ahorro matemático en intereses financieros.\n❌ Desventaja: Requiere disciplina si la deuda con más interés es grande.",
            "#10b981"
        )

        # 3. Hybrid
        self._create_method_card(
            methods_frame, 2,
            "3. Método Híbrido (Recomendado)",
            "Liquida la deuda más chica y luego la más cara",
            f"Meses estimados: ~{max(1, int(total_deuda / max(1, extra + 22000)))} meses",
            "✅ Ventaja: Combina la victoria psicológica inicial con la optimización de tasas.\n✅ Recomendado para tu estructura de gastos.",
            "#8b5cf6"
        )

    def _create_method_card(self, parent, col, title, sub, meses, desc, color):
        card = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=10)
        card.grid(row=0, column=col, sticky="nsew", padx=6, pady=5)

        ctk.CTkLabel(card, text=title, font=FONT_BODY_BOLD, text_color=color).pack(anchor="w", padx=12, pady=(12, 2))
        ctk.CTkLabel(card, text=sub, font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w", padx=12, pady=(0, 6))
        ctk.CTkLabel(card, text=meses, font=FONT_HEADER, text_color=TEXT_MAIN).pack(anchor="w", padx=12, pady=(0, 6))
        ctk.CTkLabel(card, text=desc, font=FONT_SMALL, text_color=TEXT_MAIN, wraplength=260, justify="left").pack(anchor="w", padx=12, pady=(0, 12))

    # ==========================================
    # 3. REGLA 50/30/20
    # ==========================================
    def _build_503020_tab(self):
        container = ctk.CTkScrollableFrame(self.tab_503020, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(container, text="Presupuesto Adaptado: Regla 50 / 30 / 20", font=FONT_HEADER, text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            container,
            text="Distribuye tus ingresos netos en proporciones saludables para no ahogarte con gastos fijos.",
            font=FONT_BODY,
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        # Dynamic breakdown based on user's recent average income
        summary = self.db.get_monthly_summary(2026, 11)
        ingreso = summary["ingreso"] if summary["ingreso"] > 0 else 1300000.0

        p50 = ingreso * 0.50
        p30 = ingreso * 0.30
        p20 = ingreso * 0.20

        cards_frame = ctk.CTkFrame(container, fg_color="transparent")
        cards_frame.pack(fill="x", pady=5)
        cards_frame.grid_columnconfigure((0, 1, 2), weight=1, uniform="r50")

        self._create_50_card(cards_frame, 0, "50% Esenciales", format_currency(p50), "Alquiler, Servicios, Supermercado, Transporte, Salud.", "#3b82f6")
        self._create_50_card(cards_frame, 1, "30% Personales / Deseo", format_currency(p30), "Salidas, Fulvo, Delivery, Compras, Hobbies.", "#f59e0b")
        self._create_50_card(cards_frame, 2, "20% Ahorro & Deuda", format_currency(p20), "Fondo de emergencia, Ahorro en USD, Pago acelerado.", "#10b981")

        # 5 polite refusal scripts requested by user
        box_scripts = ctk.CTkFrame(container, fg_color="#1e293b", corner_radius=10)
        box_scripts.pack(fill="x", pady=15)
        ctk.CTkLabel(box_scripts, text="💬 5 Respuestas Amables para Rechazar Gastos Fuera de Presupuesto:", font=FONT_HEADER, text_color="#38bdf8").pack(anchor="w", padx=15, pady=(12, 6))
        
        scripts = [
            "1. '¡Me encantaría sumarme, pero este mes ya alcancé el tope de mi presupuesto para salidas. ¿Lo dejamos para el próximo?'",
            "2. 'Tengo una meta de ahorro fija este mes que no puedo descuidar, pero los acompaño a tomar unos mates o plan tranqui.'",
            "3. 'Por ahora paso porque estoy cuidando los números, ¡pero pásenla de diez y nos vemos en la próxima!'",
            "4. 'No me da el presupuesto para esa salida en particular, ¿qué les parece si hacemos una comida en casa que sale mucho más accesible?'",
            "5. 'Estoy en un reto de 30 días sin compras impulsivas y me está funcionando genial, así que por esta vuelta me guardo.'"
        ]
        for s in scripts:
            ctk.CTkLabel(box_scripts, text=s, font=FONT_BODY, text_color=TEXT_MAIN, wraplength=780, justify="left").pack(anchor="w", padx=15, pady=3)
        ctk.CTkLabel(box_scripts, text="", height=8).pack()

        # Routine 15 mins
        box_routine = ctk.CTkFrame(container, fg_color="#0f172a", corner_radius=10)
        box_routine.pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(box_routine, text="⏱️ Rutina Semanal de 15 Minutos:", font=FONT_BODY_BOLD, text_color=COLOR_SUCCESS).pack(anchor="w", padx=15, pady=(10, 4))
        ctk.CTkLabel(
            box_routine,
            text="• Min 1-5: Entrar a Controlito y registrar los tickets/gastos de la semana.\n• Min 6-10: Comparar el gasto semanal con el límite del presupuesto mensual.\n• Min 11-15: Si alguna categoría se desvió, ajustar las compras no esenciales de la semana siguiente.",
            font=FONT_BODY,
            text_color=TEXT_MUTED,
            justify="left"
        ).pack(anchor="w", padx=15, pady=(0, 10))

    def _create_50_card(self, parent, col, title, amount, desc, color):
        card = ctk.CTkFrame(parent, fg_color="#1e293b", corner_radius=10)
        card.grid(row=0, column=col, sticky="nsew", padx=6, pady=5)
        ctk.CTkLabel(card, text=title, font=FONT_HEADER, text_color=color).pack(anchor="w", padx=12, pady=(10, 2))
        ctk.CTkLabel(card, text=amount, font=("Segoe UI", 18, "bold"), text_color=TEXT_MAIN).pack(anchor="w", padx=12, pady=(0, 4))
        ctk.CTkLabel(card, text=desc, font=FONT_SMALL, text_color=TEXT_MUTED, wraplength=240, justify="left").pack(anchor="w", padx=12, pady=(0, 10))

    # ==========================================
    # 4. FUENTES DE INGRESO (12 MESES)
    # ==========================================
    def _build_ingresos_tab(self):
        container = ctk.CTkScrollableFrame(self.tab_ingresos, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(container, text="Hoja de Ruta de 12 Meses: Diversificación de Ingresos", font=FONT_HEADER, text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            container,
            text="Objetivo: No depender de un único salario y construir fuentes paralelas sostenibles.",
            font=FONT_BODY,
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        alternatives = [
            ("1. Servicios Freelance / Independientes", "Bajo", "Bajo ($0 - $10k)", "4-6 hrs/sem", "Alta (corto plazo)", "Habilidades técnicas, portfolio"),
            ("2. Negocios Digitales & Afiliados", "Medio", "Bajo ($10k - $30k)", "5-8 hrs/sem", "Media (3-6 meses)", "Copywriting, redes sociales"),
            ("3. Venta de Bienes / E-commerce secundario", "Medio", "Medio ($50k - $150k)", "3-5 hrs/sem", "Media a Alta", "Gestión de inventario y envíos"),
            ("4. Inversiones de Renta Fija & Cedears", "Bajo a Medio", "Capital disponible", "1 hr/mes", "Predecible (interés compuesto)", "Análisis básico de mercado"),
            ("5. Alquileres / Renta de Activos", "Bajo", "Alto", "Bajo", "Estable (largo plazo)", "Gestión de propiedades")
        ]

        for title, riesgo, cap, tiempo, potencial, habs in alternatives:
            card = ctk.CTkFrame(container, fg_color="#1e293b", corner_radius=10)
            card.pack(fill="x", pady=5)

            ctk.CTkLabel(card, text=title, font=FONT_BODY_BOLD, text_color=COLOR_PRIMARY).pack(anchor="w", padx=12, pady=(8, 2))
            info = f"• Riesgo: {riesgo} | • Capital inicial: {cap} | • Tiempo necesario: {tiempo} | • Potencial: {potencial}\n• Habilidades: {habs}"
            ctk.CTkLabel(card, text=info, font=FONT_SMALL, text_color=TEXT_MUTED, justify="left").pack(anchor="w", padx=12, pady=(0, 8))

    # ==========================================
    # 5. HÁBITOS & RETO 30 DÍAS
    # ==========================================
    def _build_habitos_tab(self):
        container = ctk.CTkScrollableFrame(self.tab_habitos, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(container, text="Entrenador de Hábitos: Reto de 30 Días para Reducir Compras Impulsivas", font=FONT_HEADER, text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 5))

        habits = [
            ("1. Regla de las 72 Horas", "Antes de cualquier compra no esencial superior a $10.000, espera 72 horas obligatorias. El 70% del deseo impulsivo desaparece."),
            ("2. Experimento Débito / Efectivo", "Evita pagar gastos de consumo diario con tarjeta de crédito durante 30 días para sentir el impacto real del gasto en tu cuenta bancaria."),
            ("3. Auditoría de Suscripciones", "Revisa todas las plataformas (Rappi Prime, Netflix, Spotify, Discord, etc.). Cancela al menos 1 que no uses semanalmente."),
            ("4. Identificar Desencadenantes de Compra", "Detecta si compras por aburrimiento, estrés laboral o salidas espontáneas. Sustituye la recompensa por una actividad sin costo."),
            ("5. Monitoreo Diario en Controlito", "Tómate 2 minutos al final del día para cargar cualquier gasto que hayas tenido.")
        ]

        for title, desc in habits:
            card = ctk.CTkFrame(container, fg_color="#1e293b", corner_radius=8)
            card.pack(fill="x", pady=4)
            ctk.CTkLabel(card, text=title, font=FONT_BODY_BOLD, text_color=COLOR_SUCCESS).pack(anchor="w", padx=12, pady=(8, 2))
            ctk.CTkLabel(card, text=desc, font=FONT_BODY, text_color=TEXT_MUTED, wraplength=780, justify="left").pack(anchor="w", padx=12, pady=(0, 8))

    # ==========================================
    # 6. FONDO DE EMERGENCIA
    # ==========================================
    def _build_ahorro_tab(self):
        container = ctk.CTkScrollableFrame(self.tab_ahorro, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(container, text="Sistema de Ahorro Escalonado & Fondo de Emergencia", font=FONT_HEADER, text_color=TEXT_MAIN).pack(anchor="w", pady=(0, 5))
        ctk.CTkLabel(
            container,
            text="Construye tu tranquilidad financiera paso a paso sin comprometer tus necesidades básicas.",
            font=FONT_BODY,
            text_color=TEXT_MUTED
        ).pack(anchor="w", pady=(0, 10))

        steps = [
            ("Etapa 1: Fondo Inicial de Emergencia ($1.000 USD / Equivalente)", "Tu primer salvavidas para evitar endeudarte ante imprevistos (arreglo del auto, urgencia médica, rotura de electrodoméstico). Tienes parte de este fondo en tus Ahorros USD."),
            ("Etapa 2: Cobertura de 3 a 6 Meses de Gastos Esenciales", "Cálculo: Multiplica tu gasto fijo mensual (Alquiler + Servicios + Comida) por 3 o 6 meses. Mantener en cuenta remunerada de bajo riesgo o dólar billete / MEP."),
            ("Etapa 3: Automatización del Ahorro", "Programa una transferencia automática el día que cobras el sueldo ('Págate a ti mismo primero'). Lo que no ves en la cuenta de gastos diarios, no te lo gastas.")
        ]

        for title, desc in steps:
            card = ctk.CTkFrame(container, fg_color="#1e293b", corner_radius=10)
            card.pack(fill="x", pady=6)
            ctk.CTkLabel(card, text=f"🛡️ {title}", font=FONT_BODY_BOLD, text_color="#38bdf8").pack(anchor="w", padx=15, pady=(10, 3))
            ctk.CTkLabel(card, text=desc, font=FONT_BODY, text_color=TEXT_MAIN, wraplength=780, justify="left").pack(anchor="w", padx=15, pady=(0, 10))
