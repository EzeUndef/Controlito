# 🏦 Controlito - Software Open Source de Control de Finanzas Personales

Controlito es una aplicación de escritorio moderna para Windows diseñada para llevar un control financiero exhaustivo, profesional y 100% privado (offline, sin telemetría y con base de datos SQLite propia).

---

## ⚡ Instalación Rápida para Usuarios (Windows)

No necesitas tener Python instalado. Puedes descargar e instalar Controlito como cualquier programa de Windows:

1. **Descarga el instalador**: `Controlito_Setup_v1.2.0.exe` (disponible en la carpeta `dist_installer/` o en [GitHub Releases](https://github.com/Controlito/Controlito/releases)).
2. **Ejecuta el Setup**: Sigue el asistente de instalación.
3. El instalador creará automáticamente los accesos directos en tu **Escritorio** y **Menú Inicio**, además de registrar el desinstalador limpio en el Panel de Control de Windows.

---

## ✨ Características Principales

### 1. 💬 Modo Simple (Asistente Inteligente) vs 📊 Modo Data
- **Modo Simple**: Conversa en lenguaje natural con tus finanzas sin necesidad de revisar tablas ni números (*"¿Cuánta plata tengo ahora?"*, *"¿Cuánto gasté este mes?"*, *"¿Por qué gasté más en TC que el mes pasado?"*, *"¿Qué día compré zapatillas?"*).
- **Modo Data**: Toda la potencia de dashboards, tablas avanzadas y métricas detalladas.

### 2. 🏷️ Categorías Atomizadas & Unificación de Sinónimos
- **Catálogo Canónico Estandarizado**: Organización limpia en rubros fundamentales (Alimentación, Tarjetas & Finanzas, Vivienda, Transporte, Ocio, Salud, etc.).
- **Unificador Inteligente de Sinónimos**: Herramienta de 1-clic que detecta y consolida automáticamente variantes dispersas (ej: *"TC"*, *"Tarjeta Visa"*, *"Tarjeta Master"* → **Tarjetas de Crédito**; *"Comida"*, *"Delivery"*, *"Super"* → **Supermercado & Alimentos**).
- **CRUD Completo**: Alta, baja, modificación y fusión de categorías con sincronización de movimientos históricos.

### 3. ⚡ Servicios del Hogar & División Adaptable por Mes
- Seguimiento de Luz, Gas, Agua e Internet/Cable.
- **División adaptable por mes**: Cada mes puede dividirse entre una cantidad distinta de personas (ej: Enero entre 4, Febrero entre 3), calculando al instante la cuota exacta por persona.
- Ajuste rápido express y cálculo de prorrateo.

### 4. 💵 Cotización del Dólar en Vivo (dolarapi.com)
- 6 cotizaciones en tiempo real: **Dólar Blue, MEP/Bolsa, Oficial BNA, Tarjeta, Cripto y CCL**.
- Selector de cotización preferida para convertir automáticamente tus ahorros USD a Pesos Argentinos (ARS).
- Soporte offline con valores en caché.

### 5. 🎨 8 Temas Visuales y Tablas Modernas
- Tipografía geométrica de alto rendimiento **Bahnschrift** y **Segoe UI**.
- 8 temas con personalidad propia: *💎 Next-Gen Obsidian, 🌌 Cyber Neon, 🌲 Nordic Pine, ☕ Espresso Gold, 🌊 Midnight Blue, 🌸 Dracula Velvet, 🍊 Sunset Crimson, ❄️ Arctic Frost*.
- Tablas con estilo dark moderno, zebra striping (filas alternadas) y formato visual destacado.

### 6. 🧠 Detective Financiero & Asesor
- Detección de gastos hormiga y proyección de ahorro anual.
- Estrategias de desendeudamiento (Bola de Nieve, Avalancha e Híbrido).
- Guías de presupuesto 50/30/20 y fondo de emergencia escalonado.

### 7. 📂 Importador Inteligente de Excel
- Carga de 1-clic de hojas de cálculo históricas preservando años, servicios, cuentas y ahorros.

---

## 🔒 Privacidad y Seguridad (Open Source)

> **Reglas fundamentales para usuarios y desarrolladores:**
> - Los datos se guardan en tu propia máquina en `C:\Users\<TuUsuario>\.controlito\controlito.db`.
> - **100% Offline**: Ningún dato financiero sale de tu computadora.
> - Consultas protegidas al 100% contra SQL Injection mediante parámetros seguros.
> - **Nunca subas tus archivos Excel personales ni tu base de datos a GitHub**. El archivo `.gitignore` ya viene configurado para proteger tus archivos privados.
> - Consulta [SECURITY.md](SECURITY.md) para más detalles.

---

## 🛠️ Desarrollo y Compilación

### Requisitos
- Python 3.10 o superior (probado en Python 3.15)
- Windows 10 / 11

### 1. Clonar el repositorio
```bash
git clone https://github.com/Controlito/Controlito.git
cd Controlito
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación
```bash
python main.py
```

### 4. Generar el Instalador de Windows (.exe)
```bash
# Compilar los binarios con PyInstaller
python -m PyInstaller --noconfirm --onedir --windowed --icon "assets/icon.ico" --add-data "assets;assets" --collect-all customtkinter --collect-all matplotlib --name "Controlito" main.py

# Generar el instalador Setup con Inno Setup
Compilar_Instalador.bat
```
El instalador generado se ubicará en `dist_installer/Controlito_Setup_v1.2.0.exe`.

---

## 📄 Licencia
Distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.
