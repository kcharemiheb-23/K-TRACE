#!/usr/bin/env python3
"""
Phase 10U Part C - Demo walkthrough.

For three representative queries (one A1, one A3, one BENIGN), run all four
retriever modes and write a markdown report that shows side-by-side rankings
in a single table. Used for the supervisor demo and the dashboard methodology
page.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

spec = importlib.util.spec_from_file_location(
    "upgraded_retriever",
    ROOT / "scripts" / "phase10U" / "06_upgraded_retriever.py",
)
upgraded = importlib.util.module_from_spec(spec)
spec.loader.exec_module(upgraded)

OUT = ROOT / "artifacts" / "phase10U" / "reports" / "demo_walkthrough.md"

DEMOS = [
    {
        "label": "A1 semantic family query",
        "query": ("Retrieve evidence for HTTP request flooding, elevated "
                  "frontend request volume, port probing behavior, high "
                  "request counts, and service traffic pressure in the "
                  "cloud-native IDS."),
        "expected_family": "A1",
    },
    {
        "label": "A3 case-id query (the hardest baseline case)",
        "query": ("Retrieve evidence explaining IDS case A3_LOW_002 and its "
                  "security-relevant telemetry behavior."),
        "expected_family": "A3",
    },
    {
        "label": "BENIGN semantic family query",
        "query": ("Retrieve evidence for benign cloud-native microservice "
                  "behavior, normal browsing, controlled idle windows, "
                  "normal load, expected service traffic, and non-attack "
                  "activity."),
        "expected_family": "BENIGN",
    },
]

MODES = ["dense_only", "bm25_only", "rrf", "rrf_plus_metadata_rerank"]


def main():
    lines = []
    lines.append("# Phase 10U Part C - Retriever Walkthrough")
    lines.append("")
    lines.append("This walkthrough runs three representative queries against "
                 "all four upgraded retrieval modes. Each row shows the top "
                 "five retrieved chunks for one mode, with the family flag "
                 "color: a star marks chunks of the expected family, a dash "
                 "marks all others.")
    lines.append("")

    for demo in DEMOS:
        lines.append(f"## {demo['label']}")
        lines.append("")
        lines.append(f"**Query:** {demo['query']}")
        lines.append(f"**Expected family:** `{demo['expected_family']}`")
        lines.append("")
        for mode in MODES:
            lines.append(f"### Mode: `{mode}`")
            lines.append("")
            lines.append("| rank | chunk_id | family | match | score |")
            lines.append("|---:|---|---|---|---:|")
            results = upgraded.retrieve(
                query_text=demo["query"],
                top_k=5,
                mode=mode,
                expected_family=(
                    demo["expected_family"]
                    if mode == "rrf_plus_metadata_rerank" else None
                ),
            )
            for r in results:
                marker = ("*" if r["retrieved_family"] == demo["expected_family"]
                          else "-")
                lines.append(f"| {r['rank']} | `{r['chunk_id']}` | "
                             f"{r['retrieved_family']} | {marker} | "
                             f"{r['similarity_score_readable']:.4f} |")
            lines.append("")
        lines.append("---")
        lines.append("")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"WROTE: {OUT}")


if __name__ == "__main__":
    main()
