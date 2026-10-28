#!/usr/bin/env bash
set -euo pipefail

echo "[INFO] Creating app namespace"
kubectl create namespace app --dry-run=client -o yaml | kubectl apply -f -

echo "[INFO] Deploying Online Boutique"
kubectl apply -n app -f https://raw.githubusercontent.com/GoogleCloudPlatform/microservices-demo/main/release/kubernetes-manifests.yaml

echo "[INFO] Waiting for deployments"
kubectl wait --for=condition=Available --timeout=600s deployment --all -n app

echo "[INFO] Current deployments"
kubectl get deployments -n app

echo "[INFO] Current pods"
kubectl get pods -n app -o wide

echo "[INFO] Current services"
kubectl get svc -n app

echo "[OK] Online Boutique deployed"
