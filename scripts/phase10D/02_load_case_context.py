#!/usr/bin/env python3
from pathlib import Path
import argparse
import json

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

CASE_DIR = ROOT / "artifacts" / "phase10A" / "corpus" / "cases"

BEST_BINARY_MODEL = "DecisionTree"
BEST_MULTICLASS_MODEL = "RandomForest"

def extract_field(text, prefix):
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_id", required=True)
    args = parser.parse_args()

    case_path = CASE_DIR / f"{args.run_id}.md"
    if not case_path.exists():
        raise SystemExit(f"CASE DOC NOT FOUND: {case_path}")

    text = case_path.read_text()

    obj = {
        "run_id": extract_field(text, "- run_id"),
        "class_label": extract_field(text, "- class_label"),
        "binary_label": extract_field(text, "- binary_label"),
        "scenario_family": extract_field(text, "- scenario_family"),
        "subtype": extract_field(text, "- subtype"),
        "intensity": extract_field(text, "- intensity"),
        "best_binary_model": BEST_BINARY_MODEL,
        "best_multiclass_model": BEST_MULTICLASS_MODEL,
        "binary_pred_label": "",
        "multiclass_pred_label": "",
        "source_case_doc": str(case_path)
    }

    blocks = text.split("## ")
    for block in blocks:
        if block.startswith("Binary model result"):
            for line in block.splitlines():
                if line.startswith("- pred_label:"):
                    obj["binary_pred_label"] = line.split(":", 1)[1].strip()
        if block.startswith("Multiclass model result"):
            for line in block.splitlines():
                if line.startswith("- pred_label:"):
                    obj["multiclass_pred_label"] = line.split(":", 1)[1].strip()

    print(json.dumps(obj, indent=2))

if __name__ == "__main__":
    main()
