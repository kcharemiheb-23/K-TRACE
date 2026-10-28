#!/usr/bin/env bash
set -euo pipefail

RUN_ID="$1"
RAW_START="$2"

BASE="$HOME/iheb_workspace/cloud-native-ids-azure"
OUTDIR="$BASE/artifacts/phase7/raw/$RUN_ID/envoy"
mkdir -p "$OUTDIR"

kubectl logs -n app deploy/frontend -c istio-proxy --since-time="$RAW_START" > "$OUTDIR/frontend.log" 2> "$OUTDIR/frontend.err" || true

kubectl logs -n app deploy/loadgenerator -c istio-proxy --since-time="$RAW_START" > "$OUTDIR/loadgenerator.log" 2> "$OUTDIR/loadgenerator.err" || true

PODS=$(kubectl get pods -n app -o jsonpath='{range .items[*]}{.metadata.name}{" "}{.spec.containers[*].name}{"\n"}{end}' | awk '/istio-proxy/ {print $1}')

for pod in $PODS; do
  kubectl logs -n app "$pod" -c istio-proxy --since-time="$RAW_START" > "$OUTDIR/${pod}.log" 2> "$OUTDIR/${pod}.err" || true
done

echo "[OK] envoy collection attempted for $RUN_ID into $OUTDIR"
ls -l "$OUTDIR" || true
