"""Helpers and utilities for Controlito."""
import locale
from datetime import datetime

MESES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

MESES_REV = {v.upper(): k for k, v in MESES.items()}

CATEGORY_COLORS = {
    "Sueldo": "#2ecc71", "Aguinaldo": "#27ae60", "Sobrante": "#1abc9c",
    "Devolución": "#16a085", "Devolucion": "#16a085",
    "Tarjeta Visa": "#e74c3c", "Tarjeta Amex": "#c0392b", "Tarjeta Master": "#e67e22",
    "TC": "#d35400",
    "Alquiler": "#9b59b6", "Internet": "#8e44ad", "Servicios": "#2980b9",
    "Supermercado": "#f39c12", "Delivery": "#e67e22", "Comida": "#d35400",
    "Carniceria/Verduleria": "#e74c3c",
    "Compras": "#3498db", "Salida": "#1abc9c", "Transporte": "#95a5a6",
    "Casino": "#e74c3c", "Gastos del mes": "#7f8c8d", "Fulvo": "#2ecc71",
    "Psicologo": "#9b59b6", "Impuestos": "#34495e", "Prestamo": "#c0392b",
    "Deuda en contra": "#e74c3c",
}

CATEGORY_GROUPS = {
    "Ingresos": ["Sueldo", "Aguinaldo", "Sobrante", "Devolución", "Devolucion", "Devolucion prestamo"],
    "Vivienda": ["Alquiler", "Servicios", "Internet", "Agua", "Gas", "Luz", "Cable"],
    "Alimentación": ["Supermercado", "Delivery", "Comida", "Carniceria/Verduleria"],
    "Transporte": ["Transporte"],
    "Tarjetas": ["Tarjeta Visa", "Tarjeta Amex", "Tarjeta Master", "TC"],
    "Entretenimiento": ["Salida", "Casino", "Fulvo", "Compras"],
    "Salud": ["Psicologo"],
    "Obligaciones": ["Impuestos", "Prestamo", "Deuda en contra"],
    "Otros": ["Gastos del mes"],
}


def format_currency(amount, symbol="$"):
    """Format number as currency."""
    if amount is None:
        return f"{symbol} 0"
    try:
        if abs(amount) >= 1_000_000:
            return f"{symbol} {amount:,.0f}"
        return f"{symbol} {amount:,.2f}"
    except (ValueError, TypeError):
        return f"{symbol} 0"


def format_date(date_str):
    """Format date string for display."""
    if isinstance(date_str, datetime):
        return date_str.strftime("%d/%m/%Y")
    try:
        dt = datetime.strptime(str(date_str).split(" ")[0], "%Y-%m-%d")
        return dt.strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return str(date_str)


def mes_nombre(num):
    """Get month name from number."""
    return MESES.get(num, f"Mes {num}")


def mes_numero(nombre):
    """Get month number from name."""
    return MESES_REV.get(nombre.upper().strip(), 0)


def get_color_for_category(cat):
    """Get color for a category."""
    return CATEGORY_COLORS.get(cat, "#3498db")


def get_group_for_category(cat):
    """Get group for a category."""
    for group, cats in CATEGORY_GROUPS.items():
        if cat in cats:
            return group
    return "Otros"


def parse_date_safe(val):
    """Safely parse various date formats."""
    if val is None:
        return None
    if isinstance(val, datetime):
        return val.date()
    s = str(val).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def calculate_percentage(part, total):
    """Calculate percentage safely."""
    if total == 0:
        return 0
    return round((part / total) * 100, 1)
