# K-TRACE Experimental Results Index

This document maps the main experimental result groups to their retained
artifacts. File presence alone does not establish that a result is final,
reproducible, or suitable for publication.

## 1. Intrusion detection — Phase 9 v2

Location: `artifacts/phase9_v2/`

Inspect the model evaluation summaries, confusion matrices, feature-importance
outputs, and associated reports. Verify the selected models, metric definitions,
data splits, and reported values against the manuscript before citing results.

## 2. Retrieval evaluation — Phase 10R

Location: `artifacts/phase10R/`

Inspect retrieval metrics, ranked-result tables, retriever evaluation reports,
and scoring outputs. Confirm the benchmark configuration and identify which
retrieval result files are authoritative.

## 3. Updated retrieval and grounding — Phase 10U

Location: `artifacts/phase10U/`

Inspect the updated retrieval outputs, grounding-quality results, and
retrieval variants. Document the evaluated corpus, ranking method, scoring
procedure, and limitations before interpreting comparisons.

## 4. Methodology and experiment records

Locations include `artifacts/phase10A/` through `artifacts/phase10E/`,
as well as the relevant documentation under `docs/`.

Use these records to establish experiment inputs, processing steps, and the
relationship between scripts and retained outputs.

## 5. Integrated response evaluation

Inspect the Phase 11 scripts, reports, and proof files. Distinguish
precomputed-prediction orchestration and client-side dry-run validation from
fresh end-to-end inference or live Kubernetes remediation.

## 6. Publication verification checklist

- [ ] Match every reported metric to its source file.
- [ ] Identify one authoritative file for each published table or figure.
- [ ] Verify data splits and evaluation settings.
- [ ] Record dependencies and execution commands.
- [ ] Check for secrets and environment-specific infrastructure details.
- [ ] Document limitations and any results that cannot be independently reproduced.
- [ ] Confirm the manuscript and repository describe the same implementation.
