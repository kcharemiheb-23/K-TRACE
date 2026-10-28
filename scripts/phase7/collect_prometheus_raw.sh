#!/usr/bin/env bash
set -euo pipefail

RUN_ID="$1"
RAW_START="$2"
RAW_END="$3"

BASE="$HOME/iheb_workspace/cloud-native-ids-azure"
OUTDIR="$BASE/artifacts/phase7/raw/$RUN_ID/prometheus"
mkdir -p "$OUTDIR"

if ! pgrep -f "kubectl -n monitoring port-forward svc/prometheus-server 9090:80" >/dev/null 2>&1; then
  nohup kubectl -n monitoring port-forward svc/prometheus-server 9090:80 >/tmp/prometheus_pf.log 2>&1 &
  sleep 5
fi

PY="$BASE/scripts/phase7/query_prometheus_range.py"

START_EPOCH="$(date -u -d "$RAW_START - 30 seconds" +%s)"
END_EPOCH="$(date -u -d "$RAW_END + 30 seconds" +%s)"

python3 "$PY" \
  --query 'sum(rate(istio_requests_total{destination_service=~"frontend.*"}[30s]))' \
  --start "$START_EPOCH" \
  --end "$END_EPOCH" \
  --step 5s \
  --out "$OUTDIR/frontend_req_rate.json"

python3 "$PY" \
  --query 'sum(rate(istio_requests_total{response_code=~"4.."}[30s]))' \
  --start "$START_EPOCH" \
  --end "$END_EPOCH" \
  --step 5s \
  --out "$OUTDIR/resp_4xx_rate.json"

python3 "$PY" \
  --query 'sum(rate(istio_requests_total[30s]))' \
  --start "$START_EPOCH" \
  --end "$END_EPOCH" \
  --step 5s \
  --out "$OUTDIR/all_req_rate.json"
