import requests


def execute_kegg_query(path: str) -> str:
    """Internal helper - executes the HTTP GET and returns raw text."""
    base = "https://rest.kegg.jp"
    url = f"{base}/{path.lstrip('/')}"
    r = requests.get(url, timeout=30.0)
    r.raise_for_status()
    return r.text
