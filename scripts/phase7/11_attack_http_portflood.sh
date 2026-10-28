#!/usr/bin/env bash
set -euo pipefail

DURATION="$1"
INTENSITY="$2"

case "$INTENSITY" in
  low)    PORT_LOOPS=3; HTTP_BURST=8;  PAUSE=1 ;;
  medium) PORT_LOOPS=6; HTTP_BURST=15; PAUSE=1 ;;
  high)   PORT_LOOPS=10; HTTP_BURST=30; PAUSE=0 ;;
  *) echo "Unknown intensity"; exit 2 ;;
esac

kubectl exec -n attacks netshoot -- sh -c "
END=\$(( \$(date +%s) + $DURATION ))
while [ \"\$(date +%s)\" -lt \"\$END\" ]; do

  j=0
  while [ \"\$j\" -lt $PORT_LOOPS ]; do
    nc -vz -w1 frontend.app.svc.cluster.local 80 >/dev/null 2>&1 || true
    nc -vz -w1 productcatalogservice.app.svc.cluster.local 3550 >/dev/null 2>&1 || true
    j=\$((j+1))
  done

  k=0
  while [ \"\$k\" -lt $HTTP_BURST ]; do
    curl -s -o /dev/null http://frontend.app.svc.cluster.local/ &
    k=\$((k+1))
  done
  wait

  sleep $PAUSE
done
"
