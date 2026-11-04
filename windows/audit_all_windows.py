import csv
import json
import hashlib
from pathlib import Path
from datetime import datetime, timezone
from statistics import median

samples = [
    ("11M", "windows/block_11000000_"),
    ("12M", "windows/block_12000000_"),
    ("13M", "windows/block_13000000_"),
    ("Recent", "recent_600_"),
]

summary = []

for label, prefix in samples:
    blocks = json.loads(Path(prefix + "raw.json").read_text())
    metadata = json.loads(Path(prefix + "metadata.json").read_text())

    with open(prefix + "blocks.csv", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(blocks) == len(rows) == 600
    assert metadata["chain_id"] == 72957

    for i, (block, row) in enumerate(zip(blocks, rows)):
        number = int(block["number"], 16)
        timestamp = int(block["timestamp"], 16)

        assert number == int(row["block"])
        assert timestamp == int(row["timestamp"])
        assert len(block["transactions"]) == int(row["transaction_count"])
        assert int(block["gasUsed"], 16) == int(row["gas_used"])
        assert block["hash"].lower() == row["block_hash"].lower()

        if i:
            previous = blocks[i - 1]
            assert number == int(previous["number"], 16) + 1
            assert block["parentHash"].lower() == previous["hash"].lower()
            assert timestamp >= int(previous["timestamp"], 16)

    timestamps = [int(b["timestamp"], 16) for b in blocks]
    counts = [len(b["transactions"]) for b in blocks]
    duration = timestamps[-1] - timestamps[0]
    tx_count = sum(counts)
    active = sum(x > 0 for x in counts)
    observed_tps = sum(counts[1:]) / duration

    assert duration > 0
    assert tx_count == metadata["total_transactions"]
    assert active == metadata["active_blocks"]
    assert duration == metadata["elapsed_seconds"]
    assert abs(observed_tps - metadata["observed_tps"]) < 1e-12

    digest = hashlib.sha256(
        Path(prefix + "blocks.csv").read_bytes()
    ).hexdigest()

    utc = lambda t: datetime.fromtimestamp(
        t, timezone.utc
    ).strftime("%Y-%m-%d %H:%M:%S UTC")

    summary.append({
        "sample": label,
        "start_block": int(blocks[0]["number"], 16),
        "end_block": int(blocks[-1]["number"], 16),
        "start_utc": utc(timestamps[0]),
        "end_utc": utc(timestamps[-1]),
        "duration_seconds": duration,
        "total_transactions": tx_count,
        "active_blocks": active,
        "empty_blocks": 600 - active,
        "median_interval_seconds": median(
            b - a for a, b in zip(timestamps, timestamps[1:])
        ),
        "observed_tps": observed_tps,
        "csv_sha256": digest,
        "audit": "PASS"
    })

    print(f"\n{label}: AUDIT PASS")
    print("UTC:", utc(timestamps[0]), "to", utc(timestamps[-1]))
    print("Transactions:", tx_count)
    print("Empty blocks:", 600 - active)
    print("Duration:", duration, "seconds")
    print("Observed TPS:", round(observed_tps, 5))
    print("CSV SHA256:", digest)

output = Path("windows/comparison_summary.csv")
with output.open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=summary[0].keys())
    writer.writeheader()
    writer.writerows(summary)

print("\nALL FOUR WINDOWS: AUDIT PASS")
print("Total blocks:", 600 * len(summary))
print("Total transactions:", sum(s["total_transactions"] for s in summary))
print("Total empty blocks:", sum(s["empty_blocks"] for s in summary))
print("Saved:", output)
