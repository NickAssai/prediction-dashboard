import requests
from typing import List, Dict, Optional

OPINION_BASE_URL = "https://openapi.opinion.trade/openapi"
PREDICT_BASE_URL = "https://api.predict.fun/v1"

def fetch_opinion_markets(api_key: str) -> List[Dict]:
    """Точная логика как в твоём скрипте — с пагинацией и обработкой структуры"""
    headers = {"apikey": api_key, "User-Agent": "Mozilla/5.0"}
    markets = []
    page = 1
    
    while True:
        try:
            resp = requests.get(
                f"{OPINION_BASE_URL}/market",
                headers=headers,
                params={"status": "activated", "marketType": 2, "limit": 20, "page": page},
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            
            if data.get("errno", 1) != 0:
                break
                
            page_markets = data.get("result", {}).get("list", [])
            if not page_markets:
                break
                
            markets.extend(page_markets)
            page += 1
            if page > 5:  # защита от бесконечного цикла
                break
                
        except Exception as e:
            print(f"Opinion API error on page {page}: {e}")
            break
    
    return markets

def fetch_predict_markets(api_key: str) -> List[Dict]:
    """Точная логика как в твоём скрипте — только открытые рынки"""
    headers = {"x-api-key": api_key, "accept": "application/json"}
    markets = []
    after = None
    
    for _ in range(3):  # максимум 3 страницы для демо
        try:
            params = {"status": "OPEN", "first": "50", "sort": "VOLUME_24H_DESC"}
            if after:
                params["after"] = after
                
            resp = requests.get(
                f"{PREDICT_BASE_URL}/markets",
                headers=headers,
                params=params,
                timeout=10
            )
            resp.raise_for_status()
            data = resp.json()
            
            if not data.get("success"):
                break
                
            page_markets = data.get("data", [])
            markets.extend(page_markets)
            
            after = data.get("cursor")
            if not after:
                break
                
        except Exception as e:
            print(f"Predict API error: {e}")
            break
    
    return markets[:50]  # ограничим 50 для скорости

def compute_complement(price: Optional[float], precision: int = 2) -> Optional[float]:
    if price is None:
        return None
    factor = 10 ** precision
    return (factor - round(price * factor)) / factor
