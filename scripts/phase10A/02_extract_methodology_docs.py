#!/usr/bin/env python3
from pathlib import Path
import shutil

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
OUTDIR = ROOT / "artifacts" / "phase10A" / "corpus" / "methodology"
INDEX = ROOT / "artifacts" / "phase10A" / "reports" / "phase10A_methodology_index.md"

sources = [
    ROOT / "docs" / "phase-logs" / "phase9.md",
    ROOT / "docs" / "phase-logs" / "phase9_v2.md",
    ROOT / "artifacts" / "phase9_v2" / "reports" / "phase9_v2_summary.md",
    ROOT / "artifacts" / "phase9_v2" / "reports" / "phase9_supervisor_summary.md",
]

written = []

for src in sources:
    if not src.exists():
        continue
    dst = OUTDIR / src.name
    text = src.read_text()
    with open(dst, "w") as f:
        f.write(f"# Extracted Methodology Document\n\n")
        f.write(f"**Source path:** `{src}`\n\n")
        f.write("---\n\n")
        f.write(text)
    written.append(dst)

with open(INDEX, "w") as f:
    f.write("# Phase 10A Methodology Index\n\n")
    for p in written:
        f.write(f"- {p.name}\n")

print("WROTE:", len(written), "documents")
for p in written:
    print(p)
