#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Installing Prometheus"
helm upgrade --install prometheus oci://ghcr.io/prometheus-community/charts/prometheus \
  -n monitoring \
  --create-namespace \
  --set alertmanager.enabled=false \
  --set prometheus-pushgateway.enabled=false

echo "[INFO] Waiting for Prometheus workloads"
for d in $(kubectl get deploy -n monitoring -o name); do
  kubectl rollout status -n monitoring "$d" --timeout=600s
done
for d in $(kubectl get ds -n monitoring -o name); do
  kubectl rollout status -n monitoring "$d" --timeout=600s
done

echo "[INFO] Installing Falco"
helm repo add falcosecurity https://falcosecurity.github.io/charts || true
helm repo update
helm upgrade --install falco falcosecurity/falco \
  -n falco \
  --create-namespace \
  --set tty=true \
  --set falcoctl.artifact.install.enabled=false \
  --set falcoctl.artifact.follow.enabled=false

kubectl wait pods --for=condition=Ready --all -n falco --timeout=600s
for d in $(kubectl get ds -n falco -o name); do
  kubectl rollout status -n falco "$d" --timeout=600s
done

echo "[INFO] Installing Istio"
cd "$HOME"
curl -L https://istio.io/downloadIstio | sh -
cd ~/istio-*
export PATH="$PWD/bin:$PATH"
istioctl install -y --set profile=default --set meshConfig.accessLogFile=/dev/stdout
kubectl wait --for=condition=Available deployment/istiod -n istio-system --timeout=600s

echo "[INFO] Enabling sidecar injection"
kubectl label namespace app istio-injection=enabled --overwrite
kubectl rollout restart deployment -n app
for d in $(kubectl get deploy -n app -o name); do
  kubectl rollout status -n app "$d" --timeout=600s
done

echo "[OK] Phase 5 telemetry stack installed"
