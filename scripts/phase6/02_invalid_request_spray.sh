#!/usr/bin/env bash
set -euo pipefail

kubectl exec -n attacks netshoot -- sh -c '
for i in $(seq 1 60)
do
  curl -s -o /dev/null -X TRACE http://frontend.app.svc.cluster.local/invalid-$i || true
  curl -s -o /dev/null -X OPTIONS http://frontend.app.svc.cluster.local/notfound-$i || true
  curl -s -o /dev/null -I http://frontend.app.svc.cluster.local/missing-$i || true
done
'
