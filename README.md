# 🏦 Controlito - Software Open Source de Control de Finanzas Personales

[![GitHub Release](https://img.shields.io/github/v/release/EzeUndef/Controlito?color=2563eb&label=Descargar%20Instalador%20.exe)](https://github.com/EzeUndef/Controlito/releases/latest)
[![License: MIT](https://img.shields.io/badge/License-MIT-emerald.svg)](LICENSE)
[![Platform: Windows](https://img.shields.io/badge/Plataforma-Windows%2010%20%7C%2011-blue.svg)](https://github.com/EzeUndef/Controlito)
[![Privacy: 100% Local](https://img.shields.io/badge/Privacidad-100%25%20Local%20%7C%20Offline-success.svg)](SECURITY.md)

**Controlito** es una aplicación de escritorio corporativa para Windows diseñada para llevar un control financiero exhaustivo, profesional y 100% privado (offline, sin telemetría y con base de datos SQLite propia).

---

## ⚡ Descarga e Instalación para Usuarios (Windows)

No necesitas tener Python instalado ni saber de programación. Puedes descargar e instalar Controlito como cualquier programa estándar de Windows:

1. **Descarga el instalador oficial**:
   👉 Ve a **[GitHub Releases (Última Versión)](https://github.com/EzeUndef/Controlito/releases/latest)** y descarga el archivo `Controlito_Setup_v1.2.0.exe`.
2. **Ejecuta el Setup**: Haz doble clic en el instalador y sigue el asistente paso a paso.
3. El instalador creará automáticamente:
   - Acceso directo en tu **Escritorio**.
   - Acceso en el **Menú Inicio**.
   - Registro en el **Panel de Control de Windows** para una desinstalación 100% limpia cuando lo desees.

---

## ✨ Características Principales

### 1. ⚙️ Panel de Configuración y Preferencias Restaurado
- **Acceso directo desde el menú lateral**: Ahora `⚙️ Configuración` cuenta con una sección dedicada de fácil acceso.
- **Personalización de temas**: Cambia instantáneamente entre 8 paletas visuales corporativas.
- **Cotización preferida de divisas**: Selecciona con qué tipo de cambio calcular tus ahorros en USD.
- **Gestión integral de base de datos**: Importación de nuevos Excel, reinicio de bienvenida, unificación automática de categorías y acceso directo a la carpeta local de datos.

### 2. 🏛️ Estética y Tipografía Empresarial
- **Tipografía Corporativa**: Migración completa a `Segoe UI` y `Segoe UI Semibold` (estándar corporativo de Microsoft Fluent Design para Windows).
- **Temas Ejecutivos**:
  - `💼 Corporate Slate` (Tema empresarial predeterminado)
  - `🏛️ Executive Charcoal` (Estilo banca privada / Bloomberg)
  - `🌊 Midnight Navy` (Azul ejecutivo clásico)
  - `🌲 Nordic Enterprise` (Verde corporativo refinado)
  - `💎 Obsidian Tech` (Oscuro profundo tecnológico)
  - `☕ Warm Executive` (Tonos café bronce cálidos)
  - `❄️ Arctic Corporate` (Azul titanio ártico)
  - `🏢 Office Steel` (Gris acero ejecutivo)
- **Tablas Financieras Rediseñadas**: Encabezados claros, padding corporativo, zebra striping de alto contraste y selección con color de acento.

### 3. 💬 Modo Simple (Asistente Inteligente) vs 📊 Modo Data
- **Modo Simple**: Conversa en lenguaje natural con tus finanzas sin necesidad de revisar tablas (*"¿Cuánta plata tengo ahora?"*, *"¿Cuánto gasté este mes?"*, *"¿Por qué gasté más en TC que el mes pasado?"*, *"¿Qué día compré zapatillas?"*).
- **Modo Data**: Toda la potencia de dashboards, tablas avanzadas, filtros múltiples y métricas en tiempo real.

### 4. 🏷️ Categorías Atomizadas & Unificación de Sinónimos
- **Catálogo Canónico Estandarizado**: Organización limpia en rubros fundamentales (Alimentación, Tarjetas & Finanzas, Vivienda, Transporte, Ocio, Salud, etc.).
- **Unificador Inteligente de Sinónimos**: Herramienta de 1-clic que consolida automáticamente variantes dispersas (ej: *"TC"*, *"Tarjeta Visa"*, *"Tarjeta Master"* → **Tarjetas de Crédito**; *"Comida"*, *"Delivery"*, *"Super"* → **Supermercado & Alimentos**).
- **CRUD Completo**: Alta, baja, modificación y fusión de categorías con sincronización de movimientos históricos.

### 5. ⚡ Servicios del Hogar & División Adaptable por Mes
- Seguimiento de Luz, Gas, Agua e Internet/Cable.
- **División adaptable por mes**: Cada mes almacena y calcula su propia división de personas de manera independiente (ej: Enero entre 4, Febrero entre 3), calculando al instante la cuota exacta por persona.

### 6. 💵 Cotización del Dólar en Vivo (dolarapi.com)
- 6 cotizaciones en tiempo real: **Dólar Blue, MEP/Bolsa, Oficial BNA, Tarjeta, Cripto y CCL**.
- Selector de cotización preferida para convertir automáticamente tus ahorros USD a Pesos Argentinos (ARS).
- Soporte offline con valores en memoria caché.

### 7. 🧠 Detective Financiero & Asesor
- Detección de gastos hormiga y proyección de ahorro anual.
- Métodos de desendeudamiento (Bola de Nieve, Avalancha e Híbrido).
- Guías de presupuesto 50/30/20 y fondo de emergencia escalonado.

---

## 🔒 Privacidad y Seguridad (100% Local)

> - Todos tus registros financieros se almacenan localmente en tu equipo: `C:\Users\<TuUsuario>\.controlito\controlito.db`.
> - **Zero Cloud / Zero Telemetry**: Ningún dato de gastos, cuentas ni contraseñas sale jamás de tu máquina.
> - Consultas SQL parametrizadas para máxima protección.
> - El archivo `.gitignore` protege automáticamente bases de datos y archivos Excel personales. Consulta [SECURITY.md](SECURITY.md) para más detalles.

---

## 🛠️ Desarrollo, Compilación y Publicación de Releases

### Requisitos
- Python 3.10 o superior (probado en Python 3.15)
- Windows 10 / 11
- Inno Setup 6 (para generar el instalador `.exe`)

### 1. Clonar el repositorio
```bash
git clone https://github.com/EzeUndef/Controlito.git
cd Controlito
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Ejecutar en modo desarrollo
```bash
python main.py
```

### 4. Compilar los binarios y el instalador Setup (.exe)
```bash
# Paso 1: Generar carpeta ejecutable con PyInstaller
python -m PyInstaller --noconfirm --onedir --windowed --icon "assets/icon.ico" --add-data "assets;assets" --collect-all customtkinter --collect-all matplotlib --name "Controlito" main.py

# Paso 2: Crear el instalador .exe con Inno Setup
Compilar_Instalador.bat
```
El archivo resultante será `dist_installer\Controlito_Setup_v1.2.0.exe`.

### 5. Generar una Release en GitHub con el instalador adjunto
Para publicar una nueva versión en GitHub con el archivo instalador disponible para todo el mundo:
```powershell
# Usando GitHub CLI (gh):
gh release create v1.2.0 --title "Controlito v1.2.0 - Edición Empresarial" --notes "Lanzamiento oficial de Controlito v1.2.0 con instalador para Windows." dist_installer/Controlito_Setup_v1.2.0.exe
```

---

## 📄 Licencia
Distribuido bajo la Licencia MIT. Consulta el archivo `LICENSE` para más información.
