"""Category normalization and synonym unification engine for Controlito."""
import unicodedata

def _strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn').lower().strip()

CANONICAL_CATEGORIES = {
    "Supermercado & Alimentos": {
        "tipo": "gasto",
        "grupo": "Alimentación",
        "color": "#f59e0b",
        "synonyms": [
            "supermercado", "comida", "delivery", "carniceria/verduleria", "alimentos",
            "almacen", "verduleria", "carniceria", "super", "almacén", "verdulería", "carnicería"
        ]
    },
    "Tarjetas de Crédito": {
        "tipo": "gasto",
        "grupo": "Tarjetas & Finanzas",
        "color": "#ef4444",
        "synonyms": [
            "tc", "tarjeta visa", "tarjeta amex", "tarjeta master", "visa", "amex", "mastercard", "santander", "tarjeta de credito"
        ]
    },
    "Vivienda & Servicios": {
        "tipo": "gasto",
        "grupo": "Vivienda",
        "color": "#8b5cf6",
        "synonyms": [
            "alquiler", "servicios", "internet", "luz", "agua", "gas", "cable", "expensas"
        ]
    },
    "Transporte & Movilidad": {
        "tipo": "gasto",
        "grupo": "Transporte",
        "color": "#3b82f6",
        "synonyms": [
            "transporte", "combustible", "nafta", "uber", "sube", "taxi", "peaje", "estacionamiento", "remis"
        ]
    },
    "Salidas & Ocio": {
        "tipo": "gasto",
        "grupo": "Entretenimiento",
        "color": "#ec4899",
        "synonyms": [
            "salida", "salidas", "casino", "fulvo", "futbol", "navidad", "bares", "boliche", "cine", "recital"
        ]
    },
    "Compras & Personal": {
        "tipo": "gasto",
        "grupo": "Compras",
        "color": "#06b6d4",
        "synonyms": [
            "compras", "ropa", "indumentaria", "tecnología", "celular", "mercado libre", "calzado"
        ]
    },
    "Salud & Bienestar": {
        "tipo": "gasto",
        "grupo": "Salud",
        "color": "#10b981",
        "synonyms": [
            "psicologo", "psicólogo", "psicologo/psiquiatra", "psiquiatra", "gym", "gimnasio", "farmacia", "medicina", "dentista", "obra social"
        ]
    },
    "Sueldo & Honorarios": {
        "tipo": "ingreso",
        "grupo": "Ingresos",
        "color": "#10b981",
        "synonyms": [
            "sueldo", "salario", "honorarios", "haberes"
        ]
    },
    "Aguinaldo & Extras": {
        "tipo": "ingreso",
        "grupo": "Ingresos",
        "color": "#059669",
        "synonyms": [
            "aguinaldo", "bono", "extra", "premio"
        ]
    },
    "Reintegros & Devoluciones": {
        "tipo": "ambos",
        "grupo": "Ingresos",
        "color": "#14b8a6",
        "synonyms": [
            "devolucion", "devolución", "devolucion prestamo", "pago", "reintegro"
        ]
    },
    "Ahorro & Sobrante": {
        "tipo": "ambos",
        "grupo": "Ahorro",
        "color": "#6366f1",
        "synonyms": [
            "sobrante", "ahorro", "ahorros"
        ]
    },
    "Inversiones & Ventas": {
        "tipo": "ambos",
        "grupo": "Inversiones",
        "color": "#eab308",
        "synonyms": [
            "cedears", "venta", "ventas", "inversion", "cripto", "dolar", "dólar"
        ]
    },
    "Préstamos & Obligaciones": {
        "tipo": "ambos",
        "grupo": "Obligaciones",
        "color": "#dc2626",
        "synonyms": [
            "prestamo", "préstamo", "deuda en contra", "deuda", "cuotas"
        ]
    },
    "Impuestos & Tasas": {
        "tipo": "gasto",
        "grupo": "Obligaciones",
        "color": "#64748b",
        "synonyms": [
            "impuestos", "tasas", "afip", "arba", "abl", "rentas"
        ]
    },
    "Gastos Varios": {
        "tipo": "gasto",
        "grupo": "General",
        "color": "#94a3b8",
        "synonyms": [
            "gastos del mes", "sin categoría", "sin categoria", "varios", "otros", "general"
        ]
    }
}

# Precompile quick lookup table (clean string -> canonical category name)
_LOOKUP = {}
for canonical_name, data in CANONICAL_CATEGORIES.items():
    _LOOKUP[_strip_accents(canonical_name)] = canonical_name
    for syn in data["synonyms"]:
        _LOOKUP[_strip_accents(syn)] = canonical_name


def find_canonical_category(raw_category):
    """Maps any raw category string or synonym to its canonical unified category."""
    if not raw_category:
        return "Gastos Varios"
    cleaned = _strip_accents(str(raw_category))
    return _LOOKUP.get(cleaned, str(raw_category).strip())


def normalize_database_categories(db):
    """
    Normalizes and unifies all transactions and category records in the database.
    Replaces synonym variants with canonical categories and repopulates the categories table.
    Returns: (trans_updated_count, categories_consolidated_count)
    """
    cursor = db.conn.cursor()

    # 1. Update all transactions matching synonyms
    trans_updated = 0
    all_trans = cursor.execute("SELECT id, categoria FROM transactions").fetchall()
    for tid, old_cat in all_trans:
        canonical = find_canonical_category(old_cat)
        if canonical != old_cat:
            cursor.execute("UPDATE transactions SET categoria=? WHERE id=?", (canonical, tid))
            trans_updated += 1

    # 2. Rebuild the categories table cleanly with canonical categories + any custom non-matching ones
    cursor.execute("DELETE FROM categories")

    # Insert standard canonical categories first
    for cat_name, info in CANONICAL_CATEGORIES.items():
        cursor.execute(
            "INSERT OR IGNORE INTO categories (nombre, tipo, grupo, color) VALUES (?,?,?,?)",
            (cat_name, info["tipo"], info["grupo"], info["color"])
        )

    # Insert any other category currently present in transactions
    distinct_tx_cats = cursor.execute("SELECT DISTINCT categoria FROM transactions").fetchall()
    for row in distinct_tx_cats:
        c_name = row[0]
        if c_name not in CANONICAL_CATEGORIES:
            cursor.execute(
                "INSERT OR IGNORE INTO categories (nombre, tipo, grupo, color) VALUES (?,?,?,?)",
                (c_name, "ambos", "General", "#38bdf8")
            )

    db.conn.commit()

    total_categories = cursor.execute("SELECT COUNT(*) FROM categories").fetchone()[0]
    return trans_updated, total_categories
