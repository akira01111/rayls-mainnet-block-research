import csv
import json
import subprocess
import statistics
from datetime import datetime, timezone

RPC = "https://mainnet-rpc.rayls.com"
WINDOWS = 8
BLOCKS_PER_WINDOW = 20
STRIDE = 6000

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
    if not isinstance(responses, list):
        raise RuntimeError("Unexpected batch response")

    by_id = {r["id"]: r for r in responses}

    if set(by_id) != set(range(len(requests))):
        raise RuntimeError("Incomplete batch response")

    for r in by_id.values():
        if "error" in r:
            raise RuntimeError(str(r["error"]))

    return [by_id[i]["result"] for i in range(len(requests))]

chain_hex, latest_hex = rpc([
    ("eth_chainId", []),
    ("eth_blockNumber", [])
])

chain_id = int(chain_hex, 16)
latest = int(latest_hex, 16)

if chain_id != 72957:
    raise RuntimeError(f"Unexpected chain ID: {chain_id}")

rows = []

print("Chain ID:", chain_id)
print("Latest block:", latest)
print()
print("Window | Blocks | Transactions | Median Interval | Observed TPS")

for w in range(WINDOWS):
    end = latest - (WINDOWS - 1 - w) * STRIDE
    start = end - BLOCKS_PER_WINDOW + 1

    numbers = list(range(start, end + 1))
    blocks = rpc([
        ("eth_getBlockByNumber", [hex(n), False])
        for n in numbers
    ])

    timestamps = []
    counts = []

    for n, block in zip(numbers, blocks):
        if block is None or int(block["number"], 16) != n:
            raise RuntimeError(f"Missing block {n}")

        timestamp = int(block["timestamp"], 16)
        count = len(block["transactions"])

        timestamps.append(timestamp)
        counts.append(count)

        rows.append({
            "window": w + 1,
            "block": n,
            "timestamp_utc": datetime.fromtimestamp(
                timestamp, timezone.utc
            ).isoformat(),
            "transactions": count,
            "gas_used": int(block["gasUsed"], 16),
            "block_hash": block["hash"]
        })

    intervals = [
        timestamps[i] - timestamps[i - 1]
        for i in range(1, len(timestamps))
    ]

    elapsed = timestamps[-1] - timestamps[0]
    tx = sum(counts[1:])
    tps = tx / elapsed if elapsed > 0 else None

    print(
        w + 1, "|", start, "-", end,
        "|", tx,
        "|", statistics.median(intervals), "s",
        "|", round(tps, 4) if tps is not None else "N/A"
    )

with open("rayls_blocks.csv", "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

with open("sample_metadata.json", "w") as f:
    json.dump({
        "chain_id": chain_id,
        "endpoint": RPC,
        "latest_block": latest,
        "windows": WINDOWS,
        "blocks_per_window": BLOCKS_PER_WINDOW,
        "stride": STRIDE,
        "sampled_blocks": len(rows),
        "method": "eight separated 20-block contiguous windows"
    }, f, indent=2)

print("\nSaved: rayls_blocks.csv")
print("Saved: sample_metadata.json")
print("Total sampled blocks:", len(rows))
