# 🔒 Política de Seguridad y Buenas Prácticas - Controlito (Open Source)

Al ser una aplicación de gestión financiera personal destinada a ser publicada en GitHub como código abierto, **la privacidad y seguridad de los datos es la máxima prioridad**.

---

## 1. Reglas Críticas antes de hacer `git push`

> [!CAUTION]
> **NUNCA subas a GitHub:**
> 1. Tu archivo Excel personal (`.xlsx`, `.xls`) con tus movimientos reales.
> 2. Tu base de datos SQLite real (`controlito.db`).
> 3. Claves de acceso, PINs de cajero, claves PUK de celular o datos de tarjetas de crédito.
> 4. Tokens o variables de entorno en archivos de configuración.

### ¿Dónde guarda Controlito tus datos?
Controlito guarda la base de datos en la carpeta de usuario de tu sistema operativo:
- **Ruta segura**: `C:\Users\<TuUsuario>\.controlito\controlito.db`
- **Ventaja**: Al estar fuera del directorio del repositorio Git, **nunca se subirá por error a GitHub**.

---

## 2. Medidas de Protección y Seguridad Implementadas en el Código

### 🛡️ Prevención de Inyección SQL (SQL Injection)
1. **Consultas 100% Parametrizadas**:
   - Todas las consultas de lectura, inserción, actualización y borrado (`SELECT`, `INSERT`, `UPDATE`, `DELETE`) utilizan parámetros enlazados con placeholders `?`.
   - Nunca se concatena texto del usuario directamente en la sintaxis SQL.
2. **Listas Blancas (Whitelisting) para Ordenamiento y Campos Dinámicos**:
   - Los nombres de columnas permitidos para ordenar (`order_by`) están estrictamente restringidos al diccionario `VALID_ORDER_COLS` (`id`, `fecha`, `categoria`, `descripcion`, `ingreso`, `gasto`).
   - La dirección (`order_dir`) solo admite `ASC` o `DESC`.
   - La actualización de servicios valida los nombres de campo contra `VALID_SERVICE_FIELDS`.
3. **Escape de Comodines en Búsquedas (`LIKE`)**:
   - Los caracteres especiales `%` y `_` introducidos por el usuario son escapados formalmente mediante `ESCAPE '\'` para evitar ataques de DoS por consultas comodín desmedidas.

### 🧹 Sanitización y Validación de Entradas
1. **Truncamiento y Límite de Longitud**:
   - Descripciones limitadas a un máximo de 500 caracteres y categorías a 100 caracteres para evitar ataques de sobrecarga de memoria o payloads extensos.
2. **Tipado Estricto de Números y Fechas**:
   - Montos de ingreso y gasto son convertidos explícitamente a `float` con validación `try/except` y acotados a valores mayores o iguales a cero.
   - Las fechas se validan contra el estándar ISO `YYYY-MM-DD` mediante `datetime.strptime`.
   - Todos los identificadores (`id`) se fuerzan a tipo `int`.

### 🗄️ Blindaje de la Base de Datos SQLite (Database Hardening)
- `PRAGMA foreign_keys = ON;`: Garantiza integridad referencial.
- `PRAGMA journal_mode = WAL;`: Escritura atómica concurrente y resistencia contra corrupción ante cierres inesperados.
- `PRAGMA secure_delete = ON;`: Sobrescribe con ceros los sectores de registros eliminados, impidiendo la recuperación forense de movimientos eliminados desde los bloques no asignados del disco.

### 🌐 Almacenamiento 100% Local (Offline-First)
- Controlito no envía telemetría, no realiza llamadas de red ni expone puertos de red locales.
- La base de datos vive únicamente en la máquina del usuario (`~/.controlito/controlito.db`).

---

## 3. Lista de Verificación (Checklist) para Colaboradores

Antes de realizar un commit público:
- [ ] Ejecuta `git status` y revisa que ningún archivo `.xlsx` o `.db` personal esté en el stage.
- [ ] Si necesitas proveer datos de prueba para tests, usa datos ficticios ("Supermercado Ejemplo", "$100", "Usuario Demo").
- [ ] Verifica que el archivo `.env` o credenciales de servicios no existan en el repositorio.

---

## 4. Reporte de Vulnerabilidades
Si encuentras una falla de seguridad en el código de Controlito, por favor no abras un issue público con detalles explotables. Abre un reporte privado en GitHub Security Advisories.
