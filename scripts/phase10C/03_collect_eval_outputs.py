#!/usr/bin/env python3
from pathlib import Path
import shutil

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

SRC = ROOT / "artifacts" / "phase10B" / "query_results"
DST = ROOT / "artifacts" / "phase10C" / "evaluation_results"

patterns = [
    "mistral_Q*.json",
    "phi3_mini_Q*.json",
]

copied = []

for pat in patterns:
    for p in SRC.glob(pat):
        shutil.copy2(p, DST / p.name)
        copied.append(p.name)

print("COPIED:", len(copied))
for name in sorted(copied):
    print(name)
