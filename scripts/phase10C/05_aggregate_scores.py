#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

SRC = ROOT / "artifacts" / "phase10C" / "scoring" / "llm_scoring_sheet.csv"
OUTCSV = ROOT / "artifacts" / "phase10C" / "output" / "llm_score_aggregation.csv"
OUTMD = ROOT / "artifacts" / "phase10C" / "reports" / "phase10C_score_summary.md"

df = pd.read_csv(SRC)

score_cols = [
    "correctness_0_2",
    "grounding_0_2",
    "consistency_0_2",
    "no_hallucination_0_2",
    "analyst_usefulness_0_2",
]

for c in score_cols:
    df[c] = pd.to_numeric(df[c], errors="coerce")

agg = df.groupby("model")[score_cols].mean().reset_index()
agg["overall_mean"] = agg[score_cols].mean(axis=1)
agg = agg.sort_values("overall_mean", ascending=False)

agg.to_csv(OUTCSV, index=False)

with open(OUTMD, "w") as f:
    f.write("# Phase 10C Score Summary\n\n")
    f.write("## Mean scores by model\n\n")
    f.write("```text\n")
    f.write(agg.to_string(index=False))
    f.write("\n```\n")

print("WROTE:", OUTCSV)
print("WROTE:", OUTMD)
