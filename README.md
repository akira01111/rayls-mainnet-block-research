# Rayls Mainnet Block Activity — Independent Verification

Independent, read-only analysis of Rayls Public Chain mainnet.

## Network
- Chain ID: 72957
- RPC: https://mainnet-rpc.rayls.com/
- Sample: Blocks 13816689 through 13817288
- Date: November 4, 2026

## Observations
- Blocks examined: 600
- Active blocks: 7
- Empty blocks: 593
- Transactions: 8
- Observation period: 805 seconds
- Median block interval: 1 second
- Observed throughput: approximately 0.00994 TPS

## Reproduce the Analysis

Verify the archived dataset:

    python3 verify_dataset.py

Fetch the same block range again:

    python3 reproduce_fixed_600.py

Compare both CSV files:

    sha256sum recent_600_blocks.csv reproduced_600_blocks.csv

Expected original CSV SHA256:

    e1032087049347fceb42b06566920a41b068a74bd47f99805b9f4fda47b7dd19

## Important Limitations

Observed throughput measures transaction activity within the sampled period.

It does not measure maximum network capacity.

Block timestamp intervals do not independently establish consensus finality.

This dataset represents one historical period, not all Rayls network activity.

All RPC requests are read-only. No wallet or transaction is required.
