import csv
import json
import subprocess
import statistics
import hashlib
from datetime import datetime, timezone

RPC = "https://mainnet-rpc.rayls.com"
COUNT = 600
BATCH = 50

def rpc(requests):
    payload = [
        {"jsonrpc": "2.0", "id": i,
         "method": method, "params": params}
        for i, (method, params) in enumerate(requests)
    ]
    result = subprocess.run(
        ["curl", "-sS", "--fail-with-body",
         "--max-time", "30",
         "-H", "Content-Type: application/json",
         "--data-binary", json.dumps(payload), RPC],
        capture_output=True, text=True, check=True
    )
    responses = json.loads(result.stdout)
    by_id = {r["id"]: r for r in responses}

    if len(by_id) != len(requests):
        raise RuntimeError("Incomplete RPC response")

    for r in by_id.values():
        if "error" in r:
            raise RuntimeError(str(r["error"]))

    return [by_id[i]["result"] for i in range(len(requests))]

chain, head = rpc([
    ("eth_chainId", []),
    ("eth_blockNumber", [])
])

assert int(chain, 16) == 72957
latest = 12000000
start = latest - COUNT + 1

blocks = []
for n in range(start, latest + 1, BATCH):
    end = min(n + BATCH - 1, latest)
    requested = list(range(n, end + 1))
    chunk = rpc([
        ("eth_getBlockByNumber", [hex(x), False])
        for x in requested
    ])
    for expected, block in zip(requested, chunk):
        if block is None or int(block["number"], 16) != expected:
            raise RuntimeError(f"Block mismatch: {expected}")
    blocks.extend(chunk)

rows = []
for block in blocks:
    rows.append({
        "block": int(block["number"], 16),
        "timestamp": int(block["timestamp"], 16),
        "transaction_count": len(block["transactions"]),
        "gas_used": int(block["gasUsed"], 16),
        "block_hash": block["hash"]
    })

with open("windows/block_12000000_blocks.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

with open("windows/block_12000000_raw.json", "w") as f:
    json.dump(blocks, f, indent=2)

timestamps = [r["timestamp"] for r in rows]
intervals = [
    timestamps[i] - timestamps[i-1]
    for i in range(1, len(rows))
]

duration = timestamps[-1] - timestamps[0]
total_tx = sum(r["transaction_count"] for r in rows)
active = sum(r["transaction_count"] > 0 for r in rows)

# Exclude the first block to align transactions
# with the 599 intervals in the denominator.
interval_tx = sum(r["transaction_count"] for r in rows[1:])
tps = interval_tx / duration if duration > 0 else None

metadata = {
    "chain_id": 72957,
    "rpc": RPC,
    "sample_method": "600 consecutive historical blocks at a fixed height",
    "start_block": start,
    "end_block": latest,
    "total_transactions": total_tx,
    "active_blocks": active,
    "elapsed_seconds": duration,
    "observed_tps": tps,
    "retrieved_at_utc": datetime.now(timezone.utc).isoformat()
}
with open("windows/block_12000000_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)

print("Chain ID: 72957")
print("Block range:", start, "-", latest)
print("Total blocks:", len(rows))
print("Active blocks:", active)
print("Empty blocks:", len(rows) - active)
print("Transactions:", total_tx)
print("Median block interval:", statistics.median(intervals), "seconds")
print("Observed TPS:", round(tps, 5) if tps is not None else "N/A")
print("Max transactions in one block:", max(r["transaction_count"] for r in rows))
print("CSV SHA256:", hashlib.sha256(open("windows/block_12000000_blocks.csv", "rb").read()).hexdigest())
print("Saved CSV, raw JSON, and metadata.")
