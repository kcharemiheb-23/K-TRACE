# Phase 4 - Online Boutique Deployment on Single-Node Azure K3s

## Goal
Deploy Google Online Boutique and validate frontend reachability, load generation, internal DNS, and service communication before telemetry.

## Scope
- cluster pre-flight
- create app namespace
- deploy Online Boutique
- wait for deployment availability
- validate frontend with local port-forward
- validate loadgenerator
- validate in-cluster DNS and pod-to-service communication
- capture proof

## Design adaptation
This is the single-node Azure adaptation of the older multi-node Phase 4.
Cross-node spread checks are replaced with single-node stability checks.

## Safety
No telemetry stack yet.
No attacks.
No public exposure beyond SSH.
