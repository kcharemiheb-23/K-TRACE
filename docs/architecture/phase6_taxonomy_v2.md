# Phase 6 v2 Taxonomy for Azure Single-Node Rebuild

## Accepted attack classes
1. A1_HTTP_PORTFLOOD
2. A2_INVALID_REQUEST_SPRAY
3. A3_RUNTIME_RECON
4. A4_EXPLOIT_LIKE_PAYLOADS

## Superseded mapping
- old A1_PORT_SCAN + old A2_HTTP_FLOOD -> new A1_HTTP_PORTFLOOD
- old A3_INVALID_REQUEST_SPRAY -> new A2_INVALID_REQUEST_SPRAY
- old A4_RUNTIME_RECON -> new A3_RUNTIME_RECON
- old A6_EXPLOIT_LIKE_PAYLOADS -> new A4_EXPLOIT_LIKE_PAYLOADS
- old A5_LATERAL_MOVEMENT -> removed

## Rationale
The old confusion matrix showed the strongest overlap among old A1/A2/A5.
The new taxonomy narrows the class space and separates:
- traffic/probing behavior
- invalid request behavior
- runtime behavior
- exploit-like payload behavior

## Safety
All attacks stay internal to the cluster and target only in-cluster services or pods.
