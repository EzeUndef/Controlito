"""Update checker utility for Controlito using GitHub Releases API with Web Redirect Fallback."""
import json
import urllib.request
import urllib.error
import webbrowser

CURRENT_VERSION = "1.2.0"
GITHUB_REPO = "EzeUndef/Controlito"
RELEASES_API_URL = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
RELEASES_PAGE_URL = f"https://github.com/{GITHUB_REPO}/releases/latest"


def parse_version_tuple(version_str):
    """Parses a version string like 'v1.2.0' or '1.2' into a tuple of integers (1, 2, 0)."""
    clean = str(version_str).strip().lstrip("vV")
    parts = []
    for p in clean.split("."):
        try:
            parts.append(int(p))
        except ValueError:
            break
    while len(parts) < 3:
        parts.append(0)
    return tuple(parts[:3])


def is_newer_version(latest_str, current_str=CURRENT_VERSION):
    """Returns True if latest_str is strictly newer than current_str."""
    return parse_version_tuple(latest_str) > parse_version_tuple(current_str)


def check_for_updates(timeout=5):
    """
    Checks for updates on GitHub.
    1. Tries GitHub REST API for rich changelog notes and asset links.
    2. Falls back to web 302 redirect on rate-limit (403) or API blocks.
    3. Returns None only if completely offline.
    """
    # Attempt 1: GitHub REST API
    try:
        req = urllib.request.Request(
            RELEASES_API_URL,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Controlito-App"
            }
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                tag_name = data.get("tag_name", "").lstrip("vV")
                has_update = is_newer_version(tag_name, CURRENT_VERSION)

                download_url = data.get("html_url", RELEASES_PAGE_URL)
                assets = data.get("assets", [])
                for asset in assets:
                    name = asset.get("name", "").lower()
                    if name.endswith(".exe") and "setup" in name:
                        download_url = asset.get("browser_download_url", download_url)
                        break

                return {
                    "has_update": has_update,
                    "current_version": f"v{CURRENT_VERSION}",
                    "latest_version": f"v{tag_name}",
                    "release_name": data.get("name", f"Versión {tag_name}"),
                    "release_notes": data.get("body", ""),
                    "html_url": data.get("html_url", RELEASES_PAGE_URL),
                    "download_url": download_url
                }
    except Exception:
        # API failed (e.g. 403 Rate Limit Exceeded) - proceed to web fallback
        pass

    # Attempt 2: Web 302 Redirect (Immune to GitHub API rate limits)
    try:
        req = urllib.request.Request(
            RELEASES_PAGE_URL,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            final_url = resp.geturl()
            raw_tag = final_url.rstrip("/").split("/")[-1]
            tag_name = raw_tag.lstrip("vV")
            has_update = is_newer_version(tag_name, CURRENT_VERSION)

            download_url = f"https://github.com/{GITHUB_REPO}/releases/download/v{tag_name}/Controlito_Setup_v{tag_name}.exe"
            return {
                "has_update": has_update,
                "current_version": f"v{CURRENT_VERSION}",
                "latest_version": f"v{tag_name}",
                "release_name": f"Controlito v{tag_name}",
                "release_notes": "Visita el enlace para ver el registro completo de cambios de esta versión.",
                "html_url": final_url,
                "download_url": download_url
            }
    except Exception:
        pass

    return None


def open_download_page(url=None):
    """Opens browser directly to download URL or release page."""
    target = url or RELEASES_PAGE_URL
    webbrowser.open(target)
