#!/usr/bin/env python3
from pathlib import Path
import csv

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

BENCH = ROOT / "artifacts" / "phase10V" / "benchmark" / "validation_benchmark.csv"
OUT = ROOT / "artifacts" / "phase10R" / "benchmark" / "retriever_queries.csv"

QUERY_TEMPLATES = {
    "A1": {
        "family_name": "A1_HTTP_PORTFLOOD",
        "semantic": "Retrieve evidence for HTTP request flooding, elevated frontend request volume, port probing behavior, high request counts, and service traffic pressure in the cloud-native IDS.",
    },
    "A2": {
        "family_name": "A2_INVALID_REQUEST_SPRAY",
        "semantic": "Retrieve evidence for invalid request spray, malformed HTTP methods, suspicious paths, 4xx responses, abnormal URI patterns, and application-layer probing.",
    },
    "A3": {
        "family_name": "A3_RUNTIME_RECON",
        "semantic": "Retrieve evidence for runtime reconnaissance, shell commands, process discovery, filesystem inspection, Falco runtime alerts, and suspicious container activity.",
    },
    "A4": {
        "family_name": "A4_EXPLOIT_LIKE_PAYLOADS",
        "semantic": "Retrieve evidence for exploit-like payloads, path traversal strings, injection-like URLs, suspicious encoded payloads, and malicious HTTP payload patterns.",
    },
    "BENIGN": {
        "family_name": "BENIGN",
        "semantic": "Retrieve evidence for benign cloud-native microservice behavior, normal browsing, controlled idle windows, normal load, expected service traffic, and non-attack activity.",
    },
}

def family_prefix(label):
    label = (label or "").strip()
    if label == "BENIGN" or label.startswith("BENIGN"):
        return "BENIGN"
    if label.startswith("A1"):
        return "A1"
    if label.startswith("A2"):
        return "A2"
    if label.startswith("A3"):
        return "A3"
    if label.startswith("A4"):
        return "A4"
    return "UNKNOWN"

rows = list(csv.DictReader(open(BENCH, newline="")))

out_rows = []
qnum = 1

for r in rows:
    run_id = r.get("run_id", "").strip()
    class_label = r.get("class_label", "").strip()
    prefix = family_prefix(class_label)
    info = QUERY_TEMPLATES.get(prefix, QUERY_TEMPLATES["BENIGN"])

    out_rows.append({
        "query_id": f"Q{qnum:03d}",
        "run_id": run_id,
        "expected_class": class_label,
        "expected_family": prefix,
        "query_type": "case_id_query",
        "query_text": f"Retrieve evidence explaining IDS case {run_id} and its security-relevant telemetry behavior.",
        "top_k": 10,
        "purpose": "Tests whether retrieval depends on direct case document matching or self-hit behavior."
    })
    qnum += 1

    out_rows.append({
        "query_id": f"Q{qnum:03d}",
        "run_id": run_id,
        "expected_class": class_label,
        "expected_family": prefix,
        "query_type": "semantic_family_query",
        "query_text": info["semantic"],
        "top_k": 10,
        "purpose": "Tests semantic retrieval of relevant evidence without using the run identifier."
    })
    qnum += 1

with open(OUT, "w", newline="", encoding="utf-8") as f:
    fieldnames = ["query_id", "run_id", "expected_class", "expected_family", "query_type", "query_text", "top_k", "purpose"]
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

print("WROTE:", OUT)
print("QUERIES:", len(out_rows))
