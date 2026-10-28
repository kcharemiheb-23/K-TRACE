#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import subprocess

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

QUESTIONS = ROOT / "artifacts" / "phase10C" / "output" / "evaluation_questions.csv"
OUTDIR = ROOT / "artifacts" / "phase10C" / "evaluation_results"
REPORT = ROOT / "artifacts" / "phase10C" / "reports" / "phase10C_run_report.md"

MODELS = ["mistral", "phi3:mini"]

script = ROOT / "scripts" / "phase10B" / "05_reason_with_rag.py"

rows = list(csv.DictReader(open(QUESTIONS)))

written = []

for model in MODELS:
    safe_model = model.replace(":", "_")
    for r in rows:
        qid = r["question_id"]
        qtext = r["question_text"]
        save_name = f"{safe_model}_{qid}"
        cmd = [
            "python3",
            str(script),
            "--question", qtext,
            "--model", model,
            "--top_k", "4",
            "--save_name", save_name,
        ]
        print("RUNNING:", " ".join(cmd))
        subprocess.run(cmd, check=True)
        written.append(f"{save_name}.json")

with open(REPORT, "w") as f:
    f.write("# Phase 10C Run Report\n\n")
    f.write(f"- total_models: {len(MODELS)}\n")
    f.write(f"- total_questions: {len(rows)}\n")
    f.write(f"- total_outputs: {len(written)}\n\n")
    for name in written:
        f.write(f"- {name}\n")

print("WROTE:", REPORT)
