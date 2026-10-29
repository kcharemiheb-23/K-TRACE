# Extracted Methodology Document

**Source path:** `./docs/phase-logs/phase9_v2.md`

---

# Phase 9 v2 - Upgraded Traditional ML Validation

## Purpose
Upgrade the completed Phase 9 with stronger benchmarking, richer metrics, better plots, and a more supervisor-defensible reporting package.

## Why this upgrade is needed
- benchmark family too narrow
- current plots too limited
- current reporting too thin
- test-set size is small, so robustness and interpretation need strengthening

## Added in v2
- broader traditional ML benchmark set
- separate binary and multiclass comparison plots
- ROC and PR plots for binary
- per-class F1 plot for multiclass
- top feature importance and grouped source importance
- repeated-seed robustness check
- cleaner combined results and supervisor summary
