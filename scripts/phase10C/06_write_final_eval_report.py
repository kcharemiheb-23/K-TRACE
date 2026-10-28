#!/usr/bin/env python3
from pathlib import Path
import pandas as pd
import csv

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

QUEST = list(csv.DictReader(open(ROOT / "artifacts" / "phase10C" / "output" / "evaluation_questions.csv")))
AGG = pd.read_csv(ROOT / "artifacts" / "phase10C" / "output" / "llm_score_aggregation.csv")
OUT = ROOT / "artifacts" / "phase10C" / "reports" / "phase10C_final_report.md"

best_model = AGG.iloc[0]["model"]

with open(OUT, "w") as f:
    f.write("# Phase 10C Final Report\n\n")
    f.write("## Goal\n")
    f.write("Evaluate multiple local LLMs on the same RAG-backed IDS reasoning tasks.\n\n")

    f.write("## Compared models\n")
    for model in AGG["model"]:
        f.write(f"- {model}\n")
    f.write("\n")

    f.write("## Evaluation questions\n")
    for q in QUEST:
        f.write(f"- {q['question_id']} | {q['question_type']} | {q['question_text']}\n")
    f.write("\n")

    f.write("## Aggregate score summary\n")
    f.write("```text\n")
    f.write(AGG.to_string(index=False))
    f.write("\n```\n\n")

    f.write("## Best model\n")
    f.write(f"- {best_model}\n\n")

    f.write("## Interpretation notes\n")
    f.write("- The best model is the one with the strongest average balance across correctness, grounding, consistency, hallucination resistance, and analyst usefulness.\n")
    f.write("- Results remain specific to the current corpus, prompt design, and local runtime environment.\n")
    f.write("- This phase evaluates reasoning quality, not raw intrusion detection accuracy.\n")

print("WROTE:", OUT)
