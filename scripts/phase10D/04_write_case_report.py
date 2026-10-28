#!/usr/bin/env python3
import argparse
import json
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
RESULTS = ROOT / "artifacts" / "phase10D" / "results"
REPORTS = ROOT / "artifacts" / "phase10D" / "reports"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_id", required=True)
    args = parser.parse_args()

    src = RESULTS / f"{args.run_id}.json"
    if not src.exists():
        raise SystemExit(f"RESULT NOT FOUND: {src}")

    data = json.loads(src.read_text())

    out = REPORTS / f"{args.run_id}.md"
    with open(out, "w") as f:
        f.write(f"# IDS Reasoning Report - {data['run_id']}\n\n")

        f.write("## Run Metadata\n")
        f.write(f"- run_id: {data['run_id']}\n")
        f.write(f"- class_label: {data['class_label']}\n")
        f.write(f"- binary_label: {data['binary_label']}\n")
        f.write(f"- scenario_family: {data['scenario_family']}\n")
        f.write(f"- subtype: {data['subtype']}\n")
        f.write(f"- intensity: {data['intensity']}\n\n")

        f.write("## ML Context\n")
        f.write(f"- best_binary_model: {data['best_binary_model']}\n")
        f.write(f"- best_multiclass_model: {data['best_multiclass_model']}\n")
        f.write(f"- binary_pred_label: {data['binary_pred_label']}\n")
        f.write(f"- multiclass_pred_label: {data['multiclass_pred_label']}\n\n")

        f.write("## LLM Decision\n")
        f.write(f"- llm_model: {data['llm_model']}\n")
        f.write(f"- decision: {data['llm_decision']}\n")
        f.write(f"- confidence: {data['confidence_statement']}\n\n")

        f.write("## Explanation\n")
        f.write(data["llm_explanation"] + "\n\n")

        f.write("## Evidence Used\n")
        f.write(data["llm_evidence_used"] + "\n\n")

        f.write("## Recommended Action\n")
        f.write(data["recommended_action"] + "\n\n")

        f.write("## Retrieved Sources\n")
        for s in data["retrieved_sources"]:
            f.write(f"- {s['doc_name']} | {s['section']} | {s['chunk_id']}\n")

    print("WROTE:", out)

if __name__ == "__main__":
    main()
