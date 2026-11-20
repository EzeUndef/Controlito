"""Excel importer for Controlito - reads the user's Excel format."""
import openpyxl
from datetime import datetime, date
from utils.category_normalizer import find_canonical_category


MONTH_NAMES = {
    "ENERO": 1, "FEBRERO": 2, "MARZO": 3, "ABRIL": 4,
    "MAYO": 5, "JUNIO": 6, "JULIO": 7, "AGOSTO": 8,
    "SEPTIEMBRE": 9, "OCTUBRE": 10, "NOVIEMBRE": 11, "DICIEMBRE": 12
}

SERVICE_MONTH_MAP_H1 = {
    "B": "ENERO", "D": "FEBRERO", "F": "MARZO", "H": "ABRIL", "J": "MAYO", "L": "JUNIO"
}
SERVICE_MONTH_MAP_H2 = {
    "B": "JULIO", "D": "AGOSTO", "F": "SEPTIEMBRE", "H": "OCTUBRE", "J": "NOVIEMBRE", "L": "DICIEMBRE"
}


def _safe_float(val):
    if val is None:
        return 0.0
    try:
        s = str(val).replace("$", "").replace(",", "").replace("-", "0").strip()
        if s in ("", "$ -"):
            return 0.0
        return float(s)
    except (ValueError, TypeError):
        return 0.0


def _parse_date(val, year, month):
    """Parse date from Excel cell; might be datetime, number (day), or string."""
    if val is None:
        return None
    if isinstance(val, datetime):
        if val.year < 2000:
            try:
                return date(year, month, val.day)
            except (ValueError, AttributeError):
                return date(year, month, 1)
        return val.date()
    if isinstance(val, date):
        return val
    try:
        day = int(float(str(val)))
        if 1 <= day <= 31:
            try:
                return date(year, month, day)
            except ValueError:
                return date(year, month, 1)
    except (ValueError, TypeError):
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(str(val), fmt).date()
        except ValueError:
            continue
    return None


def _detect_month_from_header(ws, col, row=1):
    """Detect month name from header row."""
    val = ws.cell(row=row, column=col).value
    if val is None:
        return None
    text = str(val).upper().strip()
    for prefix in ("GASTOS ", ""):
        for name, num in MONTH_NAMES.items():
            if name in text.replace(prefix, "").strip():
                return num
    return None


def import_transactions_sheet(db, ws, year):
    """Import a yearly transactions sheet (2022-2028 format)."""
    max_col = ws.max_column
    max_row = ws.max_row

    # Detect month blocks by scanning row 1 or row 2 for month names
    month_blocks = []
    col = 1
    while col <= max_col:
        # Check row 1 for month header
        h1 = ws.cell(row=1, column=col).value
        if h1 is not None:
            month_text = str(h1).upper().strip()
            month_num = None
            for name, num in MONTH_NAMES.items():
                if name in month_text:
                    month_num = num
                    break
            if month_num is not None:
                # Determine block width by checking row 2 headers
                # Check if this block has 5 cols (Fecha,Cat,Desc,Ing,Gas) or 4 cols (Fecha,Desc,Ing,Gas)
                h2_next = ws.cell(row=2, column=col + 1).value
                if h2_next and str(h2_next).strip().lower() in ("categoria", "categoría"):
                    # 5-column format: Fecha, Categoria, Descripcion, Ingreso, Gastos
                    month_blocks.append({
                        "month": month_num, "start_col": col, "width": 5,
                        "has_category": True
                    })
                    col += 5
                    continue
                else:
                    # 4-column format: Fecha, Descripcion, Ingreso, Gastos
                    month_blocks.append({
                        "month": month_num, "start_col": col, "width": 4,
                        "has_category": False
                    })
                    col += 4
                    continue
        # Also check if col header in row 1 starts with a letter that might be month
        # For sheets like 2025+ where row 1 has month names starting at different cols
        col += 1

    if not month_blocks:
        # Fallback: check if row 1 has "c" or similar short names, try row 1 values
        col = 1
        while col <= max_col:
            r1 = ws.cell(row=1, column=col).value
            if r1 is not None:
                r1_str = str(r1).upper().strip()
                for name, num in MONTH_NAMES.items():
                    if r1_str == name or name in r1_str:
                        h2_next = ws.cell(row=2, column=col + 1).value
                        if h2_next and str(h2_next).strip().lower() in ("categoria", "categoría"):
                            month_blocks.append({"month": num, "start_col": col, "width": 5, "has_category": True})
                        else:
                            month_blocks.append({"month": num, "start_col": col, "width": 4, "has_category": False})
                        break
            col += 1

    count = 0
    for block in month_blocks:
        sc = block["start_col"]
        m = block["month"]
        has_cat = block["has_category"]

        for row_idx in range(3, max_row + 1):
            fecha_val = ws.cell(row=row_idx, column=sc).value

            # Skip summary rows
            if fecha_val is not None:
                s = str(fecha_val).upper().strip()
                if any(kw in s for kw in ["FIN DE MES", "TOTAL", "A PAGAR", "QUEDO"]):
                    continue

            dt = _parse_date(fecha_val, year, m)
            if dt is None:
                continue

            if has_cat:
                cat = ws.cell(row=row_idx, column=sc + 1).value
                desc = ws.cell(row=row_idx, column=sc + 2).value
                ing = _safe_float(ws.cell(row=row_idx, column=sc + 3).value)
                gas = _safe_float(ws.cell(row=row_idx, column=sc + 4).value)
            else:
                cat = None
                desc = ws.cell(row=row_idx, column=sc + 1).value
                ing = _safe_float(ws.cell(row=row_idx, column=sc + 2).value)
                gas = _safe_float(ws.cell(row=row_idx, column=sc + 3).value)

            if desc is None and ing == 0 and gas == 0:
                continue

            # Infer category from description if not present
            if not cat and desc:
                cat = _infer_category(str(desc))
            elif not cat:
                cat = "Sin categoría"

            cat = str(cat).strip() if cat else "Sin categoría"
            cat = find_canonical_category(cat)
            desc = str(desc).strip() if desc else ""

            db.add_transaction(dt, cat, desc, ing, gas)
            count += 1

    return count


def _infer_category(desc):
    """Infer category from description text."""
    d = desc.lower()
    mappings = [
        (["sueldo"], "Sueldo"),
        (["aguinaldo"], "Aguinaldo"),
        (["sobr"], "Sobrante"),
        (["tc", "tarjeta", "visa", "amex", "master"], "TC"),
        (["alquiler"], "Alquiler"),
        (["internet", "wifi"], "Internet"),
        (["super", "superduper"], "Supermercado"),
        (["delivery", "rappi"], "Delivery"),
        (["salida", "joda", "finde"], "Salida"),
        (["uber", "sube", "transporte"], "Transporte"),
        (["gas "], "Servicios"),
        (["agua"], "Servicios"),
        (["luz"], "Servicios"),
        (["cable"], "Servicios"),
        (["farmacia"], "Compras"),
        (["compra", "compre"], "Compras"),
        (["pelu"], "Gastos del mes"),
        (["desayuno", "almuerzo", "comida", "panaderia", "cafeteria"], "Comida"),
        (["casino", "timba"], "Casino"),
        (["fulvo"], "Fulvo"),
        (["psicologo", "psico"], "Psicologo"),
        (["prestamo", "preste"], "Prestamo"),
        (["devol"], "Devolucion"),
        (["gasto"], "Gastos del mes"),
    ]
    for keywords, category in mappings:
        for kw in keywords:
            if kw in d:
                return category
    return "Gastos del mes"


def import_services_sheet(db, ws, year):
    """Import services sheet (Servicios 2025/2026/2027 format)."""
    count = 0

    # First half: rows 2-8, cols B-L (Enero-Junio)
    for col_letter, month_name in SERVICE_MONTH_MAP_H1.items():
        col_idx = openpyxl.utils.column_index_from_string(col_letter)
        month_num = MONTH_NAMES[month_name]
        prorrateo_col = col_idx + 1

        gas = _safe_float(ws.cell(row=3, column=col_idx).value)
        gas_p = _safe_float(ws.cell(row=3, column=prorrateo_col).value)
        agua = _safe_float(ws.cell(row=4, column=col_idx).value)
        agua_p = _safe_float(ws.cell(row=4, column=prorrateo_col).value)
        luz = _safe_float(ws.cell(row=5, column=col_idx).value)
        luz_p = _safe_float(ws.cell(row=5, column=prorrateo_col).value)
        cable = _safe_float(ws.cell(row=6, column=col_idx).value)
        cable_p = _safe_float(ws.cell(row=6, column=prorrateo_col).value)
        total_sin = _safe_float(ws.cell(row=7, column=col_idx).value)
        total_con = _safe_float(ws.cell(row=8, column=col_idx).value)

        if any(v > 0 for v in [gas, agua, luz, cable]):
            db.add_service(year, month_name, month_num, 4, gas, gas_p, agua, agua_p, luz, luz_p, cable, cable_p, total_sin, total_con)
            count += 1

    # Second half: rows 10-15, cols B-L (Julio-Diciembre)
    for col_letter, month_name in SERVICE_MONTH_MAP_H2.items():
        col_idx = openpyxl.utils.column_index_from_string(col_letter)
        month_num = MONTH_NAMES[month_name]
        prorrateo_col = col_idx + 1

        gas = _safe_float(ws.cell(row=10, column=col_idx).value)
        gas_p = _safe_float(ws.cell(row=10, column=prorrateo_col).value)
        agua = _safe_float(ws.cell(row=11, column=col_idx).value)
        agua_p = _safe_float(ws.cell(row=11, column=prorrateo_col).value)
        luz = _safe_float(ws.cell(row=12, column=col_idx).value)
        luz_p = _safe_float(ws.cell(row=12, column=prorrateo_col).value)
        cable = _safe_float(ws.cell(row=13, column=col_idx).value)
        cable_p = _safe_float(ws.cell(row=13, column=prorrateo_col).value)
        total_sin = _safe_float(ws.cell(row=14, column=col_idx).value)
        total_con = _safe_float(ws.cell(row=15, column=col_idx).value)

        if any(v > 0 for v in [gas, agua, luz, cable]):
            db.add_service(year, month_name, month_num, 4, gas, gas_p, agua, agua_p, luz, luz_p, cable, cable_p, total_sin, total_con)
            count += 1

    return count


def import_services_2025(db, ws):
    """Import Servicios 2025 which has a different format (7 rows, N cols)."""
    count = 0
    # Row 2 has month names, services in cols B onwards paired (value, prorrateo)
    # Format: B=JUNIO, D=JULIO, F=AGOSTO, H=SEPTIEMBRE, J=OCTUBRE, L=NOVIEMBRE, N=DICIEMBRE
    month_cols_2025 = {"B": "JUNIO", "D": "JULIO", "F": "AGOSTO", "H": "SEPTIEMBRE", "J": "OCTUBRE", "L": "NOVIEMBRE", "N": "DICIEMBRE"}

    for col_letter, month_name in month_cols_2025.items():
        col_idx = openpyxl.utils.column_index_from_string(col_letter)
        month_num = MONTH_NAMES[month_name]
        prorrateo_col = col_idx + 1

        gas = _safe_float(ws.cell(row=3, column=col_idx).value)
        gas_p = _safe_float(ws.cell(row=3, column=prorrateo_col).value)
        agua = _safe_float(ws.cell(row=4, column=col_idx).value)
        agua_p = _safe_float(ws.cell(row=4, column=prorrateo_col).value)
        luz = _safe_float(ws.cell(row=5, column=col_idx).value)
        luz_p = _safe_float(ws.cell(row=5, column=prorrateo_col).value)
        cable = _safe_float(ws.cell(row=6, column=col_idx).value)
        cable_p = _safe_float(ws.cell(row=6, column=prorrateo_col).value)
        total = _safe_float(ws.cell(row=7, column=col_idx).value)

        if any(v > 0 for v in [gas, agua, luz, cable]):
            db.add_service(2025, month_name, month_num, 4, gas, gas_p, agua, agua_p, luz, luz_p, cable, cable_p, total, total)
            count += 1

    return count


def import_bank_accounts(db, ws):
    """Import bank accounts from Banco-Ahorros sheet."""
    count = 0
    for row_idx in range(3, 8):
        banco = ws.cell(row=row_idx, column=1).value
        if banco is None:
            continue
        alias = ws.cell(row=row_idx, column=2).value or ""
        motivo = ws.cell(row=row_idx, column=4).value or ""
        cvu = ws.cell(row=row_idx, column=5).value or ""
        db.add_bank_account(str(banco), str(alias), str(motivo), str(cvu))
        count += 1

    # Import savings
    usd_total = _safe_float(ws.cell(row=10, column=4).value)
    usd_gastos = _safe_float(ws.cell(row=11, column=4).value)
    usd_rest = _safe_float(ws.cell(row=12, column=4).value)
    dolar_bna = _safe_float(ws.cell(row=13, column=4).value)

    if usd_total > 0:
        db.add_saving("Total ahorro USD", usd_total, "USD")
    if usd_gastos > 0:
        db.add_saving("Gastos en USD", usd_gastos, "USD")
    if usd_rest > 0:
        db.add_saving("Restante USD", usd_rest, "USD")
    if dolar_bna > 0:
        db.add_saving("Cotización Dólar BNA", dolar_bna, "ARS")

    return count


def import_excel(db, filepath, progress_callback=None):
    """Import all data from Excel file."""
    wb = openpyxl.load_workbook(filepath, data_only=True)
    results = {}

    # Clear existing data
    db.clear_all_data()

    total_steps = len(wb.sheetnames)
    current = 0

    # Import yearly transaction sheets
    year_sheets = ["2022", "2023", "2024", "2025", "2026", "2027", "2028"]
    for sheet_name in year_sheets:
        if sheet_name in wb.sheetnames:
            ws = wb[sheet_name]
            year = int(sheet_name)
            count = import_transactions_sheet(db, ws, year)
            results[sheet_name] = count
            current += 1
            if progress_callback:
                progress_callback(current / total_steps, f"Importando {sheet_name}... ({count} registros)")

    # Import services
    if "Servicios 2025" in wb.sheetnames:
        count = import_services_2025(db, wb["Servicios 2025"])
        results["Servicios 2025"] = count
        current += 1
        if progress_callback:
            progress_callback(current / total_steps, f"Servicios 2025... ({count})")

    for year in [2026, 2027]:
        sheet_name = f"Servicios {year}"
        if sheet_name in wb.sheetnames:
            count = import_services_sheet(db, wb[sheet_name], year)
            results[sheet_name] = count
            current += 1
            if progress_callback:
                progress_callback(current / total_steps, f"{sheet_name}... ({count})")

    # Import bank accounts
    if "Banco-Ahorros" in wb.sheetnames:
        count = import_bank_accounts(db, wb["Banco-Ahorros"])
        results["Banco-Ahorros"] = count
        current += 1
        if progress_callback:
            progress_callback(current / total_steps, f"Banco-Ahorros... ({count})")

    # Normalize and canonicalize all categories
    db.normalize_categories()

    if progress_callback:
        progress_callback(1.0, "¡Importación completa!")

    wb.close()
    return results
