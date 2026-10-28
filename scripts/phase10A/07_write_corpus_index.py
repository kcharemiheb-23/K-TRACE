#!/usr/bin/env python3
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
CORPUS = ROOT / "artifacts" / "phase10A" / "corpus"
OUT = ROOT / "artifacts" / "phase10A" / "reports" / "phase10A_corpus_index.md"

sections = ["methodology", "features", "ml_results", "cases", "glossary"]

with open(OUT, "w") as f:
    f.write("# Phase 10A Corpus Index\n\n")
    total = 0
    for section in sections:
        sec = CORPUS / section
        files = sorted([p.name for p in sec.glob("*.md")])
        total += len(files)
        f.write(f"## {section}\n")
        f.write(f"- count: {len(files)}\n")
        for name in files:
            f.write(f"- {name}\n")
        f.write("\n")
    f.write(f"## total_documents\n- {total}\n")

print("WROTE:", OUT)
