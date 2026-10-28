# Phase 3 - Single-Node K3s Installation

## Goal
Install and validate a single-node K3s server on the Azure VM.

## Scope
- Record installation inputs
- Write K3s config
- Install K3s
- Validate node readiness
- Validate kube-system health
- Prepare kubeconfig for azureuser
- Capture proof

## Design
- Single Azure VM
- Single-node K3s
- Traefik disabled
- ServiceLB disabled
- Local SSH-based administration only

## Safety
No application deployment yet.
No telemetry stack yet.
No attack activity.
