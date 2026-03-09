import argparse
import time
import requests
from datetime import datetime

APTOS_API = "https://api.testnet.aptoslabs.com/v1"


def get_transactions(address, limit=25):
    resp = requests.get(f"{APTOS_API}/accounts/{address}/transactions", params={"limit": limit})
    return resp.json() if resp.status_code == 200 else []


def filter_storage_events(txns):
    return [
        {"hash": t.get("hash"), "timestamp": t.get("timestamp"),
         "function": t.get("payload", {}).get("function", ""),
         "success": t.get("success")}
        for t in txns
        if "blob" in t.get("payload", {}).get("function", "").lower()
        or "shelby" in t.get("payload", {}).get("function", "").lower()
    ]


def watch(address, interval=30, max_iter=10):
    print(f"👁️  Watching {address[:16]}... for storage events")
    print(f"⏱️  Polling every {interval}s\n")
    seen = set()
    i = 0
    while max_iter == 0 or i < max_iter:
        for e in filter_storage_events(get_transactions(address)):
            if e["hash"] not in seen:
                seen.add(e["hash"])
                ts = datetime.fromtimestamp(int(e["timestamp"]) / 1e6)
                print(f"{'✅' if e['success'] else '❌'} [{ts.strftime('%H:%M:%S')}] {e['function']}")
                print(f"   tx: {e['hash'][:24]}...")
        i += 1
        if max_iter == 0 or i < max_iter:
            time.sleep(interval)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("address")
    p.add_argument("--interval", type=int, default=30)
    p.add_argument("--limit", type=int, default=10)
    args = p.parse_args()
    watch(args.address, args.interval, args.limit)
