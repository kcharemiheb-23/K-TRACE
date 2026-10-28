# K-TRACE Retrieval Evaluation Results

## Evaluation scope

The Phase 10U retrieval comparison evaluates five configurations over 22 queries.
The headline comparison file reports bootstrap 95% confidence intervals based
on 1,000 resamples.

## Headline results

| Configuration | MRR | Precision@5 | Recall@5 | F1@5 | Cross-class contamination@5 |
|---|---:|---:|---:|---:|---:|
| Baseline | 0.7311 | 0.5182 | 0.1747 | 0.2466 | 0.4182 |
| Dense only | 0.6444 | 0.5455 | 0.1724 | 0.2455 | 0.2455 |
| BM25 only | 0.9545 | 0.6091 | 0.2076 | 0.2920 | 0.2000 |
| RRF | 0.8674 | 0.5909 | 0.1985 | 0.2799 | 0.1909 |
| RRF + metadata reranking | 1.0000 | 0.7091 | 0.2465 | 0.3457 | 0.1091 |

## Main observations

- RRF + metadata reranking has the highest reported MRR, Precision@5,
  Recall@5, and F1@5 among these configurations.
- Its reported cross-class contamination@5 is the lowest of the five.
- BM25 alone has higher MRR than RRF without metadata reranking.
- Relative to baseline, F1@5 increases from 0.2466 to 0.3457.
- Relative to baseline, cross-class contamination@5 decreases from 0.4182
  to 0.1091.

## Evidence files

- `artifacts/phase10U/output/comparison_headline.csv`
- `artifacts/phase10U/output/ablation_study.csv`
- `artifacts/phase10U/output/scoring_baseline/retrieval_metrics_summary.csv`
- `artifacts/phase10U/output/scoring_dense_only/retrieval_metrics_summary.csv`
- `artifacts/phase10U/output/scoring_bm25_only/retrieval_metrics_summary.csv`
- `artifacts/phase10U/output/scoring_rrf/retrieval_metrics_summary.csv`
- `artifacts/phase10U/output/scoring_rrf_plus_metadata_rerank/retrieval_metrics_summary.csv`
- `artifacts/phase10U/reports/phase10U_evaluation_report.md`

## Interpretation and limitations

These figures describe the evaluated 22-query benchmark. They do not alone
establish generalization to unseen queries or semantic entailment of generated
LLM explanations. Consult the evaluation report for confidence intervals,
methodology, grounding evaluation, and other limitations before citing results.

The reported figures should be rechecked against the underlying CSV files
before publication. This note is a navigation and summary document, not a
replacement for the source artifacts.
