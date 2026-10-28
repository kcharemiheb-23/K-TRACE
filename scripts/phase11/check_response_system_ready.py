#!/usr/bin/env python3
"""Phase 11 - Pre-flight check for the integrated response pipeline.

Verifies that every dependency the orchestrator needs is reachable.
Exits with code 0 if all checks pass, 1 otherwise.
"""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"

CHECKS = []

def check(name: str, ok: bool, detail: str = ""):
    CHECKS.append({"check": name, "ok": ok, "detail": detail})
    flag = "OK " if ok else "FAIL"
    print(f"[{flag}] {name}{(' - ' + detail) if detail else ''}")
    return ok

def main():
    ok_all = True

    # 1. Phase 10U retriever module loadable.
    retriever_path = ROOT / "scripts/phase10U/06_upgraded_retriever.py"
    ok = retriever_path.exists()
    ok_all &= check("phase10u_retriever_module_present", ok, str(retriever_path))

    if ok:
        try:
            spec = importlib.util.spec_from_file_location("upgraded_retriever", retriever_path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            ok = hasattr(mod, "retrieve")
            ok_all &= check("phase10u_retriever_has_retrieve_fn", ok)
        except Exception as e:
            ok_all &= check("phase10u_retriever_importable", False, str(e))

    # 2. Phase 10U corpus + index files.
    for label, p in [
        ("phase10u_chroma_dir",   ROOT / "artifacts/phase10U/vectorstore_v2"),
        ("phase10u_bm25_index",   ROOT / "artifacts/phase10U/bm25/bm25_index.pkl"),
        ("phase10u_chunk_records",ROOT / "artifacts/phase10U/chunks/chunk_records_v2.jsonl"),
        ("phase10u_corpus_cases", ROOT / "artifacts/phase10U/corpus_v2/cases"),
    ]:
        ok_all &= check(label, p.exists(), str(p))

    # 3. Phase 7 ledger.
    ledger = ROOT / "artifacts/phase7/output/run-ledger.csv"
    ok_all &= check("phase7_run_ledger_present", ledger.exists(), str(ledger))

    # 4. Phase 10D LLM result jsons (used as fallback for ML predictions).
    p10d = ROOT / "artifacts/phase10D/results"
    n = len(list(p10d.glob("*.json"))) if p10d.exists() else 0
    ok_all &= check("phase10d_results_dir", p10d.exists() and n > 0, f"{n} json files")

    # 5. Phase 10V benchmark CSV (provides the canonical run_id list).
    bench = ROOT / "artifacts/phase10V/benchmark/validation_benchmark.csv"
    ok_all &= check("phase10v_benchmark_csv", bench.exists(), str(bench))

    # 6. Phase 11 policy file.
    policy = ROOT / "scripts/phase11/policies/remediation_rules.yaml"
    ok = policy.exists()
    ok_all &= check("phase11_policy_present", ok, str(policy))
    if ok:
        try:
            import yaml
            data = yaml.safe_load(policy.read_text())
            ok = "rules" in data and "apply_guardrails" in data
            ok_all &= check("phase11_policy_parseable", ok)
        except Exception as e:
            ok_all &= check("phase11_policy_parseable", False, str(e))

    # 7. Manifest templates.
    for t in ["isolate_pod.yaml.j2", "rate_limit_or_deny.yaml.j2"]:
        p = ROOT / f"scripts/phase11/policies/manifest_templates/{t}"
        ok_all &= check(f"manifest_template_{t}", p.exists(), str(p))

    # 8. kubectl available.
    kctl = shutil.which("kubectl")
    ok_all &= check("kubectl_in_path", kctl is not None, kctl or "")

    if kctl:
        res = subprocess.run([kctl, "version", "--client", "--output=yaml"],
                             capture_output=True, text=True)
        ok_all &= check("kubectl_version_runs", res.returncode == 0)

    # 9. ollama available with mistral.
    oll = shutil.which("ollama")
    ok_all &= check("ollama_in_path", oll is not None, oll or "")
    if oll:
        res = subprocess.run([oll, "list"], capture_output=True, text=True)
        has_mistral = "mistral" in (res.stdout or "")
        ok_all &= check("ollama_has_mistral", has_mistral)

    # 10. Phase 11 output directories.
    for d in ["incidents", "reports", "actions", "logs", "summary"]:
        p = ROOT / f"artifacts/phase11/{d}"
        ok_all &= check(f"phase11_dir_{d}", p.exists() and p.is_dir(), str(p))

    print("")
    print(f"TOTAL_CHECKS: {len(CHECKS)}")
    print(f"PASSED: {sum(1 for c in CHECKS if c['ok'])}")
    print(f"FAILED: {sum(1 for c in CHECKS if not c['ok'])}")
    sys.exit(0 if ok_all else 1)

if __name__ == "__main__":
    main()
