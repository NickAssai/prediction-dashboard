import requests

OPINION_BASE_URL = "https://openapi.opinion.trade/openapi"
PREDICT_BASE_URL = "https://api.predict.fun/v1"

def fetch_opinion_raw(api_key: str):
    headers = {"apikey": api_key, "User-Agent": "Mozilla/5.0"}
    resp = requests.get(
        f"{OPINION_BASE_URL}/market",
        headers=headers,
        params={"status": "activated", "marketType": 2, "limit": 20, "page": 1},
        timeout=10
    )
    return resp.json()  # ВОЗВРАЩАЕМ ВЕСЬ ОТВЕТ КАК ЕСТЬ

def fetch_predict_raw(api_key: str):
    headers = {"x-api-key": api_key, "accept": "application/json"}
    resp = requests.get(
        f"{PREDICT_BASE_URL}/markets",
        headers=headers,
        params={"status": "OPEN", "first": "50", "sort": "VOLUME_24H_DESC"},
        timeout=10
    )
    return resp.json()  # ВОЗВРАЩАЕМ ВЕСЬ ОТВЕТ КАК ЕСТЬ
