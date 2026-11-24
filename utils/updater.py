"""Update checker utility for Controlito using GitHub Releases API."""
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


def check_for_updates(timeout=4):
    """
    Queries GitHub Releases API.
    Returns a dict with update info if a newer version is found, or None if up to date or on network failure.
    Format of return dict:
    {
        "has_update": bool,
        "current_version": str,
        "latest_version": str,
        "release_name": str,
        "release_notes": str,
        "html_url": str,
        "download_url": str or None
    }
    """
    req = urllib.request.Request(
        RELEASES_API_URL,
        headers={
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "Controlito-App"
        }
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            if resp.status == 200:
                data = json.loads(resp.read().decode("utf-8"))
                tag_name = data.get("tag_name", "").lstrip("vV")
                has_update = is_newer_version(tag_name, CURRENT_VERSION)

                # Find direct installer .exe download URL if available in assets
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
        pass
    return None


def open_download_page(url=None):
    """Opens browser directly to download URL or release page."""
    target = url or RELEASES_PAGE_URL
    webbrowser.open(target)
