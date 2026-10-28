#!/usr/bin/env python3
from pathlib import Path
import csv

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
OUT = ROOT / "artifacts" / "phase10C" / "output" / "evaluation_questions.csv"

rows = [
    ["Q1", "classification_explanation", "Why would a case be considered A3 runtime recon rather than A1 flooding?"],
    ["Q2", "attack_evidence", "Which evidence should an analyst use to justify that a suspicious run is an attack?"],
    ["Q3", "feature_interpretation", "Which features indicate abnormal behavior in suspicious cases?"],
    ["Q4", "class_comparison", "Compare A1 HTTP port flood and A2 invalid request spray in terms of expected behavior."],
    ["Q5", "analyst_decision", "What should an analyst do after the system classifies a suspicious run as an attack?"],
    ["Q6", "rag_grounding", "Which sources are most useful for explaining why a run was classified as A3?"],
]

with open(OUT, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["question_id", "question_type", "question_text"])
    w.writerows(rows)

print("WROTE:", OUT)
