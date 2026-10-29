# Multiclass Best Model

- task: multiclass
- best_model: RandomForest
- test_accuracy: 0.9583333333333334
- test_precision_macro: 0.95
- test_recall_macro: 0.9333333333333332
- test_f1_macro: 0.9314285714285716

## Test report

```text
task: multiclass
best_model: RandomForest

                          precision    recall  f1-score   support

       A1_HTTP_PORTFLOOD       0.75      1.00      0.86         3
A2_INVALID_REQUEST_SPRAY       1.00      1.00      1.00         3
        A3_RUNTIME_RECON       1.00      0.67      0.80         3
A4_EXPLOIT_LIKE_PAYLOADS       1.00      1.00      1.00         3
                  BENIGN       1.00      1.00      1.00        12

                accuracy                           0.96        24
               macro avg       0.95      0.93      0.93        24
            weighted avg       0.97      0.96      0.96        24

```
