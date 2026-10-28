# K-TRACE: Evidence-Grounded Intrusion Analysis and Controlled Response for Kubernetes Security

K-TRACE is a research prototype for evaluating evidence-grounded intrusion analysis and controlled response in cloud-native Kubernetes environments.

The framework combines run-level intrusion detection, evidence retrieval, LLM-assisted incident analysis, and deterministic response-policy selection. It is designed to separate generated explanations from remediation decisions.

## Research objectives

K-TRACE investigates four capabilities:

1. **Intrusion detection:** classify evaluated runs using telemetry-derived features.
2. **Evidence retrieval:** retrieve relevant incident evidence using lexical and dense retrieval methods.
3. **Grounded analysis:** evaluate whether generated incident explanations are supported by retrieved evidence.
4. **Controlled response:** apply deterministic policy logic and prepare Kubernetes remediation artifacts.

## Experimental environment and evaluation

The experiments use a controlled, single-node K3s environment with a cloud-native microservice application and security and observability components.

The retained evaluation materials cover:
- A 120-run dataset and associated detection experiments.
- Retrieval benchmark results.
- A 14-case grounding evaluation.
- An 11-run integrated response benchmark.

Consult the accompanying manuscript and the corresponding files under `artifacts/` for the precise protocols, metrics, and results.

### Important implementation detail

The Phase 9 v2 experiments evaluate classification models separately. In the supplied Phase 11 implementation, the intrusion gate consumes binary and multiclass predictions already recorded in enriched case files. The integrated workflow therefore does not, by itself, demonstrate fresh end-to-end inference from runtime telemetry.

The integrated response evaluation uses dry-run behavior. Generated remediation artifacts do not establish that changes were applied to a live cluster, that human approval is enforced, or that autonomous remediation is safe for production.

## Repository structure

| Path | Contents |
|---|---|
| `scripts/` | Experiment scripts and workflow entry points |
| `artifacts/` | Retained datasets, evaluation outputs, retrieval results, reports, and other experimental evidence |
| `docs/` | Phase documentation, research notes, and execution evidence |
| `manifests/` | Kubernetes configuration and deployment manifests |
| `README.md` | Project overview and release guidance |

Not every retained artifact is a raw dataset or a reusable model. Inspect the relevant phase documentation and manifests to understand the provenance and purpose of each file.

## Reproducibility

Reproducing an experiment requires more than running a script. The relevant inputs, dependencies, configuration, execution environment, and expected outputs must be identified together.

Before executing an experiment:

1. Read the documentation for the corresponding phase under `docs/` and inspect its scripts.
2. Identify the exact input data and configuration used by the reported result.
3. Review the required Python packages, external services, and infrastructure.
4. Inspect Kubernetes manifests and shell scripts before execution.
5. Record the command, environment, and outputs so the run can be independently checked.

**Release limitation:** the repository's dependency specification and cross-platform execution instructions must be verified before a complete clean-environment reproduction procedure can be claimed. Some scripts use environment-specific paths, and `scripts/phase11/demo_run.sh` is a Bash script intended for a compatible shell environment. Do not assume that it runs unchanged in Windows PowerShell.

The Phase 7 run manifest is located at `artifacts/phase7/output/dataset_run_manifest_clean.csv`. Other phases may use different inputs and execution procedures.

## Data and experimental evidence

The `artifacts/` directory contains retained experimental inputs and outputs, including run manifests, model-evaluation summaries, retrieval benchmarks, case files, and response reports.

For each result, consult its phase-specific documentation and associated scripts to determine:
- What data and labels were used.
- Which evaluation procedure and metrics were applied.
- Whether the result is a measured output, a diagnostic, or a derived report.
- Which limitations affect interpretation.

The repository's retained files should not be treated as proof that every experiment can be independently reproduced without additional environment setup or missing dependencies. Dataset provenance, reuse permissions, and any external data requirements must be documented explicitly in the release.

## Safety and intended use

This is a research prototype, not a production-ready security product.

- Run experiments only in infrastructure you own or are authorized to test.
- Inspect scripts and Kubernetes manifests before executing them.
- Begin with dry-run or non-destructive validation.
- Do not expose credentials, private keys, tokens, or sensitive infrastructure details.
- Do not enable live remediation in a production cluster based solely on these experiments.

## Limitations

The evaluation is conducted in a controlled environment. Results should not be interpreted as proof of production-scale generalization, fresh end-to-end inference in the integrated workflow, validated human-approval enforcement, or safe live-cluster remediation.

Retrieval and grounding results depend on their evaluated benchmarks and scoring procedures. Any metric reported in the manuscript should be traceable to its corresponding experimental output and protocol.

## Citation

If you use K-TRACE in research, cite the associated manuscript once its final bibliographic information is available.

A version-specific citation file and archived release identifier should be added before the public release. Do not cite an unregistered DOI or an unpublished version as though it were finalized.

## License and availability

The repository's reuse license must be selected after code ownership, third-party components, and dataset permissions have been checked. Until that review is complete, do not assume that public visibility grants permission to reuse every file.

The final publication release should identify the exact source-code version and provide the corresponding code-availability information requested by the journal.
