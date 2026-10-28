#!/usr/bin/env bash
set -euo pipefail

BASE="$HOME/cloud-native-ids-azure/scripts/phase6"
WRAP="$BASE/attack-window.sh"

bash "$WRAP" RUN_P6_A1_001 A1_HTTP_PORTFLOOD attacks netshoot internal_app_services script "$BASE/01_http_portflood.sh"
bash "$WRAP" RUN_P6_A2_001 A2_INVALID_REQUEST_SPRAY attacks netshoot frontend_http script "$BASE/02_invalid_request_spray.sh"
bash "$WRAP" RUN_P6_A3_001 A3_RUNTIME_RECON app falco-test in_container_runtime script "$BASE/03_runtime_recon.sh"
bash "$WRAP" RUN_P6_A4_001 A4_EXPLOIT_LIKE_PAYLOADS attacks netshoot frontend_http script "$BASE/04_exploit_like_payloads.sh"

echo "[OK] Phase 6 dry-runs completed"
