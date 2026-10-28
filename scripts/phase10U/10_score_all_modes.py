#!/usr/bin/env python3
"""
Phase 10U Part D - Score baseline plus all four upgrade modes.

For each mode we run the existing Phase 10R scoring code unchanged. To do this
we temporarily place each mode's ranked-results CSV at the path the Phase 10R
script expects to read, then move the outputs to a per-mode folder.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
PHASE10R_RANKED_PATH = ROOT / "artifacts/phase10R/output/retrieval_ranked_results.csv"
PHASE10R_BACKUP = ROOT / "artifacts/phase10R/output/retrieval_ranked_results.BACKUP_for_phase10U.csv"
PHASE10R_OUT_QUERY = ROOT / "artifacts/phase10R/output/retrieval_metrics_by_query.csv"
PHASE10R_OUT_SUMMARY = ROOT / "artifacts/phase10R/output/retrieval_metrics_summary.csv"
PHASE10R_OUT_ERRORS = ROOT / "artifacts/phase10R/output/retrieval_error_analysis.csv"
SCORE_SCRIPT = ROOT / "scripts/phase10R/05_score_retriever_smart_metrics.py"

MODES = {
    "baseline": ROOT / "artifacts/phase10R/output/retrieval_ranked_results.csv",
    "dense_only": ROOT / "artifacts/phase10U/output/retrieval_ranked_results_v2_dense_only.csv",
    "bm25_only": ROOT / "artifacts/phase10U/output/retrieval_ranked_results_v2_bm25_only.csv",
    "rrf": ROOT / "artifacts/phase10U/output/retrieval_ranked_results_v2_rrf.csv",
    "rrf_plus_metadata_rerank": ROOT / "artifacts/phase10U/output/retrieval_ranked_results_v2_rrf_plus_metadata_rerank.csv",
}

OUT_BASE = ROOT / "artifacts/phase10U/output"


def main():
    # Always preserve the original baseline ranked results.
    if PHASE10R_RANKED_PATH.exists() and not PHASE10R_BACKUP.exists():
        shutil.copy2(PHASE10R_RANKED_PATH, PHASE10R_BACKUP)
        print(f"BACKED_UP_BASELINE_TO: {PHASE10R_BACKUP}")

    try:
        for mode, src in MODES.items():
            if not src.exists():
                print(f"SKIP {mode}: source missing at {src}")
                continue
            out_dir = OUT_BASE / f"scoring_{mode}"
            out_dir.mkdir(parents=True, exist_ok=True)

            # For non-baseline, point the Phase 10R script at our CSV.
            if mode != "baseline":
                shutil.copy2(src, PHASE10R_RANKED_PATH)
            else:
                # Restore the baseline file in case a previous run displaced it.
                if PHASE10R_BACKUP.exists():
                    shutil.copy2(PHASE10R_BACKUP, PHASE10R_RANKED_PATH)

            # Run the unchanged Phase 10R scoring script.
            res = subprocess.run(
                [sys.executable, str(SCORE_SCRIPT)],
                capture_output=True, text=True, check=False,
            )
            print(f"=== {mode} stdout ===\n{res.stdout}")
            if res.returncode != 0:
                print(f"=== {mode} stderr ===\n{res.stderr}", file=sys.stderr)
                raise SystemExit(f"scoring failed for {mode}")

            # Move outputs into the per-mode folder.
            for src_path in [PHASE10R_OUT_QUERY, PHASE10R_OUT_SUMMARY, PHASE10R_OUT_ERRORS]:
                if src_path.exists():
                    shutil.copy2(src_path, out_dir / src_path.name)

            print(f"WROTE: {out_dir}")
    finally:
        # Always restore the original baseline ranked-results file.
        if PHASE10R_BACKUP.exists():
            shutil.copy2(PHASE10R_BACKUP, PHASE10R_RANKED_PATH)
            print(f"RESTORED_BASELINE_AT: {PHASE10R_RANKED_PATH}")


if __name__ == "__main__":
    main()
