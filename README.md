# Rayls Mainnet: Independent Block Activity Study

A reproducible, read-only study of transaction activity
and block intervals on Rayls Public Chain.

## Research question

How fast is Rayls Public Chain in observed activity,
and what can public onchain data actually prove?

## Network

- Chain ID: 72957
- RPC: https://mainnet-rpc.rayls.com/
- Observation dates: September 28 to November 4, 2026

## Verified results

| Window end | Blocks | Transactions | Empty blocks | Duration (s) | Observed TPS |
|---|---:|---:|---:|---:|---:|
| 11,000,000 | 600 | 19 | 593 | 414 | 0.04589 |
| 12,000,000 | 600 | 14 | 597 | 797 | 0.01757 |
| 13,000,000 | 600 | 6 | 597 | 809 | 0.00742 |
| 13,817,288 | 600 | 8 | 593 | 805 | 0.00994 |

Across four separate windows:
- 2,400 blocks examined
- 47 transactions recorded
- 2,380 blocks with zero transactions
- 99.17% of sampled blocks contained no transactions

These are disjoint historical samples, not continuous
monitoring or a statistically representative sample.

## Method

Each window consists of 600 consecutive EVM blocks
selected by a fixed ending block number.

Block data was retrieved using Ethereum JSON-RPC
eth_getBlockByNumber.

For each window, observed TPS is calculated as:

Transactions in blocks 2 through 600
divided by the timestamp difference between
the final and first sampled blocks.

This matches 599 measured timestamp intervals.

The scripts verify:
- Block-number continuity
- Parent-hash linkage
- CSV agreement with raw RPC responses
- Transaction counts and recorded timestamps
- Observed throughput calculations

## Reproduce

Verify the original sample:

    python3 verify_dataset.py

Verify all four samples:

    python3 windows/audit_all_windows.py

Re-fetch the original fixed block range:

    python3 reproduce_fixed_600.py

Re-fetch historical windows:

    python3 windows/fetch_11000000.py
    python3 windows/fetch_12000000.py
    python3 windows/fetch_13000000.py

The file windows/comparison_summary.csv contains
sample timestamps, measurements, and CSV SHA256 hashes.

## Interpretation and limitations

Observed throughput is not maximum network capacity.

A block with zero entries in its transaction array
does not imply consensus inactivity.

Block timestamp intervals are not direct measurements
of transaction finality.

These samples cannot establish network-wide usage trends,
peak TPS, validator performance, or consensus latency.

No transactions, wallet signatures, or private keys
were required.

## Official references

Rayls Public Chain:
https://docs.rayls.com/docs/a-warm-intro-do-rayls-public-chain

Axyl benchmarks:
https://docs.rayls.com/docs/axyl-performance-benchmarks

Axyl source:
https://github.com/raylsnetwork/axyl

## Axyl source snapshot

Reviewed source revision: `bb8ac6ddef4cf0b73aa109703a10c6be5d579a7f`

[Execution overview](https://github.com/raylsnetwork/axyl/blob/bb8ac6ddef4cf0b73aa109703a10c6be5d579a7f/doc/crates/execution/overview.md)

This identifies a public source-code revision; it does not prove which binary was deployed on mainnet.
