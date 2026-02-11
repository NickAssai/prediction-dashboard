import requests
from typing import List, Dict, Optional

OPINION_BASE_URL = "https://openapi.opinion.trade/openapi"
PREDICT_BASE_URL = "https://api.predict.fun/v1"

def fetch_opinion_markets(api_key: str) -> List[Dict]:
    headers = {"apikey": api_key, "User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(
            f"{OPINION_BASE_URL}/market",
            headers=headers,
            params={"status": "activated", "marketType": 2, "limit": 20, "page": 1},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("result", {}).get("list", []) if data.get("errno") == 0 else []
    except Exception as e:
        print(f"Opinion API error: {e}")
        return []

def fetch_predict_markets(api_key: str) -> List[Dict]:
    headers = {"x-api-key": api_key, "accept": "application/json"}
    try:
        resp = requests.get(
            f"{PREDICT_BASE_URL}/markets",
            headers=headers,
            params={"status": "OPEN", "first": "50", "sort": "VOLUME_24H_DESC"},
            timeout=10
        )
        resp.raise_for_status()
        data = resp.json()
        return data.get("data", []) if data.get("success") else []
    except Exception as e:
        print(f"Predict API error: {e}")
        return []

def compute_complement(price: Optional[float], precision: int = 2) -> Optional[float]:
    if price is None:
        return None
    factor = 10 ** precision
    return (factor - round(price * factor)) / factor
