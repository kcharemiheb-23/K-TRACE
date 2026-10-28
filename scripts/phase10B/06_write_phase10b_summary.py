#!/usr/bin/env python3
from pathlib import Path
import json

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
QDIR = ROOT / "artifacts" / "phase10B" / "query_results"
OUT = ROOT / "artifacts" / "phase10B" / "reports" / "phase10B_summary.md"

files = sorted(QDIR.glob("*.json"))

with open(OUT, "w") as f:
    f.write("# Phase 10B Summary\n\n")
    f.write("## Goal\n")
    f.write("Build the first working RAG prototype over the validated Phase 10A corpus.\n\n")
    f.write("## Saved query artifacts\n")
    for p in files:
        f.write(f"- {p.name}\n")
    f.write("\n")

    for p in files:
        data = json.loads(p.read_text())
        f.write(f"## {p.name}\n")
        f.write(f"- question: {data.get('question')}\n")
        f.write(f"- model: {data.get('model', 'n/a')}\n")
        f.write(f"- top_k: {data.get('top_k', 'n/a')}\n")
        f.write("- sources:\n")
        for s in data.get("sources", []):
            f.write(f"  - {s['doc_name']} | {s['section']} | {s['chunk_id']}\n")
        f.write("\n")

print("WROTE:", OUT)
