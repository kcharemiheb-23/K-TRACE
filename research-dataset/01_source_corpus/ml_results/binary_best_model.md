# Binary Best Model

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

## Test report

```text
task: binary
best_model: DecisionTree

              precision    recall  f1-score   support

      ATTACK       1.00      0.92      0.96        12
      BENIGN       0.92      1.00      0.96        12

    accuracy                           0.96        24
   macro avg       0.96      0.96      0.96        24
weighted avg       0.96      0.96      0.96        24

```
