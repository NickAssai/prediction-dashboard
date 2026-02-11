#!/usr/bin/env python3
"""
OPINION.TRADE — OPTIMIZED MONITOR v3 (MAX SPEED ~45–75 сек)

• Увеличены батчи и параллелизм до предела безопасного лимита (15 req/s)
• CONCURRENCY_LIMIT=10 + BATCH_SIZE=40 + REQ_DELAY=0.25
• Прогресс через tqdm (или fallback print)
• Обработка ошибок, retries при 429
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timezone
import time

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

API_KEY = os.getenv("OPINION_API_KEY", "2SYhVH3RBM9FIclodBONiE1qQySEQpZN")
BASE_URL = "https://openapi.opinion.trade/openapi"
HEADERS = {"apikey": API_KEY, "User-Agent": "Mozilla/5.0"}

# Оптимизированные для скорости параметры (15 req/s лимит API)
BATCH_SIZE         = 40
REQ_DELAY          = 0.25
CONCURRENCY_LIMIT  = 10
RETRY_DELAY_BASE   = 1.0
DATA_DIR           = "data/opinion_snapshots"
os.makedirs(DATA_DIR, exist_ok=True)


async def fetch(session, url, params=None, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url, headers=HEADERS, params=params, timeout=20) as resp:
                if resp.status == 429:
                    wait = RETRY_DELAY_BASE * (2 ** attempt)
                    await asyncio.sleep(wait)
                    continue
                if resp.status != 200:
                    return None
                data = await resp.json()
                if data.get("errno", 1) != 0:
                    return None
                return data.get("result")
        except Exception as e:
            if attempt == retries - 1:
                pass
            await asyncio.sleep(0.5 * (attempt + 1))
    return None


async def fetch_orderbook(session, token_id):
    if not token_id or token_id == "0":
        return None
    return await fetch(session, f"{BASE_URL}/token/orderbook", {"token_id": token_id})


def compute_prices(orderbook):
    if not orderbook:
        return None
    bids = orderbook.get("bids", [])
    asks = orderbook.get("asks", [])
    best_bid = max((float(b["price"]) for b in bids), default=None) if bids else None
    best_ask = min((float(a["price"]) for a in asks), default=None) if asks else None
    return {"buy": best_ask, "sell": best_bid}


async def process_batch(session, sem, batch):
    tasks = []
    for obj, token_id, token_type in batch:
        async def task():
            async with sem:
                ob = await fetch_orderbook(session, token_id)
                prices = compute_prices(ob)
                prefix = f"{token_type}_"
                obj[prefix + "orderbook"] = ob
                obj[prefix + "prices"] = prices
                await asyncio.sleep(0.02)
        tasks.append(task())
    await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    async with aiohttp.ClientSession() as session:
        # 1. Рынки (пагинация)
        markets = []
        page = 1
        while True:
            params = {"status": "activated", "marketType": 2, "limit": 20, "page": page}
            data = await fetch(session, f"{BASE_URL}/market", params)
            if not data:
                break
            page_markets = data.get("list", [])
            if not page_markets:
                break
            markets.extend(page_markets)
            page += 1
            await asyncio.sleep(0.2)

        if not markets:
            return {"error": "No markets"}

        # 2. Токены
        tokens = []
        for m in markets:
            mtype = m.get("marketType")
            if mtype == 0:
                for ttype, tid in [("yes", m.get("yesTokenId")), ("no", m.get("noTokenId"))]:
                    if tid and tid != "0":
                        tokens.append((m, tid, ttype))
            elif mtype == 1:
                for child in m.get("childMarkets", []):
                    tid = child.get("yesTokenId")
                    if tid and tid != "0":
                        tokens.append((child, tid, "yes"))

        # 3. Обработка батчами
        sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
        for i in range(0, len(tokens), BATCH_SIZE):
            batch = tokens[i:i + BATCH_SIZE]
            await process_batch(session, sem, batch)
            await asyncio.sleep(REQ_DELAY)

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "markets_count": len(markets),
        "tokens_count": len(tokens),
        "markets": markets
    }


def run():
    """Запуск скрипта и возврат данных"""
    return asyncio.run(main())
    asyncio.run(main())

