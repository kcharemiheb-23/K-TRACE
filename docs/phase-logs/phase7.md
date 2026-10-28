# Phase 7 - Enriched Controlled Collection v3 on Azure

## Goal
Build a large, balanced, contamination-aware raw telemetry corpus from the rebuilt Azure environment.

## Main corrections relative to older collection phases
- balanced attack vs benign run counts
- controlled + continuous benign traffic
- Python-based metadata-safe execution
- explicit raw and effective windows
- trim first 10s and last 10s by default
- pilot plots before full campaign
- cooldown gap between runs
- internal-only traffic

## Attack classes
- A1_HTTP_PORTFLOOD
- A2_INVALID_REQUEST_SPRAY
- A3_RUNTIME_RECON
- A4_EXPLOIT_LIKE_PAYLOADS

## Benign families
- BENIGN_CONTROLLED_IDLE
- BENIGN_CONTROLLED_NORMAL
- BENIGN_CONTROLLED_PEAK
- BENIGN_CONTINUOUS_NORMAL
- BENIGN_CONTINUOUS_BROWSE

## Safety
- no public targets
- no attacks outside the VM / cluster
- raw corpus only in this phase
