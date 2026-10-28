#!/usr/bin/env bash
set -euo pipefail

DURATION="$1"
INTENSITY="$2"

case "$INTENSITY" in
  low) SPRAY=3 ;;
  medium) SPRAY=6 ;;
  high) SPRAY=10 ;;
  *) echo "Unknown intensity"; exit 2 ;;
esac

kubectl exec -n attacks netshoot -- sh -c "
END=\$(( \$(date +%s) + $DURATION ))
while [ \"\$(date +%s)\" -lt \"\$END\" ]; do
  i=0
  while [ \"\$i\" -lt $SPRAY ]; do
    curl -s -o /dev/null -X TRACE http://frontend.app.svc.cluster.local/x || true
    curl -s -o /dev/null http://frontend.app.svc.cluster.local/404\$i || true
    i=\$((i+1))
  done
done
"
