"""Official GitHub Release publisher for Controlito."""
import os
import sys
import json
import subprocess
import urllib.request
import urllib.error


def get_github_token():
    # 1. Try env variable
    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if token:
        return token.strip()

    # 2. Try git credential fill
    try:
        proc = subprocess.run(
            ["git", "credential", "fill"],
            input="protocol=https\nhost=github.com\n",
            capture_output=True,
            text=True,
            check=True
        )
        for line in proc.stdout.splitlines():
            if line.startswith("password="):
                return line.split("=", 1)[1].strip()
    except Exception as e:
        print(f"Could not retrieve token from git credential: {e}")

    return None


def publish_release(tag="v1.2.0", title="Controlito v1.2.0 - Edición Empresarial", notes=None):
    token = get_github_token()
    if not token:
        print("ERROR: No se encontró token de GitHub. Asegúrate de tener credenciales configuradas en Git.")
        sys.exit(1)

    repo = "EzeUndef/Controlito"
    installer_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist_installer", "Controlito_Setup_v1.2.0.exe")
    if not os.path.isfile(installer_path):
        print(f"ERROR: No se encontró el instalador en {installer_path}")
        sys.exit(1)

    file_size_mb = os.path.getsize(installer_path) / (1024 * 1024)
    print(f"Instalador listo: Controlito_Setup_v1.2.0.exe ({file_size_mb:.2f} MB)")

    if not notes:
        notes = (
            "## 🏦 Controlito v1.2.0 — Edición Empresarial\n\n"
            "### 🚀 Novedades y Mejoras:\n"
            "- **Panel de Configuración Restaurado**: Nueva vista dedicada con selector de temas corporativos, cotización del dólar preferida, normalización de categorías y gestión de datos locales.\n"
            "- **Tipografía Empresarial**: Migración completa a **Segoe UI** y **Segoe UI Semibold** (Windows Fluent Enterprise Design).\n"
            "- **Temas Corporativos Ejecutivos**: `💼 Corporate Slate`, `🏛️ Executive Charcoal`, `🌊 Midnight Navy`, `🌲 Nordic Enterprise`, `💎 Obsidian Tech`, `☕ Warm Executive`, `❄️ Arctic Corporate`, `🏢 Office Steel`.\n"
            "- **Tablas Financieras Rediseñadas**: Encabezados claros, padding corporativo y formato de filas alternadas.\n"
            "- **División de Servicios Adaptable**: Cada mes calcula su cuota por persona de forma personalizada.\n"
            "- **100% Offline y Local**: Sin servidores externos ni telemetría.\n\n"
            "### 📥 Instalación:\n"
            "Descarga el archivo adjunto `Controlito_Setup_v1.2.0.exe` y ejecútalo para instalar en Windows 10/11."
        )

    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Controlito-Release-Agent"
    }

    # Step 1: Create or get release
    print(f"Creando o verificando release {tag} en {repo}...")
    release_url = f"https://api.github.com/repos/{repo}/releases"
    payload = {
        "tag_name": tag,
        "target_commitish": "main",
        "name": title,
        "body": notes,
        "draft": False,
        "prerelease": False
    }

    req = urllib.request.Request(
        release_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as resp:
            release_data = json.loads(resp.read().decode("utf-8"))
            print(f"Release creada exitosamente (ID: {release_data['id']})")
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8")
        if e.code == 422 or "already_exists" in err_body:
            print("La release ya existe, recuperando ID...")
            get_req = urllib.request.Request(f"https://api.github.com/repos/{repo}/releases/tags/{tag}", headers=headers)
            with urllib.request.urlopen(get_req) as resp:
                release_data = json.loads(resp.read().decode("utf-8"))
                print(f"Release encontrada (ID: {release_data['id']})")
        else:
            print(f"Error al crear release: {e.code} - {err_body}")
            sys.exit(1)

    release_id = release_data["id"]
    upload_url_template = release_data["upload_url"]
    upload_url = upload_url_template.split("{")[0] + "?name=Controlito_Setup_v1.2.0.exe"

    # Step 2: Check if asset already uploaded and delete if so
    if "assets" in release_data and release_data["assets"]:
        for asset in release_data["assets"]:
            if asset["name"] == "Controlito_Setup_v1.2.0.exe":
                print(f"Eliminando versión anterior del asset (ID: {asset['id']})...")
                del_req = urllib.request.Request(asset["url"], headers=headers, method="DELETE")
                urllib.request.urlopen(del_req)
                break

    # Step 3: Upload binary asset
    print(f"Subiendo instalador {os.path.basename(installer_path)} a GitHub Releases (esto puede tardar unos segundos)...")
    with open(installer_path, "rb") as f:
        file_bytes = f.read()

    upload_headers = {
        "Authorization": f"token {token}",
        "Content-Type": "application/octet-stream",
        "User-Agent": "Controlito-Release-Agent"
    }

    upload_req = urllib.request.Request(upload_url, data=file_bytes, headers=upload_headers)
    try:
        with urllib.request.urlopen(upload_req) as resp:
            asset_data = json.loads(resp.read().decode("utf-8"))
            print("\n" + "="*60)
            print(" ¡RELEASE PUBLICADA CON ÉXITO EN GITHUB!")
            print(f" URL de la Release: {release_data['html_url']}")
            print(f" Enlace directo de descarga:")
            print(f" {asset_data['browser_download_url']}")
            print("="*60 + "\n")
    except urllib.error.HTTPError as e:
        print(f"Error subiendo asset: {e.code} - {e.read().decode('utf-8')}")
        sys.exit(1)


if __name__ == "__main__":
    publish_release()
