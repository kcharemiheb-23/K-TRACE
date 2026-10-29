# Extracted Methodology Document

**Source path:** `./artifacts/phase9_v2/reports/phase9_v2_summary.md`

---

# Phase 9 v2 Summary

## Binary best model
- task: binary
- best_model: DecisionTree
- test_accuracy: 0.9583333333333334
- test_precision_macro: 0.9615384615384616
- test_recall_macro: 0.9583333333333331
- test_f1_macro: 0.9582608695652174
- test_precision_binary: 0.9230769230769232
- test_recall_binary: 1.0
- test_f1_binary: 0.96
- test_roc_auc: 0.9930555555555556
- test_pr_auc: 0.9871794871794872

## Multiclass best model
- task: multiclass
- best_model: RandomForest
- test_accuracy: 0.9583333333333334
- test_precision_macro: 0.95
- test_recall_macro: 0.9333333333333332
- test_f1_macro: 0.9314285714285716

## Robustness note
- binary: mean accuracy=0.9583, std accuracy=0.0000, mean f1_macro=0.9583
- multiclass: mean accuracy=0.9333, std accuracy=0.0228, mean f1_macro=0.9038

## Interpretation note
- Results are strong but still based on a small held-out test set.
- Binary and multiclass must be discussed separately.
- A3_RUNTIME_RECON should be discussed as the most difficult attack family if its per-class recall remains lower.
- Tree-based ensemble models should be presented as consistently strong, rather than overclaiming a single absolute winner.
