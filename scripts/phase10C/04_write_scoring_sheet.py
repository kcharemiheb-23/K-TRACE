#!/usr/bin/env python3
from pathlib import Path
import csv

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

QUESTIONS = list(csv.DictReader(open(ROOT / "artifacts" / "phase10C" / "output" / "evaluation_questions.csv")))
OUT = ROOT / "artifacts" / "phase10C" / "scoring" / "llm_scoring_sheet.csv"

models = ["mistral", "phi3:mini"]

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow([
        "model",
        "question_id",
        "question_type",
        "correctness_0_2",
        "grounding_0_2",
        "consistency_0_2",
        "no_hallucination_0_2",
        "analyst_usefulness_0_2",
        "comments"
    ])
    for model in models:
        for q in QUESTIONS:
            w.writerow([
                model,
                q["question_id"],
                q["question_type"],
                "",
                "",
                "",
                "",
                "",
                ""
            ])

print("WROTE:", OUT)
