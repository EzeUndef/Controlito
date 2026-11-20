"""Conversational AI / NLP Engine for Controlito internal database."""
import re
from datetime import datetime
from utils.helpers import format_currency, format_date, mes_nombre, mes_numero, MESES


class FinancialChatEngine:
    """Interprets natural language queries and responds with concrete data from SQLite."""

    def __init__(self, db):
        self.db = db

    def process_query(self, query):
        q = query.lower().strip()

        # 1. Available money / Current balance
        if any(kw in q for kw in ["plata tengo ahora", "saldo actual", "cuanta plata", "cuanto tengo", "dinero tengo", "disponible tengo"]):
            return self._handle_current_balance()

        # 2. Opportunities of improvement / Where to save
        if any(kw in q for kw in ["oportunidad", "mejora", "recortar", "ahorrar mas", "donde gasto mas", "gasto al pedo", "fuga"]):
            return self._handle_improvement_opportunities()

        # 3. Why did I spend more on TC / Credit Card comparison
        if any(kw in q for kw in ["gaste mas en tc", "tarjeta que el mes", "gaste en tc", "aumento tc", "subio la tarjeta"]):
            return self._handle_tc_comparison()

        # 4. Comparative table / chart
        if any(kw in q for kw in ["cuadro comparativo", "comparativo de gastos", "comparar meses", "comparar gastos"]):
            return self._handle_comparative_table()

        # 5. Search specific purchase ("que dia gaste en...", "cuando compre...")
        search_kw = self._extract_search_keyword(q)
        if search_kw:
            return self._handle_search_item(search_kw)

        # 6. Specific month expenses
        month_query = self._extract_month_query(q)
        if month_query:
            return self._handle_month_summary(month_query)

        # 7. Services inquiry (Luz, gas, agua, cable) - check as whole words to avoid matching 'gaste'
        if any(re.search(rf'\b{kw}\b', q) for kw in ["luz", "gas", "agua", "cable", "internet", "fibertel"]):
            return self._handle_services_query(q)

        # 8. Savings in USD
        if any(kw in q for kw in ["dolar", "dolares", "usd", "ahorro usd"]):
            return self._handle_savings_query()

        # 9. Fallback general search in description
        words = [w for w in re.findall(r'\b\w+\b', q) if len(w) > 3 and w not in ["gaste", "plata", "cuanto", "cuando", "donde", "mostrar", "mostrame", "tengo"]]
        if words:
            for w in words:
                res = self._handle_search_item(w)
                if not res.startswith("No encontré"):
                    return res

        # Default help answer
        return (
            "🤖 **No entendí del todo tu consulta, pero puedes preguntarme cosas como:**\n\n"
            "• *'¿Cuánta plata tengo ahora?'*\n"
            "• *'¿Cuánto gasté en el mes?'*\n"
            "• *'¿Qué día gasté en comprar zapatillas / uber / super?'*\n"
            "• *'¿Por qué gasté más en TC que el mes pasado?'*\n"
            "• *'Dame oportunidades de mejora y ahorro'*\n"
            "• *'Mostrame un cuadro comparativo de gastos'*\n"
            "• *'¿Cuánto pagué de luz o servicios?'*"
        )

    def _handle_current_balance(self):
        cur = self.db.get_current_available_money()
        savings = self.db.get_savings()
        usd_total = 0.0
        dolar_rate = 1525.0
        for s in savings:
            if s["moneda"] == "USD":
                usd_total = s["monto"]
                break
            if "cotización" in s["concepto"].lower() or "bna" in s["concepto"].lower():
                dolar_rate = s["monto"]

        pesos = cur["saldo"]
        total_usd_en_pesos = usd_total * dolar_rate
        total_patrimonio = pesos + total_usd_en_pesos

        return (
            f"💵 **Tu estado financiero actual:**\n\n"
            f"• **Saldo disponible en Pesos:** {format_currency(pesos)} *(remanente último mes activo {mes_nombre(cur['mes'])} {cur['anio']})*.\n"
            f"• **Ahorros en USD:** USD {usd_total:,.2f} *(aprox. {format_currency(total_usd_en_pesos)} a cotización ${dolar_rate:,.0f})*.\n"
            f"• **Patrimonio Líquido Total:** **{format_currency(total_patrimonio)}**.\n\n"
            f"💡 *Tip:* Para ver el desglose cuenta por cuenta, puedes pasar a **Modo Data > Bancos & Ahorros**."
        )

    def _handle_improvement_opportunities(self):
        repetitivos = self.db.get_gastos_repetitivos(limit=5)
        top_cats = self.db.get_top_gastos(limit=4)

        resp = "🎯 **Auditoría de Oportunidades de Mejora y Ahorro:**\n\n"

        if repetitivos:
            resp += "**1. Gastos Hormiga & Fugas Frecuentes detectadas:**\n"
            total_fugas = 0
            valid_reps = [r for r in repetitivos if r["descripcion"] and r["descripcion"].strip() and r["descripcion"] != "gastos del mes"]
            if not valid_reps:
                valid_reps = repetitivos
            for r in valid_reps[:3]:
                desc = r["descripcion"].strip() if r["descripcion"] else "Varios"
                anual = r["promedio"] * r["veces"] * 1.5
                total_fugas += anual
                resp += f"   • *{desc}* ({r['categoria']}): promedio {format_currency(r['promedio'])} x {r['veces']} veces. (Impacto anual proyectado: ~{format_currency(anual)})\n"
            resp += f"   👉 *Si optimizas o reduces a la mitad estas compras, ahorrarías aproximadamente **{format_currency(total_fugas/2)}** al año.*\n\n"

        if top_cats:
            resp += "**2. Principales Categorías donde se va tu dinero:**\n"
            for c in top_cats[:3]:
                resp += f"   • **{c['categoria']}**: {format_currency(c['total'])} acumulados.\n"
            resp += "\n"

        resp += (
            "**3. Recomendaciones Prácticas de Acción Inmediata:**\n"
            "   • **Regla de las 72 Horas:** Antes de comprar algo fuera de lo esencial mayor a $10.000, espera 3 días.\n"
            "   • **Tarjetas de Crédito:** Prioriza pagar el total de la liquidación para no generar intereses punitorios.\n"
            "   • **Servicios:** Recuerda que la Luz en algunos meses tuvo picos altos; revisa consumos de aire/calefacción."
        )
        return resp

    def _handle_tc_comparison(self):
        # Find the last 2 months with TC expenses
        rows = self.db.conn.execute("""
            SELECT anio, mes, SUM(gasto) as total_tc
            FROM transactions
            WHERE categoria LIKE '%tc%' OR categoria LIKE '%tarjeta%' OR descripcion LIKE '%tc%' OR descripcion LIKE '%tarjeta%'
            GROUP BY anio, mes
            ORDER BY anio DESC, mes DESC
            LIMIT 2
        """).fetchall()

        if len(rows) < 2:
            return "No tengo suficiente historial consecutivo de pagos de Tarjeta de Crédito para comparar."

        m_actual, m_ant = rows[0], rows[1]
        diff = m_actual["total_tc"] - m_ant["total_tc"]
        pct = (diff / m_ant["total_tc"]) * 100 if m_ant["total_tc"] > 0 else 0

        # Detailed transactions for current month TC
        txs = self.db.conn.execute("""
            SELECT descripcion, gasto FROM transactions
            WHERE anio=? AND mes=? AND (categoria LIKE '%tc%' OR categoria LIKE '%tarjeta%' OR descripcion LIKE '%tc%')
            ORDER BY gasto DESC LIMIT 4
        """, (m_actual["anio"], m_actual["mes"])).fetchall()

        resp = (
            f"💳 **Comparativa de Tarjeta de Crédito (TC):**\n\n"
            f"• **{mes_nombre(m_actual['mes'])} {m_actual['anio']}:** {format_currency(m_actual['total_tc'])}\n"
            f"• **{mes_nombre(m_ant['mes'])} {m_ant['anio']}:** {format_currency(m_ant['total_tc'])}\n\n"
        )

        if diff > 0:
            resp += f"📈 **Gastaste {format_currency(diff)} más (+{pct:.1f}%) que el mes anterior.**\n\n"
        else:
            resp += f"📉 **Gastaste {format_currency(abs(diff))} menos ({pct:.1f}%) que el mes anterior.**\n\n"

        if txs:
            resp += f"**Cargos destacados de {mes_nombre(m_actual['mes'])}:**\n"
            for t in txs:
                resp += f"• {t['descripcion']}: {format_currency(t['gasto'])}\n"

        return resp

    def _handle_comparative_table(self):
        # Compare top categories between last 2 active months
        months = self.db.conn.execute("""
            SELECT DISTINCT anio, mes FROM transactions 
            GROUP BY anio, mes HAVING SUM(gasto) > 0 
            ORDER BY anio DESC, mes DESC LIMIT 2
        """).fetchall()

        if len(months) < 2:
            return "Necesito al menos 2 meses con gastos registrados para armar un cuadro comparativo."

        m1, m2 = months[0], months[1]
        s1 = self.db.get_monthly_summary(m1["anio"], m1["mes"])
        s2 = self.db.get_monthly_summary(m2["anio"], m2["mes"])

        diff_gasto = s1["gasto"] - s2["gasto"]
        diff_ingreso = s1["ingreso"] - s2["ingreso"]

        table_str = (
            f"📊 **Cuadro Comparativo de Gastos e Ingresos:**\n\n"
            f"| Concepto | {mes_nombre(m2['mes'])} {m2['anio']} | {mes_nombre(m1['mes'])} {m1['anio']} | Variación |\n"
            f"| :--- | :--- | :--- | :--- |\n"
            f"| **Ingresos** | {format_currency(s2['ingreso'])} | {format_currency(s1['ingreso'])} | {format_currency(diff_ingreso)} |\n"
            f"| **Gastos** | {format_currency(s2['gasto'])} | {format_currency(s1['gasto'])} | {format_currency(diff_gasto)} |\n"
            f"| **Sobrante (Quedó)** | {format_currency(s2['balance'])} | {format_currency(s1['balance'])} | {format_currency(s1['balance'] - s2['balance'])} |\n\n"
        )

        if diff_gasto > 0:
            table_str += f"⚠️ En {mes_nombre(m1['mes'])} tus gastos aumentaron **{format_currency(diff_gasto)}** respecto al mes anterior."
        else:
            table_str += f"✅ En {mes_nombre(m1['mes'])} lograste reducir tus gastos en **{format_currency(abs(diff_gasto))}**."

        return table_str

    def _extract_search_keyword(self, q):
        patterns = [
            r'(?:que dia|cuando|que fecha|gast[eé] en|compr[eé]|pagu[eé])\s+(?:plata en|en comprar|en|plata por|por)\s+([a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+)',
            r'buscar\s+([a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+)',
            r'cuanto gast[eé] en\s+([a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+)',
            r'precio de\s+([a-zA-Z0-9áéíóúÁÉÍÓÚñÑ\s]+)'
        ]
        for p in patterns:
            m = re.search(p, q)
            if m:
                kw = m.group(1).strip()
                # Remove common noise words
                kw = re.sub(r'^(el|la|los|las|un|una|unos|unas)\s+', '', kw)
                if len(kw) >= 3:
                    return kw
        return None

    def _handle_search_item(self, keyword):
        rows = self.db.conn.execute("""
            SELECT fecha, categoria, descripcion, gasto, ingreso
            FROM transactions
            WHERE (descripcion LIKE ? OR categoria LIKE ?) AND (gasto > 0 OR ingreso > 0)
            ORDER BY fecha DESC LIMIT 5
        """, (f"%{keyword}%", f"%{keyword}%")).fetchall()

        if not rows:
            return f"🔍 No encontré ningún movimiento registrado con la palabra **'{keyword}'** en tu historial. ¿Podría figurar con otro nombre (ej: Supermercado, Bazar, etc.)?"

        resp = f"🔎 **Encontré los siguientes registros para '{keyword}':**\n\n"
        total = 0.0
        for r in rows:
            f_str = format_date(r["fecha"])
            monto_str = format_currency(r["gasto"] if r["gasto"] > 0 else r["ingreso"])
            tipo = "Gasto" if r["gasto"] > 0 else "Ingreso"
            resp += f"• **{f_str}** — {r['descripcion']} ({r['categoria']}): **{monto_str}** [{tipo}]\n"
            total += (r["gasto"] if r["gasto"] > 0 else 0)

        if len(rows) > 1 and total > 0:
            resp += f"\n💰 **Gasto total acumulado en '{keyword}':** {format_currency(total)}"

        return resp

    def _extract_month_query(self, q):
        for num, name in MESES.items():
            if name.lower() in q:
                # check year
                y_match = re.search(r'\b(202[2-9])\b', q)
                year = int(y_match.group(1)) if y_match else 2026
                return {"mes": num, "anio": year, "nombre": name}
        if "este mes" in q:
            return {"mes": datetime.now().month, "anio": 2026, "nombre": mes_nombre(datetime.now().month)}
        return None

    def _handle_month_summary(self, m_info):
        s = self.db.get_monthly_summary(m_info["anio"], m_info["mes"])
        if s["ingreso"] == 0 and s["gasto"] == 0:
            return f"Para **{m_info['nombre']} {m_info['anio']}** no se registran movimientos cargados aún."

        return (
            f"📅 **Resumen de {m_info['nombre']} {m_info['anio']}:**\n\n"
            f"• **Ingresos Totales:** {format_currency(s['ingreso'])}\n"
            f"• **Gastos Totales:** {format_currency(s['gasto'])}\n"
            f"• **Total que quedó (Sobrante):** **{format_currency(s['balance'])}** ({'Superávit ✅' if s['balance'] >= 0 else 'Déficit ⚠️'})\n"
        )

    def _handle_services_query(self, q):
        # Services latest
        rows = self.db.get_services(2026)
        if not rows:
            return "No hay registros de servicios cargados para el 2026."

        ultimo = rows[-1]
        return (
            f"⚡ **Estado de Servicios ({ultimo['mes']} {ultimo['anio']}):**\n\n"
            f"• **Gas:** {format_currency(ultimo['gas'])}\n"
            f"• **Agua:** {format_currency(ultimo['agua'])}\n"
            f"• **Luz:** {format_currency(ultimo['luz'])}\n"
            f"• **Cable / Internet:** {format_currency(ultimo['cable'])}\n"
            f"• **Total con Luz:** {format_currency(ultimo['total_con_luz'])}\n"
            f"• **Total sin Luz (efectivo):** {format_currency(ultimo['total_sin_luz'])}"
        )

    def _handle_savings_query(self):
        savings = self.db.get_savings()
        if not savings:
            return "No tienes registros de ahorros cargados."

        resp = "💵 **Tus Ahorros Registrados:**\n\n"
        for s in savings:
            sym = "USD" if s["moneda"] == "USD" else "$"
            resp += f"• **{s['concepto']}:** {sym} {s['monto']:,.2f}\n"
        return resp
