#!/usr/bin/env python3
import csv
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

SRC = ROOT / "artifacts" / "phase8" / "output" / "run_feature_dataset.csv"
OUT = ROOT / "artifacts" / "phase8" / "reports" / "feature_dictionary.md"

rows = list(csv.DictReader(open(SRC)))
fields = rows[0].keys()

with open(OUT, "w") as f:
    f.write("# Feature Dictionary\n\n")
    for field in fields:
        if field in {"run_id","class_label","scenario_family","subtype","intensity","benign_type","binary_label"}:
            f.write(f"- **{field}**: metadata/label field\n")
        elif field.startswith("envoy_") or field.startswith("status_") or field.startswith("method_") or field.startswith("payload_") or field.startswith("pod_"):
            f.write(f"- **{field}**: Envoy-derived run summary feature\n")
        elif field.startswith("falco_"):
            f.write(f"- **{field}**: Falco-derived run summary feature\n")
        elif field.startswith("prom_"):
            f.write(f"- **{field}**: Prometheus-derived run summary feature\n")
        else:
            f.write(f"- **{field}**: engineered feature\n")

print("WROTE:", OUT)
