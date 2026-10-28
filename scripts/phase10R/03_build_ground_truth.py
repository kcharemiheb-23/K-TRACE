#!/usr/bin/env python3
from pathlib import Path
import csv
import json
import re

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

QUERIES = ROOT / "artifacts" / "phase10R" / "benchmark" / "retriever_queries.csv"
CHUNKS = ROOT / "artifacts" / "phase10B" / "chunks" / "chunk_records.jsonl"
OUT = ROOT / "artifacts" / "phase10R" / "scoring" / "retriever_ground_truth.csv"
POLICY = ROOT / "artifacts" / "phase10R" / "reports" / "ground_truth_policy.md"

FAMILY_KEYWORDS = {
    "A1": [
        "A1", "HTTP_PORTFLOOD", "portflood", "http flood", "flood",
        "request volume", "request count", "traffic pressure", "port probing",
        "frontend request", "high request"
    ],
    "A2": [
        "A2", "INVALID_REQUEST_SPRAY", "invalid request", "malformed",
        "bad path", "suspicious path", "4xx", "TRACE", "abnormal uri",
        "application-layer probing"
    ],
    "A3": [
        "A3", "RUNTIME_RECON", "runtime recon", "runtime reconnaissance",
        "Falco", "shell", "process", "filesystem", "whoami", "uname",
        "cat /etc/passwd", "container activity"
    ],
    "A4": [
        "A4", "EXPLOIT_LIKE_PAYLOADS", "exploit-like", "payload",
        "path traversal", "injection", "encoded payload", "suspicious URL",
        "suspicious URI"
    ],
    "BENIGN": [
        "BENIGN", "benign", "normal", "idle", "browse", "non-attack",
        "baseline", "normal load", "controlled idle", "continuous browse"
    ],
}

def load_chunks():
    rows = []
    with open(CHUNKS, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                rows.append(json.loads(line))
    return rows

def chunk_family(row):
    name = row.get("doc_name", "") or ""
    stem = row.get("doc_stem", "") or ""
    text = f"{name} {stem}"

    if name.startswith("BENIGN") or stem.startswith("BENIGN"):
        return "BENIGN"
    for fam in ["A1", "A2", "A3", "A4"]:
        if name.startswith(fam + "_") or stem.startswith(fam + "_"):
            return fam
    return "UNKNOWN"

def keyword_match(expected_family, row):
    text = " ".join([
        str(row.get("doc_name", "")),
        str(row.get("doc_stem", "")),
        str(row.get("section", "")),
        str(row.get("text", "")),
    ]).lower()

    for kw in FAMILY_KEYWORDS.get(expected_family, []):
        if kw.lower() in text:
            return True, kw
    return False, ""

def is_relevant(query, chunk):
    expected = query["expected_family"]
    cfam = chunk_family(chunk)

    # Strongest rule: same-family case document.
    if cfam == expected and chunk.get("section") == "cases":
        return 1, "same_family_case_document"

    # Benign special case.
    if expected == "BENIGN" and cfam == "BENIGN":
        return 1, "benign_family_document"

    # Methodology/features/glossary documents can be relevant if they contain expected-family vocabulary.
    matched, kw = keyword_match(expected, chunk)
    if matched and chunk.get("section") in {"methodology", "features", "ml_results", "glossary", "cases"}:
        return 1, f"keyword_policy_match:{kw}"

    return 0, "not_relevant_under_policy"

queries = list(csv.DictReader(open(QUERIES, newline="", encoding="utf-8")))
chunks = load_chunks()

out_rows = []
for q in queries:
    relevant_count = 0
    for c in chunks:
        rel, reason = is_relevant(q, c)
        if rel == 1:
            relevant_count += 1
            out_rows.append({
                "query_id": q["query_id"],
                "run_id": q["run_id"],
                "query_type": q["query_type"],
                "expected_family": q["expected_family"],
                "expected_class": q["expected_class"],
                "chunk_id": c.get("chunk_id"),
                "doc_name": c.get("doc_name"),
                "section": c.get("section"),
                "source_path": c.get("source_path"),
                "relevance": rel,
                "relevance_reason": reason,
            })

    if relevant_count == 0:
        print("WARNING: no relevant chunks found for", q["query_id"], q["expected_family"], q["run_id"])

with open(OUT, "w", newline="", encoding="utf-8") as f:
    fieldnames = [
        "query_id", "run_id", "query_type", "expected_family", "expected_class",
        "chunk_id", "doc_name", "section", "source_path", "relevance", "relevance_reason"
    ]
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(out_rows)

with open(POLICY, "w", encoding="utf-8") as f:
    f.write("# Phase 10R Ground-Truth Relevance Policy\n\n")
    f.write("## Purpose\n\n")
    f.write("This file defines how relevant documents are selected for retriever evaluation. ")
    f.write("Ground truth is defined independently of the retriever ranking.\n\n")

    f.write("## Relevance labels\n\n")
    f.write("| Label | Meaning |\n")
    f.write("|---:|---|\n")
    f.write("| 1 | Relevant to the expected IDS evidence need |\n")
    f.write("| 0 | Irrelevant or not included in the ground-truth relevant set |\n\n")

    f.write("## Relevance criteria\n\n")
    f.write("A chunk is relevant if it satisfies at least one of these rules:\n\n")
    f.write("1. It is a same-family case document for the expected family.\n")
    f.write("2. It is a benign family document for BENIGN queries.\n")
    f.write("3. It is a methodology, feature, ML result, glossary, or case chunk containing vocabulary directly associated with the expected family.\n\n")

    f.write("## Family-specific evidence rules\n\n")
    for fam, kws in FAMILY_KEYWORDS.items():
        f.write(f"### {fam}\n\n")
        f.write("Relevant vocabulary includes:\n")
        for kw in kws:
            f.write(f"- {kw}\n")
        f.write("\n")

    f.write("## Research note\n\n")
    f.write("This policy is intentionally explicit and reproducible. ")
    f.write("It can be manually refined later, but Phase 10R begins with a documented independent relevance policy so that Precision@k, Recall@k, and MRR are meaningful.\n")

print("WROTE:", OUT)
print("WROTE:", POLICY)
print("GROUND_TRUTH_ROWS:", len(out_rows))
