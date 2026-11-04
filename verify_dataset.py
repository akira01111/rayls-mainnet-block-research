import csv
import json
import hashlib
from pathlib import Path
from statistics import median

folder = Path(".")
blocks = json.loads((folder / "recent_600_raw.json").read_text())
with open("recent_600_blocks.csv", newline="") as f:
    rows = list(csv.DictReader(f))
metadata = json.loads(Path("recent_600_metadata.json").read_text())

assert len(blocks) == len(rows) == 600
assert metadata["chain_id"] == 72957

for i, (block, row) in enumerate(zip(blocks, rows)):
    n = int(block["number"], 16)
    assert n == int(row["block"])
    assert int(block["timestamp"], 16) == int(row["timestamp"])
    assert len(block["transactions"]) == int(row["transaction_count"])
    assert int(block["gasUsed"], 16) == int(row["gas_used"])
    assert block["hash"].lower() == row["block_hash"].lower()

    if i:
        prev = blocks[i - 1]
        assert n == int(prev["number"], 16) + 1
        assert block["parentHash"].lower() == prev["hash"].lower()

timestamps = [int(b["timestamp"], 16) for b in blocks]
counts = [len(b["transactions"]) for b in blocks]
intervals = [b - a for a, b in zip(timestamps, timestamps[1:])]

duration = timestamps[-1] - timestamps[0]
total_tx = sum(counts)
active = sum(c > 0 for c in counts)
tps = sum(counts[1:]) / duration if duration else None

assert total_tx == metadata["total_transactions"]
assert active == metadata["active_blocks"]
assert duration == metadata["elapsed_seconds"]

report = {
    "status": "PASS",
    "chain_id": 72957,
    "start_block": int(blocks[0]["number"], 16),
    "end_block": int(blocks[-1]["number"], 16),
    "sampled_blocks": len(blocks),
    "active_blocks": active,
    "empty_blocks": len(blocks) - active,
    "total_transactions": total_tx,
    "duration_seconds": duration,
    "median_interval_seconds": median(intervals),
    "observed_tps": tps,
    "csv_sha256": hashlib.sha256(
        Path("recent_600_blocks.csv").read_bytes()
    ).hexdigest()
}

Path("audit_report.json").write_text(
    json.dumps(report, indent=2) + "\n"
)

print(json.dumps(report, indent=2))
print("Saved: audit_report.json")
