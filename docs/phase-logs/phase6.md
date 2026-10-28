# Phase 6 - Attack Design and Dry-Run on Single-Node Azure K3s

## Goal
Rebuild the attack layer under the new Azure single-node conditions and supervisor feedback.

## Accepted taxonomy
- A1_HTTP_PORTFLOOD
- A2_INVALID_REQUEST_SPRAY
- A3_RUNTIME_RECON
- A4_EXPLOIT_LIKE_PAYLOADS

## Removed class
- A5_LATERAL_MOVEMENT

## Why this redesign
The old confusion structure showed overlap among the previous A1/A2/A5 family.
The taxonomy is narrowed to improve class separability.

## Safety
- Internal traffic only
- No public IP targets
- No attacks outside the VM / cluster
- Dry-run only in this phase
