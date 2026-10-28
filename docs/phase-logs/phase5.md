# Phase 5 - Telemetry Stack on Single-Node Azure K3s

## Goal
Install and validate Prometheus, Falco, and Istio/Envoy on the rebuilt single-node Azure K3s environment.

## Order
1. Prometheus
2. Falco
3. Istio

## Why this order
Prometheus first for low-risk metrics visibility.
Falco second for runtime telemetry.
Istio third because sidecar injection changes application pod shape.

## Safety
No attacks.
No dataset collection yet.
No public exposure beyond SSH.
