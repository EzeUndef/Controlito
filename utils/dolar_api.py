"""Integration with DolarApi for live Argentine exchange rates."""
import urllib.request
import json
import threading
from datetime import datetime

# Fallback cached rates if offline
DEFAULT_RATES = {
    "oficial": {"nombre": "Dólar Oficial (BNA)", "compra": 1540.0, "venta": 1590.0, "fecha": "Reciente"},
    "blue": {"nombre": "Dólar Blue", "compra": 1630.0, "venta": 1650.0, "fecha": "Reciente"},
    "bolsa": {"nombre": "Dólar MEP / Bolsa", "compra": 1653.0, "venta": 1655.0, "fecha": "Reciente"},
    "tarjeta": {"nombre": "Dólar Tarjeta", "compra": 2002.0, "venta": 2067.0, "fecha": "Reciente"},
    "cripto": {"nombre": "Dólar Cripto", "compra": 1747.0, "venta": 1750.0, "fecha": "Reciente"},
    "contadoconliqui": {"nombre": "Contado con Liqui (CCL)", "compra": 1752.0, "venta": 1754.0, "fecha": "Reciente"},
}

_cached_rates = DEFAULT_RATES.copy()
_last_fetch = None
_fetch_lock = threading.Lock()
_is_fetching = False


def fetch_dolar_rates():
    """Fetches live exchange rates from DolarApi synchronously with timeout and cache check."""
    global _cached_rates, _last_fetch, _is_fetching
    now = datetime.now()
    # If fetched successfully in last 2 minutes, return cached rates immediately
    if _last_fetch and (now - _last_fetch).total_seconds() < 120:
        return True, _cached_rates

    with _fetch_lock:
        # Re-check cache under lock
        if _last_fetch and (now - _last_fetch).total_seconds() < 120:
            return True, _cached_rates

        url = "https://dolarapi.com/v1/dolares"
        req = urllib.request.Request(url, headers={"User-Agent": "Controlito/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                for item in data:
                    casa = item.get("casa", "").lower()
                    if casa in _cached_rates:
                        _cached_rates[casa] = {
                            "nombre": item.get("nombre", _cached_rates[casa]["nombre"]),
                            "compra": float(item.get("compra", 0) or 0),
                            "venta": float(item.get("venta", 0) or 0),
                            "fecha": item.get("fechaActualizacion", datetime.now().strftime("%d/%m %H:%M"))
                        }
                _last_fetch = datetime.now()
                return True, _cached_rates
        except Exception:
            return False, _cached_rates


def fetch_dolar_rates_async(callback=None):
    """Fetches rates in a background thread and calls callback(success, rates).
    Prevents spawning multiple concurrent network requests."""
    global _is_fetching
    if _is_fetching:
        if callback:
            callback(True, _cached_rates)
        return

    def _worker():
        global _is_fetching
        _is_fetching = True
        try:
            success, rates = fetch_dolar_rates()
            if callback:
                callback(success, rates)
        finally:
            _is_fetching = False

    t = threading.Thread(target=_worker, daemon=True)
    t.start()


def get_current_rates():
    """Returns currently available or cached rates."""
    return _cached_rates
