##!/usr/bin/env python3
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
    print("tqdm не найден → простой текстовый прогресс")

API_KEY = os.getenv("OPINION_API_KEY", "2SYhVH3RBM9FIclodBONiE1qQySEQpZN")
BASE_URL = "https://openapi.opinion.trade/openapi"
HEADERS = {"apikey": API_KEY, "User-Agent": "Mozilla/5.0"}

# Оптимизированные для скорости параметры (15 req/s лимит API)
BATCH_SIZE         = 40          # больше батч → меньше overhead
REQ_DELAY          = 0.25        # минимальная пауза между батчами
CONCURRENCY_LIMIT  = 10          # ~10–12 req/s в пике → безопасно
RETRY_DELAY_BASE   = 1.0         # для 429 — экспоненциальная задержка
DATA_DIR           = "data/opinion_snapshots"
os.makedirs(DATA_DIR, exist_ok=True)


async def fetch(session, url, params=None, retries=3):
    for attempt in range(retries):
        try:
            async with session.get(url, headers=HEADERS, params=params, timeout=20) as resp:
                if resp.status == 429:
                    wait = RETRY_DELAY_BASE * (2 ** attempt)
                    print(f"429 Rate Limit → ждём {wait} сек")
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
                print(f"Ошибка запроса {url}: {e}")
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
                await asyncio.sleep(0.02)  # микрозадержка внутри батча
        tasks.append(task())
    await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    print("=" * 80)
    print("🚀 OPINION.TRADE — MAX SPEED MONITOR v3 (~45–75 сек)")
    print(f"🔑 API KEY: {API_KEY[:8]}...{API_KEY[-6:]}")
    print("=" * 80)

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
            print(f"✅ Page {page}: {len(page_markets)} markets (total: {len(markets)})")
            page += 1
            await asyncio.sleep(0.2)

        if not markets:
            print("⚠️ Нет рынков")
            return

        # 2. Токены
        tokens = []
        for m in markets:
            mtype = m.get("marketType")
            if mtype == 0:  # binary
                for ttype, tid in [("yes", m.get("yesTokenId")), ("no", m.get("noTokenId"))]:
                    if tid and tid != "0":
                        tokens.append((m, tid, ttype))
            elif mtype == 1:  # categorical
                for child in m.get("childMarkets", []):
                    tid = child.get("yesTokenId")
                    if tid and tid != "0":
                        tokens.append((child, tid, "yes"))

        print(f"🔍 Токенов для обработки: {len(tokens)}")

        # 3. Обработка батчами
        sem = asyncio.Semaphore(CONCURRENCY_LIMIT)

        if TQDM_AVAILABLE:
            pbar = tqdm(total=len(tokens), desc="Orderbooks", unit="token", ncols=100)
        else:
            print("Fetching orderbooks...")
            processed = 0

        for i in range(0, len(tokens), BATCH_SIZE):
            batch = tokens[i:i + BATCH_SIZE]
            await process_batch(session, sem, batch)

            if TQDM_AVAILABLE:
                pbar.update(len(batch))
            else:
                processed += len(batch)
                pct = (processed / len(tokens)) * 100
                bar = "█" * int(pct // 2) + "░" * (50 - int(pct // 2))
                print(f"  {processed:4d}/{len(tokens)}  {pct:5.1f}%  |{bar}|", end="\r", flush=True)

            await asyncio.sleep(REQ_DELAY)

        if TQDM_AVAILABLE:
            pbar.close()
        else:
            print("\nFetching завершено.")

    # Сохранение
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = f"{DATA_DIR}/snapshot_maxspeed_{ts}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "timestamp": ts,
            "markets_count": len(markets),
            "tokens_count": len(tokens),
            "markets": markets
        }, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Сохранено: {path}")
    print(f"   Рынков: {len(markets)} | Токенов: {len(tokens)}")


if __name__ == "__main__":
    asyncio.run(main())
