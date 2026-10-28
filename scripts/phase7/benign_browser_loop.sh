#!/usr/bin/env bash
set -euo pipefail

DURATION="$1"
RPS="$2"

INTERVAL=$(python3 - <<PY
rps = float("$RPS")
print(1.0 / rps)
PY
)

kubectl exec -n app benign-browser -- sh -c "
END=\$(( \$(date +%s) + $DURATION ))
while [ \"\$(date +%s)\" -lt \"\$END\" ]; do
  curl -s -o /dev/null http://frontend.app.svc.cluster.local/ || true
  sleep $INTERVAL
done
"
