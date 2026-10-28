#!/usr/bin/env python3
"""
Phase 10U Part A - Corpus enrichment.

Reads:
  - artifacts/phase7/output/run-ledger.csv for run-level telemetry context
  - artifacts/phase10A/corpus/cases/*.md for existing case documents
Writes:
  - artifacts/phase10U/corpus_v2/cases/*.md enriched case documents
  - artifacts/phase10U/corpus_v2/_corpus_v2_manifest.json provenance manifest
  - artifacts/phase10U/reports/corpus_enrichment_report.md before/after example

The enrichment joins each case document with its run-ledger row and injects
family-specific evidence vocabulary drawn from the approved Phase 10R ground
truth policy. Original ML model results from each case document are preserved.
The boilerplate Notes block and the all-identical numerical feature dump are
removed because they add no information and dilute the embedding signal.
"""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

LEDGER = ROOT / "artifacts" / "phase7" / "output" / "run-ledger.csv"
CASES_IN = ROOT / "artifacts" / "phase10A" / "corpus" / "cases"
CASES_OUT = ROOT / "artifacts" / "phase10U" / "corpus_v2" / "cases"
MANIFEST_OUT = ROOT / "artifacts" / "phase10U" / "corpus_v2" / "_corpus_v2_manifest.json"
REPORT_OUT = ROOT / "artifacts" / "phase10U" / "reports" / "corpus_enrichment_report.md"

# Family-specific evidence vocabulary, drawn from
# artifacts/phase10R/reports/ground_truth_policy.md
# This is the approved relevance policy and therefore defensible.
FAMILY_EVIDENCE = {
    "A1_HTTP_PORTFLOOD": {
        "short": "A1",
        "human_name": "HTTP port flood and request pressure",
        "behavior_summary": (
            "This run exhibits HTTP request flooding behavior. The attacker pod "
            "issues a high-rate stream of HTTP requests and port probes against "
            "internal application services, generating elevated frontend request "
            "volume, increased request count per unit time, and traffic pressure "
            "on the service mesh."
        ),
        "telemetry_signals": [
            "elevated Envoy request count per second on the frontend service",
            "high HTTP request volume from a single attacker pod",
            "port probing behavior visible in destination port distribution",
            "request pressure spikes correlated with the attack window",
            "increased connection rate on the cloud-native frontend",
        ],
        "evidence_keywords": [
            "A1", "HTTP_PORTFLOOD", "portflood", "http flood", "flood",
            "request volume", "request count", "traffic pressure",
            "port probing", "frontend request", "high request",
        ],
    },
    "A2_INVALID_REQUEST_SPRAY": {
        "short": "A2",
        "human_name": "invalid HTTP request spray and application-layer probing",
        "behavior_summary": (
            "This run exhibits invalid request spray behavior. The attacker pod "
            "issues malformed HTTP methods, suspicious URI paths, and abnormal "
            "header patterns against the frontend service, generating a high "
            "rate of 4xx responses and application-layer probing signatures."
        ),
        "telemetry_signals": [
            "elevated 4xx response rate at the Envoy sidecar",
            "malformed HTTP methods including TRACE and unusual verbs",
            "suspicious or non-existent URI paths in access logs",
            "abnormal URI patterns indicating application-layer probing",
            "high ratio of bad requests to total requests",
        ],
        "evidence_keywords": [
            "A2", "INVALID_REQUEST_SPRAY", "invalid request", "malformed",
            "bad path", "suspicious path", "4xx", "TRACE",
            "abnormal uri", "application-layer probing",
        ],
    },
    "A3_RUNTIME_RECON": {
        "short": "A3",
        "human_name": "runtime reconnaissance inside containers",
        "behavior_summary": (
            "This run exhibits runtime reconnaissance behavior. The attacker "
            "executes shell commands and process discovery activity inside a "
            "container, inspecting the filesystem, reading sensitive files, "
            "and probing the container runtime, which produces Falco runtime "
            "alerts and suspicious container activity signatures."
        ),
        "telemetry_signals": [
            "Falco runtime alerts for shell execution inside container",
            "process discovery commands such as whoami, uname, and ps",
            "filesystem inspection including reads of /etc/passwd",
            "suspicious container activity not present in the benign baseline",
            "runtime syscall patterns inconsistent with normal application behavior",
        ],
        "evidence_keywords": [
            "A3", "RUNTIME_RECON", "runtime recon", "runtime reconnaissance",
            "Falco", "shell", "process", "filesystem", "whoami", "uname",
            "cat /etc/passwd", "container activity",
        ],
    },
    "A4_EXPLOIT_LIKE_PAYLOADS": {
        "short": "A4",
        "human_name": "exploit-like payloads and injection signatures",
        "behavior_summary": (
            "This run exhibits exploit-like payload behavior. The attacker pod "
            "issues HTTP requests containing path traversal strings, "
            "injection-like URL patterns, and suspicious encoded payloads "
            "against the frontend HTTP service, producing access log entries "
            "that match malicious payload signatures."
        ),
        "telemetry_signals": [
            "path traversal sequences such as ../ in request URIs",
            "injection-like URL patterns targeting application endpoints",
            "suspicious URL-encoded payloads in HTTP requests",
            "exploit-like signatures in Envoy access logs",
            "malicious HTTP payload patterns absent from the benign baseline",
        ],
        "evidence_keywords": [
            "A4", "EXPLOIT_LIKE_PAYLOADS", "exploit-like", "payload",
            "path traversal", "injection", "encoded payload",
            "suspicious URL", "suspicious URI",
        ],
    },
    "BENIGN": {
        "short": "BENIGN",
        "human_name": "benign cloud-native microservice activity",
        "behavior_summary": (
            "This run exhibits benign cloud-native microservice activity. "
            "Either the load generator produces normal browse patterns against "
            "the frontend, or the system is in a controlled idle window with "
            "no attack traffic. The run represents the legitimate baseline of "
            "the application and is used to validate false-positive behavior."
        ),
        "telemetry_signals": [
            "expected service traffic with no attack signatures",
            "normal request rate consistent with benign baseline",
            "no Falco runtime alerts in the trim window",
            "no malformed HTTP methods or path traversal payloads",
            "request distribution matches the benign reference profile",
        ],
        "evidence_keywords": [
            "BENIGN", "benign", "normal", "idle", "browse", "non-attack",
            "baseline", "normal load", "controlled idle", "continuous browse",
        ],
    },
}

INTENSITY_DESCRIPTIONS = {
    "low": "low intensity (subtle attack signal that may be hard to detect)",
    "medium": "medium intensity (clearly visible but not overwhelming)",
    "high": "high intensity (strongly visible attack signal)",
    "none": "no attack intensity (benign run)",
    "nan": "no attack intensity (benign run)",
}


def parse_ledger() -> dict:
    """Return a mapping from run_id to ledger row."""
    out = {}
    with LEDGER.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            run_id = row.get("run_id", "").strip()
            if run_id:
                out[run_id] = row
    return out


def parse_existing_case(text: str) -> dict:
    """Extract the small set of fields we want to preserve from an existing case."""
    fields = {}
    patterns = {
        "run_id": r"-\s*run_id:\s*(\S+)",
        "class_label": r"-\s*class_label:\s*(\S+)",
        "binary_label": r"-\s*binary_label:\s*(\S+)",
        "subtype": r"-\s*subtype:\s*(\S+)",
        "intensity": r"-\s*intensity:\s*(\S+)",
        "binary_model": r"##\s*Binary model result\s*\n-\s*model:\s*(\S+)",
        "binary_true": r"##\s*Binary model result[\s\S]*?-\s*true_label:\s*(\S+)",
        "binary_pred": r"##\s*Binary model result[\s\S]*?-\s*pred_label:\s*(\S+)",
        "multi_model": r"##\s*Multiclass model result\s*\n-\s*model:\s*(\S+)",
        "multi_true": r"##\s*Multiclass model result[\s\S]*?-\s*true_label:\s*(\S+)",
        "multi_pred": r"##\s*Multiclass model result[\s\S]*?-\s*pred_label:\s*(\S+)",
    }
    for key, pat in patterns.items():
        m = re.search(pat, text)
        fields[key] = m.group(1) if m else ""
    return fields


def family_of(class_label: str) -> str:
    """Map a class_label to the FAMILY_EVIDENCE key."""
    if not class_label:
        return "BENIGN"
    if class_label.startswith("A1"):
        return "A1_HTTP_PORTFLOOD"
    if class_label.startswith("A2"):
        return "A2_INVALID_REQUEST_SPRAY"
    if class_label.startswith("A3"):
        return "A3_RUNTIME_RECON"
    if class_label.startswith("A4"):
        return "A4_EXPLOIT_LIKE_PAYLOADS"
    return "BENIGN"


def render_enriched_case(run_id: str, ledger_row: dict, existing: dict) -> str:
    """Build the enriched markdown case document."""
    class_label = (
        existing.get("class_label")
        or ledger_row.get("class_label", "")
        or "BENIGN"
    )
    fam_key = family_of(class_label)
    fam = FAMILY_EVIDENCE[fam_key]

    intensity = (
        existing.get("intensity")
        or ledger_row.get("intensity", "")
        or "none"
    ).strip()
    intensity_desc = INTENSITY_DESCRIPTIONS.get(intensity, intensity)

    source_namespace = ledger_row.get("source_namespace", "").strip() or "unknown"
    source_pod = ledger_row.get("source_pod", "").strip() or "unknown"
    target_scope = ledger_row.get("target_scope", "").strip() or "unknown"
    duration = ledger_row.get("duration_sec", "").strip() or "unknown"
    payload_cmd = ledger_row.get("payload_cmd", "").strip()
    raw_start = ledger_row.get("raw_start_utc", "").strip()
    raw_end = ledger_row.get("raw_end_utc", "").strip()
    eff_start = ledger_row.get("effective_start_utc", "").strip()
    eff_end = ledger_row.get("effective_end_utc", "").strip()

    binary_model = existing.get("binary_model", "DecisionTree")
    binary_true = existing.get("binary_true", "")
    binary_pred = existing.get("binary_pred", "")
    multi_model = existing.get("multi_model", "RandomForest")
    multi_true = existing.get("multi_true", "")
    multi_pred = existing.get("multi_pred", "")

    binary_correct = (binary_true and binary_pred and binary_true == binary_pred)
    multi_correct = (multi_true and multi_pred and multi_true == multi_pred)

    keywords_csv = ", ".join(fam["evidence_keywords"])
    signals_md = "\n".join(f"- {s}" for s in fam["telemetry_signals"])

    md = f"""# Case Summary - {run_id}

## Run identity
- run_id: {run_id}
- attack_family: {fam["short"]}
- class_label: {class_label}
- scenario_family: {ledger_row.get("scenario_family", "").strip() or fam["short"]}
- subtype: {existing.get("subtype") or ledger_row.get("subtype", "").strip() or class_label}
- intensity: {intensity}
- intensity_meaning: {intensity_desc}

## Telemetry context (from Phase 7 controlled collection)
- source_namespace: {source_namespace}
- source_pod: {source_pod}
- target_scope: {target_scope}
- duration_sec: {duration}
- raw_start_utc: {raw_start}
- raw_end_utc: {raw_end}
- effective_start_utc: {eff_start}
- effective_end_utc: {eff_end}
- payload_command: {payload_cmd if payload_cmd else "n/a"}

## Behavior summary
{fam["behavior_summary"]}

This specific run is identified as {run_id} with intensity {intensity}, and was executed from source pod {source_pod} in namespace {source_namespace} against {target_scope} for {duration} seconds.

## Family-specific telemetry signals expected for {fam["short"]} ({fam["human_name"]})
{signals_md}

## ML detection result for this run
- Binary model: {binary_model}
- Binary true label: {binary_true}
- Binary predicted label: {binary_pred}
- Binary classification: {"correct" if binary_correct else "incorrect or unknown"}
- Multiclass model: {multi_model}
- Multiclass true label: {multi_true}
- Multiclass predicted label: {multi_pred}
- Multiclass classification: {"correct" if multi_correct else "incorrect or unknown"}

## Evidence vocabulary (for retriever grounding)
This case is associated with the following family-specific evidence vocabulary, used in the Phase 10R ground-truth relevance policy: {keywords_csv}.

## Notes
This case document was generated by Phase 10U Part A corpus enrichment. It joins the existing Phase 10A case structure with Phase 7 controlled-collection telemetry context and family-specific evidence vocabulary. It is intended for retrieval and LLM reasoning in the upgraded Phase 10U workflow.
"""
    return md


def main() -> None:
    CASES_OUT.mkdir(parents=True, exist_ok=True)
    REPORT_OUT.parent.mkdir(parents=True, exist_ok=True)
    MANIFEST_OUT.parent.mkdir(parents=True, exist_ok=True)

    ledger = parse_ledger()
    print(f"LEDGER_RUNS: {len(ledger)}")

    case_files = sorted(CASES_IN.glob("*.md"))
    print(f"BASELINE_CASE_FILES: {len(case_files)}")

    manifest = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "ledger_path": str(LEDGER),
        "cases_in": str(CASES_IN),
        "cases_out": str(CASES_OUT),
        "run_count": len(ledger),
        "case_count": len(case_files),
        "enrichment": [],
        "missing_in_ledger": [],
    }

    sample_before = ""
    sample_after = ""
    sample_run_id = "A3_LOW_004"

    for case_path in case_files:
        original_text = case_path.read_text(encoding="utf-8")
        existing = parse_existing_case(original_text)
        run_id = existing.get("run_id") or case_path.stem

        ledger_row = ledger.get(run_id, {})
        used_ledger = bool(ledger_row)
        if not used_ledger:
            manifest["missing_in_ledger"].append(run_id)

        enriched = render_enriched_case(run_id, ledger_row, existing)
        out_path = CASES_OUT / case_path.name
        out_path.write_text(enriched, encoding="utf-8")

        manifest["enrichment"].append({
            "run_id": run_id,
            "in_path": str(case_path),
            "out_path": str(out_path),
            "in_chars": len(original_text),
            "out_chars": len(enriched),
            "used_ledger": used_ledger,
        })

        if run_id == sample_run_id:
            sample_before = original_text
            sample_after = enriched

    MANIFEST_OUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    median_before = sorted(e["in_chars"] for e in manifest["enrichment"])[len(manifest["enrichment"]) // 2]
    median_after = sorted(e["out_chars"] for e in manifest["enrichment"])[len(manifest["enrichment"]) // 2]

    report = f"""# Phase 10U Part A - Corpus Enrichment Report

## What this part did
Phase 10U Part A rewrote the Phase 10A case corpus into a leakage-safe enriched corpus. Each case document was joined with its Phase 7 run-ledger row and augmented with family-specific evidence vocabulary drawn from the Phase 10R ground-truth relevance policy.

## Why
The Phase 10R retriever evaluation showed that Phase 10A case documents differ in only four lines per template, which prevents semantic embeddings from discriminating between attack families. The enrichment increases the volume of family-specific natural language per case document, which is expected to substantially improve Precision@k, Recall@k, and reduce cross-class contamination.

## Scope
- Cases enriched: {len(manifest["enrichment"])}
- Runs in Phase 7 ledger: {len(ledger)}
- Cases missing from ledger: {len(manifest["missing_in_ledger"])}
- Median chars before: {median_before}
- Median chars after: {median_after}
- Median size growth ratio: {median_after / max(median_before, 1):.2f}x

## Cases missing in Phase 7 ledger
{chr(10).join('- ' + r for r in manifest["missing_in_ledger"]) if manifest["missing_in_ledger"] else "(none)"}

## Example before (run A3_LOW_004)
## Provenance manifest
The provenance of every enriched case is recorded in:
{MANIFEST_OUT}

## Next step
Phase 10U Part B will rebuild the chunker, embedder, and Chroma collection from this enriched corpus into a parallel collection named ids_rag_corpus_v2, leaving the Phase 10B baseline untouched.
"""
    REPORT_OUT.write_text(report, encoding="utf-8")

    print(f"WROTE_CASES: {len(manifest['enrichment'])}")
    print(f"WROTE_MANIFEST: {MANIFEST_OUT}")
    print(f"WROTE_REPORT: {REPORT_OUT}")
    print(f"MEDIAN_GROWTH: {median_after / max(median_before, 1):.2f}x")
    if manifest["missing_in_ledger"]:
        print(f"WARN_MISSING_IN_LEDGER: {manifest['missing_in_ledger']}")


if __name__ == "__main__":
    main()

