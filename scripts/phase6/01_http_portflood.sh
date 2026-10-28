#!/usr/bin/env bash
set -euo pipefail

kubectl exec -n attacks netshoot -- sh -c '
for i in $(seq 1 25)
do
  nc -vz -w1 frontend.app.svc.cluster.local 80 >/dev/null 2>&1 || true
  nc -vz -w1 productcatalogservice.app.svc.cluster.local 3550 >/dev/null 2>&1 || true
  nc -vz -w1 cartservice.app.svc.cluster.local 7070 >/dev/null 2>&1 || true
  nc -vz -w1 checkoutservice.app.svc.cluster.local 5050 >/dev/null 2>&1 || true
done

for i in $(seq 1 200)
do
  curl -s -o /dev/null http://frontend.app.svc.cluster.local/ &
done
wait
'
