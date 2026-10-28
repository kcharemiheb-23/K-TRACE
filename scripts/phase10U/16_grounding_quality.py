#!/usr/bin/env python3
"""
Phase 10U Part D - Grounding quality of LLM outputs.

For each Phase 10D LLM reasoning output, extract sentences that make factual
claims about telemetry, families, or behavior, then check what fraction of
those sentences contain at least one substantive token in common with the
top-5 retrieved chunks for that case (under both baseline and upgraded
retrieval).

Grounding rate is reported as the fraction of LLM claims with at least one
substantive overlap with the retrieved evidence. This is a deliberately
conservative proxy for grounding; it is not perfect, but it gives a
defensible numeric signal for the bridge between retrieval quality and LLM
reasoning quality.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
PHASE10D_RESULTS = ROOT / "artifacts/phase10D/results"
OUT = ROOT / "artifacts/phase10U/output/grounding_quality.csv"

spec = importlib.util.spec_from_file_location(
    "upgraded_retriever",
    ROOT / "scripts/phase10U/06_upgraded_retriever.py",
)
upgraded = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upgraded)

# A small stoplist so common words do not dominate the overlap score.
STOPWORDS = {
    "the", "a", "an", "and", "or", "but", "if", "then", "of", "to", "in",
    "on", "at", "for", "with", "by", "is", "are", "was", "were", "be",
    "been", "being", "this", "that", "these", "those", "it", "its", "as",
    "from", "into", "such", "which", "who", "whom", "whose", "what", "where",
    "when", "why", "how", "not", "no", "yes", "may", "can", "will", "would",
    "should", "could", "have", "has", "had", "do", "does", "did", "we", "i",
    "you", "they", "he", "she", "them", "us", "our", "your", "their",
}
TOKEN_RE = re.compile(r"[a-zA-Z0-9_]+")


def tokenize(text: str) -> set[str]:
    return {t.lower() for t in TOKEN_RE.findall(text or "") if t.lower() not in STOPWORDS and len(t) > 2}


def split_claims(text: str) -> list[str]:
    """Naive sentence splitter; good enough for grounding-style overlap."""
    sentences = re.split(r"(?<=[\.\!\?])\s+", (text or "").strip())
    return [s for s in sentences if len(s) > 30]


def grounding_for_case(run_id: str, llm_text: str, mode: str, top_k: int = 5,
                       expected_family: str | None = None) -> tuple[int, int]:
    """Return (claims_grounded, total_claims) for one case under one mode."""
    claims = split_claims(llm_text)
    if not claims:
        return 0, 0

    query = (
        f"Retrieve evidence explaining IDS case {run_id} and its "
        f"security-relevant telemetry behavior."
    )
    results = upgraded.retrieve(
        query_text=query, top_k=top_k, mode=mode,
        expected_family=expected_family,
    )
    chunk_tokens: set[str] = set()
    for r in results:
        chunk_tokens.update(tokenize(r.get("text_preview", "")))

    grounded = 0
    for c in claims:
        ctoks = tokenize(c)
        if not ctoks:
            continue
        if len(ctoks & chunk_tokens) >= 2:
            grounded += 1
    return grounded, len(claims)


def main():
    rows = []
    for jf in sorted(PHASE10D_RESULTS.glob("*.json")):
        try:
            data = json.loads(jf.read_text())
        except Exception as e:
            print(f"SKIP {jf.name}: {e}")
            continue
        run_id = data.get("run_id") or jf.stem
        # The 10D json schema stores the LLM text under various names; try several.
        llm_text = (
            data.get("llm_reasoning")
            or data.get("reasoning")
            or data.get("answer")
            or data.get("output")
            or json.dumps(data)
        )
        # Family from class_label if present.
        cls = (data.get("class_label") or "").upper()
        fam = next((f for f in ("A1", "A2", "A3", "A4") if cls.startswith(f)),
                   "BENIGN" if cls.startswith("BENIGN") else None)

        for mode in ("dense_only", "rrf_plus_metadata_rerank"):
            grounded, total = grounding_for_case(
                run_id, llm_text, mode,
                expected_family=(fam if mode == "rrf_plus_metadata_rerank" else None),
            )
            rate = (grounded / total) if total else 0.0
            rows.append({
                "run_id": run_id,
                "mode": mode,
                "claims_total": total,
                "claims_grounded": grounded,
                "grounding_rate": round(rate, 4),
            })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["run_id", "mode", "claims_total",
                                          "claims_grounded", "grounding_rate"])
        w.writeheader()
        w.writerows(rows)
    print(f"WROTE: {OUT}")

    # Per-mode summary
    by_mode = {}
    for r in rows:
        by_mode.setdefault(r["mode"], []).append(r["grounding_rate"])
    print("\nGrounding rate by mode (mean across cases):")
    for mode, rates in by_mode.items():
        mean = sum(rates) / len(rates) if rates else 0.0
        print(f"  {mode:<32} mean grounding rate = {mean:.3f}  (n={len(rates)})")


if __name__ == "__main__":
    main()
