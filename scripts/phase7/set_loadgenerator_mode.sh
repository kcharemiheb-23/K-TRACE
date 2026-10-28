#!/usr/bin/env bash
set -euo pipefail

MODE="$1"

case "$MODE" in
  idle)
    kubectl scale deployment -n app loadgenerator --replicas=0
    kubectl wait --for=delete pod -l app=loadgenerator -n app --timeout=300s || true
    ;;
  normal|peak|continuous_normal|continuous_browse)
    kubectl scale deployment -n app loadgenerator --replicas=1
    kubectl rollout status deployment/loadgenerator -n app --timeout=300s
    ;;
  *)
    echo "Unknown load mode: $MODE" >&2
    exit 2
    ;;
esac

kubectl get deployment -n app loadgenerator
kubectl get pods -n app -l app=loadgenerator -o wide || true
