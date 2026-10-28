#!/usr/bin/env python3
from pathlib import Path

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
OUT = ROOT / "artifacts" / "phase10A" / "corpus" / "glossary" / "project_glossary.md"

with open(OUT, "w") as f:
    f.write("# Project Glossary\n\n")
    f.write("- **RAG**: Retrieval-Augmented Generation.\n")
    f.write("- **LLM**: Large Language Model.\n")
    f.write("- **Envoy**: service-mesh proxy telemetry source.\n")
    f.write("- **Falco**: runtime security telemetry source.\n")
    f.write("- **Prometheus**: metrics telemetry source.\n")
    f.write("- **Binary task**: ATTACK vs BENIGN classification.\n")
    f.write("- **Multiclass task**: BENIGN + A1 + A2 + A3 + A4 classification.\n")
    f.write("- **Case document**: one run-level knowledge document built from validated outputs.\n")
    f.write("- **Corpus**: the full document collection that will later be chunked and embedded.\n")
    f.write("- **Top-k retrieval**: selecting the k most relevant retrieved chunks.\n")

print("WROTE:", OUT)
