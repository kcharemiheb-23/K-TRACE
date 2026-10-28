#!/usr/bin/env bash
set -euo pipefail

RUN_ID="$1"
RAW_START="$2"

BASE="$HOME/iheb_workspace/cloud-native-ids-azure"
OUTDIR="$BASE/artifacts/phase7/raw/$RUN_ID/falco"
mkdir -p "$OUTDIR"

for pod in $(kubectl get pods -n falco -o jsonpath='{range .items[*]}{.metadata.name}{"\n"}{end}')
do
  kubectl logs -n falco "$pod" --tail=500 > "$OUTDIR/${pod}.log" 2> "$OUTDIR/${pod}.err" || true
done

echo "[OK] falco collection attempted for $RUN_ID into $OUTDIR"
ls -l "$OUTDIR" || true
