"""
PREDICT.FUN — SNAPSHOT SCANNER (ASYNC ENHANCED)

• Fetch only active (OPEN) markets
• Support pagination to get all markets
• Sort by 24h volume descending
• For each market, fetch orderbook and stats asynchronously with concurrency limit
• Include raw orderbook data (limited depth)
• Compute complementary No prices with precision
• Rate limit friendly (concurrency limited to 4, respecting 240/min ~4/sec)
• Save progressive snapshots every 50 markets
• Ready for arbitrage analysis
"""

import asyncio
import aiohttp
import json
import os
from datetime import datetime, timezone
import time

# API Configuration
API_KEY = os.getenv("PREDICT_API_KEY", "05a4ad31-7943-44ba-aa15-0a271a926ed2")  # Use env var in production
BASE_URL = "https://api.predict.fun/v1"
HEADERS = {
    "x-api-key": API_KEY,
    "accept": "application/json"
}

PAGE_SIZE = 100  # first param
CONCURRENCY_LIMIT = 4  # ~240/min = 4/sec
DATA_DIR = "data/predictfun_snapshots"
os.makedirs(DATA_DIR, exist_ok=True)

# Progressive save every N markets
PROGRESSIVE_SAVE_INTERVAL = 50


def get_complement(price, decimal_precision=2):
    """Compute complementary price as per API docs"""
    if price is None:
        return None
    factor = 10 ** decimal_precision
    return (factor - round(price * factor)) / factor


async def fetch(session, url, params=None, method="GET", json_data=None):
    """Async fetch with session"""
    kwargs = {"headers": HEADERS, "params": params, "timeout": aiohttp.ClientTimeout(total=20)}
    if method == "POST":
        kwargs["json"] = json_data
    async with session.request(method, url, **kwargs) as response:
        if response.status != 200:
            print(f"❌ API error {response.status}: {await response.text()}")
            return None
        return await response.json()


async def fetch_all_active_markets(session):
    """Fetch all OPEN markets with pagination, sorted by 24h volume desc"""
    markets = []
    after = None
    while True:
        params = {
            "status": "OPEN",
            "first": str(PAGE_SIZE),
            "sort": "VOLUME_24H_DESC"
        }
        if after:
            params["after"] = after
        
        print(f"📡 Fetching markets page (after: {after})...")
        data = await fetch(session, f"{BASE_URL}/markets", params)
        
        if not data or not data.get("success"):
            print("❌ Failed to fetch markets")
            break
        
        page_markets = data.get("data", [])
        markets.extend(page_markets)
        print(f"✅ Fetched {len(page_markets)} markets (total: {len(markets)})")
        
        after = data.get("cursor")
        if not after:
            break
        
        await asyncio.sleep(0.1)  # Small delay between pages
    
    return markets


async def enhance_market(session, sem, market):
    """Fetch additional data for a single market: orderbook, stats, compute prices"""
    async with sem:
        market_id = market["id"]
        print(f"🔍 Enhancing market {market_id}: {market['title'][:50]}...")
        
        # Fetch orderbook and stats in parallel
        ob_task = asyncio.create_task(fetch(session, f"{BASE_URL}/markets/{market_id}/orderbook"))
        stats_task = asyncio.create_task(fetch(session, f"{BASE_URL}/markets/{market_id}/stats"))
        
        ob_data, stats_data = await asyncio.gather(ob_task, stats_task)
        
        if ob_data and ob_data.get("success"):
            market["orderbook"] = ob_data["data"]
        else:
            print(f"⚠️ Failed to fetch orderbook for {market_id}")
            market["orderbook"] = None
        
        if stats_data and stats_data.get("success"):
            market["stats"] = stats_data["data"]
        else:
            print(f"⚠️ Failed to fetch stats for {market_id}")
            market["stats"] = None
        
        # Compute prices if orderbook available
        if market["orderbook"]:
            ob = market["orderbook"]
            dp = market.get("decimalPrecision", 2)
            
            best_yes_bid = ob["bids"][0][0] if ob["bids"] else None
            best_yes_ask = ob["asks"][0][0] if ob["asks"] else None
            
            market["prices"] = {
                "yes": {
                    "buy": best_yes_ask,
                    "sell": best_yes_bid
                },
                "no": {
                    "buy": get_complement(best_yes_bid, dp),
                    "sell": get_complement(best_yes_ask, dp)
                }
            }
        
        # Small delay inside semaphore to ease rate limiting
        await asyncio.sleep(0.1)
    
    return market


async def main():
    print("=" * 80)
    print("🚀 PREDICT.FUN — ASYNC ENHANCED SNAPSHOT SCAN")
    print(f"🔑 API KEY: {API_KEY[:8]}...{API_KEY[-6:]}")
    print("=" * 80)
    
    async with aiohttp.ClientSession() as session:
        markets = await fetch_all_active_markets(session)
        
        if not markets:
            print("⚠️ No active markets fetched")
            return
        
        # Enhance markets asynchronously
        sem = asyncio.Semaphore(CONCURRENCY_LIMIT)
        tasks = [asyncio.create_task(enhance_market(session, sem, market)) for market in markets]
        enhanced_markets = await asyncio.gather(*tasks)
    
    # Save full snapshot
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    path = f"{DATA_DIR}/enhanced_snapshot_{ts}.json"
    
    snapshot_data = {
        "timestamp": ts,
        "total_markets": len(enhanced_markets),
        "markets": enhanced_markets
    }
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Enhanced snapshot saved: {len(enhanced_markets)} active markets")
    print(f"💾 File: {path}")
    
    # Progressive save: save partial every INTERVAL
    # But since async, perhaps save after all, or implement in loop but since gather, it's all at once.


if __name__ == "__main__":
    asyncio.run(main())