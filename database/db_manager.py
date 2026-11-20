import sqlite3
import os
from datetime import datetime


class DatabaseManager:
    """Manages SQLite database for Controlito."""

    def __init__(self, db_path=None):
        if db_path is None:
            app_data = os.path.join(os.path.expanduser("~"), ".controlito")
            os.makedirs(app_data, exist_ok=True)
            db_path = os.path.join(app_data, "controlito.db")
        self.db_path = db_path
        self.conn = None
        self.connect()
        self.create_tables()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self.conn.execute("PRAGMA secure_delete=ON")

    def close(self):
        if self.conn:
            self.conn.close()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL,
                tipo TEXT CHECK(tipo IN ('ingreso', 'gasto', 'ambos')) DEFAULT 'ambos',
                grupo TEXT DEFAULT 'General',
                color TEXT DEFAULT '#3498db'
            );

            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha DATE NOT NULL,
                categoria TEXT NOT NULL DEFAULT 'Sin categoría',
                descripcion TEXT,
                ingreso REAL DEFAULT 0,
                gasto REAL DEFAULT 0,
                mes INTEGER NOT NULL,
                anio INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS services (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                anio INTEGER NOT NULL,
                mes TEXT NOT NULL,
                mes_num INTEGER NOT NULL,
                personas INTEGER DEFAULT 4,
                gas REAL DEFAULT 0,
                gas_prorrateo REAL DEFAULT 0,
                agua REAL DEFAULT 0,
                agua_prorrateo REAL DEFAULT 0,
                luz REAL DEFAULT 0,
                luz_prorrateo REAL DEFAULT 0,
                cable REAL DEFAULT 0,
                cable_prorrateo REAL DEFAULT 0,
                total_sin_luz REAL DEFAULT 0,
                total_con_luz REAL DEFAULT 0,
                UNIQUE(anio, mes_num)
            );

            CREATE TABLE IF NOT EXISTS bank_accounts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                banco TEXT NOT NULL,
                alias TEXT,
                motivo TEXT,
                cvu_cbu TEXT
            );

            CREATE TABLE IF NOT EXISTS savings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                concepto TEXT NOT NULL,
                monto REAL DEFAULT 0,
                moneda TEXT DEFAULT 'ARS',
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS budget_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mes INTEGER NOT NULL,
                anio INTEGER NOT NULL,
                categoria_grupo TEXT NOT NULL,
                categoria TEXT NOT NULL,
                monto REAL DEFAULT 0,
                UNIQUE(mes, anio, categoria_grupo, categoria)
            );

            CREATE TABLE IF NOT EXISTS app_settings (
                key TEXT PRIMARY KEY,
                value TEXT
            );

            CREATE INDEX IF NOT EXISTS idx_trans_fecha ON transactions(fecha);
            CREATE INDEX IF NOT EXISTS idx_trans_anio_mes ON transactions(anio, mes);
            CREATE INDEX IF NOT EXISTS idx_trans_categoria ON transactions(categoria);
            CREATE INDEX IF NOT EXISTS idx_services_anio ON services(anio);
        """)
        self.conn.commit()

        # Automatic schema migration for existing databases
        try:
            self.conn.execute("ALTER TABLE services ADD COLUMN personas INTEGER DEFAULT 4")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # column already exists

    VALID_ORDER_COLS = {
        "id": "id",
        "fecha": "fecha",
        "categoria": "categoria",
        "descripcion": "descripcion",
        "ingreso": "ingreso",
        "gasto": "gasto"
    }

    VALID_SERVICE_FIELDS = {
        "personas", "gas", "gas_prorrateo", "agua", "agua_prorrateo",
        "luz", "luz_prorrateo", "cable", "cable_prorrateo",
        "total_sin_luz", "total_con_luz"
    }

    # === TRANSACTIONS ===
    def add_transaction(self, fecha, categoria, descripcion, ingreso=0, gasto=0):
        if isinstance(fecha, str):
            fecha = datetime.strptime(str(fecha)[:10], "%Y-%m-%d").date()
        mes = fecha.month
        anio = fecha.year
        # Sanitize and clamp inputs
        categoria = str(categoria).strip()[:100] or "Sin categoría"
        descripcion = str(descripcion).strip()[:500] if descripcion else ""
        ingreso = max(0.0, float(ingreso)) if ingreso else 0.0
        gasto = max(0.0, float(gasto)) if gasto else 0.0

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO transactions (fecha, categoria, descripcion, ingreso, gasto, mes, anio) VALUES (?,?,?,?,?,?,?)",
            (str(fecha), categoria, descripcion, ingreso, gasto, mes, anio)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_transaction(self, tid, fecha, categoria, descripcion, ingreso, gasto):
        if isinstance(fecha, str):
            dt = datetime.strptime(str(fecha)[:10], "%Y-%m-%d").date()
        else:
            dt = fecha
        # Sanitize inputs
        categoria = str(categoria).strip()[:100] or "Sin categoría"
        descripcion = str(descripcion).strip()[:500] if descripcion else ""
        ingreso = max(0.0, float(ingreso)) if ingreso else 0.0
        gasto = max(0.0, float(gasto)) if gasto else 0.0
        tid = int(tid)

        self.conn.execute(
            "UPDATE transactions SET fecha=?, categoria=?, descripcion=?, ingreso=?, gasto=?, mes=?, anio=? WHERE id=?",
            (str(dt), categoria, descripcion, ingreso, gasto, dt.month, dt.year, tid)
        )
        self.conn.commit()

    def delete_transaction(self, tid):
        self.conn.execute("DELETE FROM transactions WHERE id=?", (int(tid),))
        self.conn.commit()

    def get_transactions(self, anio=None, mes=None, categoria=None, search=None, limit=500, offset=0, order_by="fecha", order_dir="DESC"):
        # Strict validation of order_by and order_dir against SQL Injection whitelist
        safe_order_col = self.VALID_ORDER_COLS.get(str(order_by).lower(), "fecha")
        safe_order_dir = "ASC" if str(order_dir).upper() == "ASC" else "DESC"

        query = "SELECT * FROM transactions WHERE 1=1"
        params = []
        if anio:
            query += " AND anio=?"
            params.append(int(anio))
        if mes:
            query += " AND mes=?"
            params.append(int(mes))
        if categoria:
            query += " AND categoria=?"
            params.append(str(categoria)[:100])
        if search:
            # Escape wildcard characters to prevent LIKE injection DOS
            clean_search = str(search)[:200].replace("%", "\\%").replace("_", "\\_")
            query += " AND (descripcion LIKE ? ESCAPE '\\' OR categoria LIKE ? ESCAPE '\\')"
            params.extend([f"%{clean_search}%", f"%{clean_search}%"])

        query += f" ORDER BY {safe_order_col} {safe_order_dir}, id DESC LIMIT ? OFFSET ?"
        params.extend([max(1, min(int(limit), 1000)), max(0, int(offset))])
        return self.conn.execute(query, params).fetchall()

    def get_transaction_count(self, anio=None, mes=None, categoria=None, search=None):
        query = "SELECT COUNT(*) FROM transactions WHERE 1=1"
        params = []
        if anio:
            query += " AND anio=?"
            params.append(anio)
        if mes:
            query += " AND mes=?"
            params.append(mes)
        if categoria:
            query += " AND categoria=?"
            params.append(categoria)
        if search:
            query += " AND (descripcion LIKE ? OR categoria LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        return self.conn.execute(query, params).fetchone()[0]

    def get_monthly_summary(self, anio, mes):
        row = self.conn.execute(
            "SELECT COALESCE(SUM(ingreso),0) as total_ingreso, COALESCE(SUM(gasto),0) as total_gasto FROM transactions WHERE anio=? AND mes=?",
            (anio, mes)
        ).fetchone()
        return {"ingreso": row[0], "gasto": row[1], "balance": row[0] - row[1]}

    def get_filtered_summary(self, anio=None, mes=None, categoria=None, search=None):
        query = "SELECT COALESCE(SUM(ingreso),0) as total_ingreso, COALESCE(SUM(gasto),0) as total_gasto FROM transactions WHERE 1=1"
        params = []
        if anio:
            query += " AND anio=?"
            params.append(anio)
        if mes:
            query += " AND mes=?"
            params.append(mes)
        if categoria:
            query += " AND categoria=?"
            params.append(categoria)
        if search:
            query += " AND (descripcion LIKE ? OR categoria LIKE ?)"
            params.extend([f"%{search}%", f"%{search}%"])
        row = self.conn.execute(query, params).fetchone()
        return {"ingreso": row[0], "gasto": row[1], "balance": row[0] - row[1]}

    def get_current_available_money(self):
        """Calculates current available money based on the most recent active month's ending balance + savings."""
        row = self.conn.execute("""
            SELECT anio, mes, COALESCE(SUM(ingreso),0) - COALESCE(SUM(gasto),0) as balance 
            FROM transactions 
            GROUP BY anio, mes 
            HAVING (SUM(ingreso) > 0 OR SUM(gasto) > 0)
            ORDER BY anio DESC, mes DESC LIMIT 1
        """).fetchone()
        if row:
            return {"anio": row[0], "mes": row[1], "saldo": row[2]}
        return {"anio": datetime.now().year, "mes": datetime.now().month, "saldo": 0.0}

    def get_yearly_summary(self, anio):
        rows = self.conn.execute(
            "SELECT mes, COALESCE(SUM(ingreso),0) as total_ingreso, COALESCE(SUM(gasto),0) as total_gasto FROM transactions WHERE anio=? GROUP BY mes ORDER BY mes",
            (anio,)
        ).fetchall()
        return [{"mes": r[0], "ingreso": r[1], "gasto": r[2], "balance": r[1] - r[2]} for r in rows]

    def get_category_summary(self, anio=None, mes=None):
        query = "SELECT categoria, COALESCE(SUM(ingreso),0) as total_ingreso, COALESCE(SUM(gasto),0) as total_gasto FROM transactions WHERE 1=1"
        params = []
        if anio:
            query += " AND anio=?"
            params.append(anio)
        if mes:
            query += " AND mes=?"
            params.append(mes)
        query += " GROUP BY categoria ORDER BY total_gasto DESC"
        rows = self.conn.execute(query, params).fetchall()
        return [{"categoria": r[0], "ingreso": r[1], "gasto": r[2]} for r in rows]

    def get_available_years(self):
        rows = self.conn.execute("SELECT DISTINCT anio FROM transactions ORDER BY anio").fetchall()
        return [r[0] for r in rows]

    def get_available_categories(self):
        rows = self.conn.execute("SELECT DISTINCT categoria FROM transactions ORDER BY categoria").fetchall()
        return [r[0] for r in rows]

    def get_balance_evolution(self, anio=None):
        query = "SELECT anio, mes, COALESCE(SUM(ingreso),0) as ing, COALESCE(SUM(gasto),0) as gas FROM transactions"
        params = []
        if anio:
            query += " WHERE anio=?"
            params.append(anio)
        query += " GROUP BY anio, mes ORDER BY anio, mes"
        rows = self.conn.execute(query, params).fetchall()
        return [{"anio": r[0], "mes": r[1], "ingreso": r[2], "gasto": r[3]} for r in rows]

    # === SERVICES ===
    def add_service(self, anio, mes, mes_num, personas=4, gas=0, gas_p=0, agua=0, agua_p=0, luz=0, luz_p=0, cable=0, cable_p=0, total_sin=0, total_con=0):
        personas = max(1, int(personas)) if personas else 4
        self.conn.execute(
            """INSERT OR REPLACE INTO services 
            (anio, mes, mes_num, personas, gas, gas_prorrateo, agua, agua_prorrateo, luz, luz_prorrateo, cable, cable_prorrateo, total_sin_luz, total_con_luz) 
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (anio, mes, mes_num, personas, gas, gas_p, agua, agua_p, luz, luz_p, cable, cable_p, total_sin, total_con)
        )
        self.conn.commit()

    def add_services_year(self, anio):
        """Initializes all 12 months for a given year if they don't already exist."""
        meses = [
            ("ENERO", 1), ("FEBRERO", 2), ("MARZO", 3), ("ABRIL", 4),
            ("MAYO", 5), ("JUNIO", 6), ("JULIO", 7), ("AGOSTO", 8),
            ("SEPTIEMBRE", 9), ("OCTUBRE", 10), ("NOVIEMBRE", 11), ("DICIEMBRE", 12)
        ]
        for nombre, num in meses:
            existing = self.conn.execute(
                "SELECT id FROM services WHERE anio=? AND mes_num=?", (anio, num)
            ).fetchone()
            if not existing:
                self.add_service(anio, nombre, num)
        return True

    def get_services(self, anio=None):
        if anio:
            return self.conn.execute("SELECT * FROM services WHERE anio=? ORDER BY mes_num", (anio,)).fetchall()
        return self.conn.execute("SELECT * FROM services ORDER BY anio, mes_num").fetchall()

    def get_services_years(self):
        rows = self.conn.execute("SELECT DISTINCT anio FROM services ORDER BY anio").fetchall()
        return [r[0] for r in rows]

    def update_service(self, sid, **kwargs):
        # Strict validation of service fields against whitelist
        valid_kwargs = {}
        for k, v in kwargs.items():
            if k in self.VALID_SERVICE_FIELDS:
                valid_kwargs[k] = int(v) if k == "personas" else float(v)
        if not valid_kwargs:
            return
        sets = ", ".join(f"{k}=?" for k in valid_kwargs)
        vals = list(valid_kwargs.values()) + [int(sid)]
        self.conn.execute(f"UPDATE services SET {sets} WHERE id=?", vals)
        self.conn.commit()

    # === BANK ACCOUNTS ===
    def add_bank_account(self, banco, alias="", motivo="", cvu_cbu=""):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO bank_accounts (banco, alias, motivo, cvu_cbu) VALUES (?,?,?,?)",
                        (banco, alias, motivo, cvu_cbu))
        self.conn.commit()
        return cursor.lastrowid

    def get_bank_accounts(self):
        return self.conn.execute("SELECT * FROM bank_accounts ORDER BY banco").fetchall()

    def update_bank_account(self, bid, banco, alias, motivo, cvu_cbu):
        self.conn.execute("UPDATE bank_accounts SET banco=?, alias=?, motivo=?, cvu_cbu=? WHERE id=?",
                          (banco, alias, motivo, cvu_cbu, bid))
        self.conn.commit()

    def delete_bank_account(self, bid):
        self.conn.execute("DELETE FROM bank_accounts WHERE id=?", (bid,))
        self.conn.commit()

    # === SAVINGS ===
    def add_saving(self, concepto, monto, moneda="ARS"):
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO savings (concepto, monto, moneda) VALUES (?,?,?)", (concepto, monto, moneda))
        self.conn.commit()
        return cursor.lastrowid

    def get_savings(self):
        return self.conn.execute("SELECT * FROM savings ORDER BY moneda, concepto").fetchall()

    def update_saving(self, sid, concepto, monto, moneda):
        self.conn.execute("UPDATE savings SET concepto=?, monto=?, moneda=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",
                          (concepto, monto, moneda, sid))
        self.conn.commit()

    def delete_saving(self, sid):
        self.conn.execute("DELETE FROM savings WHERE id=?", (sid,))
        self.conn.commit()

    # === BUDGET ===
    def set_budget_item(self, mes, anio, grupo, categoria, monto):
        self.conn.execute(
            "INSERT OR REPLACE INTO budget_items (mes, anio, categoria_grupo, categoria, monto) VALUES (?,?,?,?,?)",
            (mes, anio, grupo, categoria, monto)
        )
        self.conn.commit()

    def get_budget(self, mes, anio):
        return self.conn.execute(
            "SELECT * FROM budget_items WHERE mes=? AND anio=? ORDER BY categoria_grupo, categoria",
            (mes, anio)
        ).fetchall()

    def get_budget_vs_real(self, mes, anio):
        budget = self.get_budget(mes, anio)
        result = []
        for b in budget:
            real = self.conn.execute(
                "SELECT COALESCE(SUM(gasto),0) FROM transactions WHERE mes=? AND anio=? AND categoria LIKE ?",
                (mes, anio, f"%{b['categoria']}%")
            ).fetchone()[0]
            result.append({
                "grupo": b["categoria_grupo"],
                "categoria": b["categoria"],
                "presupuesto": b["monto"],
                "real": real,
                "diferencia": b["monto"] - real,
                "porcentaje": (real / b["monto"] * 100) if b["monto"] > 0 else 0
            })
        return result

    # === CATEGORIES ===
    def add_category(self, nombre, tipo="ambos", grupo="General", color="#3498db"):
        nombre = str(nombre).strip()[:100]
        if not nombre:
            raise ValueError("El nombre de la categoría no puede estar vacío.")
        grupo = str(grupo).strip()[:100] or "General"
        tipo = tipo if tipo in ("ingreso", "gasto", "ambos") else "ambos"
        color = str(color).strip()[:20] or "#3498db"

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO categories (nombre, tipo, grupo, color) VALUES (?,?,?,?)",
            (nombre, tipo, grupo, color)
        )
        self.conn.commit()
        return cursor.lastrowid

    def update_category(self, cid, nombre, tipo="ambos", grupo="General", color="#3498db", sync_transactions=True):
        nombre = str(nombre).strip()[:100]
        if not nombre:
            raise ValueError("El nombre de la categoría no puede estar vacío.")
        grupo = str(grupo).strip()[:100] or "General"
        tipo = tipo if tipo in ("ingreso", "gasto", "ambos") else "ambos"
        color = str(color).strip()[:20] or "#3498db"
        cid = int(cid)

        # Get old name to sync transactions if changed
        old_cat = self.conn.execute("SELECT nombre FROM categories WHERE id=?", (cid,)).fetchone()
        old_name = old_cat[0] if old_cat else None

        self.conn.execute(
            "UPDATE categories SET nombre=?, tipo=?, grupo=?, color=? WHERE id=?",
            (nombre, tipo, grupo, color, cid)
        )

        if sync_transactions and old_name and old_name != nombre:
            self.conn.execute(
                "UPDATE transactions SET categoria=? WHERE categoria=?",
                (nombre, old_name)
            )

        self.conn.commit()

    def delete_category(self, cid, reassign_to="Sin categoría"):
        cid = int(cid)
        cat = self.conn.execute("SELECT nombre FROM categories WHERE id=?", (cid,)).fetchone()
        if not cat:
            return 0
        name = cat[0]

        # Reassign associated transactions so they don't break
        if reassign_to:
            self.conn.execute("UPDATE transactions SET categoria=? WHERE categoria=?", (reassign_to, name))

        self.conn.execute("DELETE FROM categories WHERE id=?", (cid,))
        self.conn.commit()
        return True

    def get_categories(self):
        return self.conn.execute("SELECT * FROM categories ORDER BY grupo, nombre").fetchall()

    def get_category_by_id(self, cid):
        return self.conn.execute("SELECT * FROM categories WHERE id=?", (int(cid),)).fetchone()

    def get_category_groups(self):
        rows = self.conn.execute("SELECT DISTINCT grupo FROM categories WHERE grupo IS NOT NULL AND grupo != '' ORDER BY grupo").fetchall()
        groups = [r[0] for r in rows]
        for standard in ["General", "Ingresos", "Vivienda", "Alimentación", "Tarjetas", "Entretenimiento", "Salud", "Obligaciones", "Otros"]:
            if standard not in groups:
                groups.append(standard)
        return sorted(groups)

    def get_categories_with_stats(self, search=None, grupo=None):
        query = """
            SELECT c.id, c.nombre, c.tipo, c.grupo, c.color,
                   COUNT(t.id) as trans_count,
                   COALESCE(SUM(t.gasto), 0) as total_gasto,
                   COALESCE(SUM(t.ingreso), 0) as total_ingreso
            FROM categories c
            LEFT JOIN transactions t ON c.nombre = t.categoria
            WHERE 1=1
        """
        params = []
        if grupo and grupo != "Todos":
            query += " AND c.grupo = ?"
            params.append(grupo)
        if search:
            clean = str(search)[:100].replace("%", "\\%").replace("_", "\\_")
            query += " AND (c.nombre LIKE ? ESCAPE '\\' OR c.grupo LIKE ? ESCAPE '\\')"
            params.extend([f"%{clean}%", f"%{clean}%"])

        query += " GROUP BY c.id ORDER BY c.grupo, c.nombre"
        return self.conn.execute(query, params).fetchall()

    def normalize_categories(self):
        """Unifies synonyms and normalizes all categories and transactions."""
        from utils.category_normalizer import normalize_database_categories
        return normalize_database_categories(self)

    def merge_categories(self, target_category_name, source_categories):
        """Merges multiple categories into one target category and updates transactions."""
        target = str(target_category_name).strip()
        if not target or not source_categories:
            return 0
        cursor = self.conn.cursor()
        total_tx = 0
        for src in source_categories:
            if src != target:
                res = cursor.execute("UPDATE transactions SET categoria=? WHERE categoria=?", (target, src))
                total_tx += res.rowcount
                cursor.execute("DELETE FROM categories WHERE nombre=?", (src,))
        self.conn.commit()
        return total_tx

    # === STATS ===
    def get_top_gastos(self, anio=None, mes=None, limit=10):
        query = "SELECT categoria, SUM(gasto) as total FROM transactions WHERE gasto > 0"
        params = []
        if anio:
            query += " AND anio=?"
            params.append(anio)
        if mes:
            query += " AND mes=?"
            params.append(mes)
        query += " GROUP BY categoria ORDER BY total DESC LIMIT ?"
        params.append(limit)
        return self.conn.execute(query, params).fetchall()

    def get_gastos_repetitivos(self, anio=None, limit=10):
        query = """SELECT categoria, descripcion, COUNT(*) as veces, AVG(gasto) as promedio, SUM(gasto) as total 
                   FROM transactions WHERE gasto > 0"""
        params = []
        if anio:
            query += " AND anio=?"
            params.append(anio)
        query += " GROUP BY categoria, descripcion HAVING veces >= 3 ORDER BY total DESC LIMIT ?"
        params.append(limit)
        return self.conn.execute(query, params).fetchall()

    # === SETTINGS ===
    def get_setting(self, key, default=None):
        row = self.conn.execute("SELECT value FROM app_settings WHERE key=?", (str(key),)).fetchone()
        return row[0] if row else default

    def set_setting(self, key, value):
        self.conn.execute("INSERT OR REPLACE INTO app_settings (key, value) VALUES (?,?)", (str(key), str(value)))
        self.conn.commit()

    def clear_all_data(self):
        for table in ["transactions", "services", "bank_accounts", "savings", "budget_items", "categories"]:
            self.conn.execute(f"DELETE FROM {table}")
        self.conn.commit()
