#!/usr/bin/env python3
from pathlib import Path
import pandas as pd

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

TEST = pd.read_csv(ROOT / "artifacts" / "phase8" / "output" / "split_test_runs.csv")

bin_sum = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / "binary_best_model_summary_v2.csv").iloc[0].to_dict()
mul_sum = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / "multiclass_best_model_summary_v2.csv").iloc[0].to_dict()

binary_best = bin_sum["best_model"]
multiclass_best = mul_sum["best_model"]

BIN_PRED = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / f"binary_test_predictions_{binary_best}_v2.csv")
MUL_PRED = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / f"multiclass_test_predictions_{multiclass_best}_v2.csv")

BIN_TOP = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / f"binary_top_feature_importance_{binary_best}_v2.csv")
MUL_TOP = pd.read_csv(ROOT / "artifacts" / "phase9_v2" / "output" / f"multiclass_top_feature_importance_{multiclass_best}_v2.csv")

OUTDIR = ROOT / "artifacts" / "phase10A" / "corpus" / "cases"
INDEX = ROOT / "artifacts" / "phase10A" / "reports" / "phase10A_case_index.md"

bin_map = {r["run_id"]: r for _, r in BIN_PRED.iterrows()}
mul_map = {r["run_id"]: r for _, r in MUL_PRED.iterrows()}

top_bin = BIN_TOP.head(10)["importance"].to_dict()
top_mul = MUL_TOP.head(10)["importance"].to_dict()

written = []

for _, row in TEST.iterrows():
    run_id = row["run_id"]
    path = OUTDIR / f"{run_id}.md"

    with open(path, "w") as f:
        f.write(f"# Case Summary - {run_id}\n\n")
        f.write("## Run metadata\n")
        f.write(f"- run_id: {run_id}\n")
        f.write(f"- class_label: {row['class_label']}\n")
        f.write(f"- binary_label: {row['binary_label']}\n")
        f.write(f"- scenario_family: {row['scenario_family']}\n")
        f.write(f"- subtype: {row['subtype']}\n")
        f.write(f"- intensity: {row['intensity']}\n")
        f.write(f"- benign_type: {row.get('benign_type', '')}\n\n")

        if run_id in bin_map:
            b = bin_map[run_id]
            f.write("## Binary model result\n")
            f.write(f"- model: {binary_best}\n")
            f.write(f"- true_label: {b['true_label']}\n")
            f.write(f"- pred_label: {b['pred_label']}\n\n")

        if run_id in mul_map:
            m = mul_map[run_id]
            f.write("## Multiclass model result\n")
            f.write(f"- model: {multiclass_best}\n")
            f.write(f"- true_label: {m['true_label']}\n")
            f.write(f"- pred_label: {m['pred_label']}\n\n")

        f.write("## Top global binary features (best model)\n")
        for feat, val in top_bin.items():
            f.write(f"- {feat}: {val}\n")
        f.write("\n")

        f.write("## Top global multiclass features (best model)\n")
        for feat, val in top_mul.items():
            f.write(f"- {feat}: {val}\n")
        f.write("\n")

        f.write("## Notes\n")
        f.write("- This case document was generated from validated environment outputs.\n")
        f.write("- It is intended for later RAG retrieval and LLM reasoning.\n")

    written.append(path)

with open(INDEX, "w") as f:
    f.write("# Phase 10A Case Index\n\n")
    f.write(f"- total_case_docs: {len(written)}\n\n")
    for p in written:
        f.write(f"- {p.name}\n")

print("WROTE:", len(written), "case docs")
print("INDEX:", INDEX)
