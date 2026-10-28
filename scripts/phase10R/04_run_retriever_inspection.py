#!/usr/bin/env python3
from pathlib import Path
import argparse
import csv
import json
import math
import sys

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

QUERIES = ROOT / "artifacts" / "phase10R" / "benchmark" / "retriever_queries.csv"
CHUNKS = ROOT / "artifacts" / "phase10B" / "chunks" / "chunk_records.jsonl"
VSTORE = ROOT / "artifacts" / "phase10B" / "vectorstore"

OUT_CSV = ROOT / "artifacts" / "phase10R" / "output" / "retrieval_ranked_results.csv"
OUT_JSONL = ROOT / "artifacts" / "phase10R" / "output" / "retrieval_ranked_results.jsonl"

def load_chunk_map():
    by_id = {}
    by_doc = {}
    with open(CHUNKS, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                cid = str(row.get("chunk_id"))
                by_id[cid] = row
                by_doc.setdefault(row.get("doc_name"), []).append(row)
    return by_id, by_doc

def family_from_doc(name):
    name = name or ""
    if name.startswith("BENIGN"):
        return "BENIGN"
    for fam in ["A1", "A2", "A3", "A4"]:
        if name.startswith(fam + "_"):
            return fam
    return "UNKNOWN"

def attack_vs_benign(fam):
    if fam == "BENIGN":
        return "BENIGN"
    if fam in {"A1", "A2", "A3", "A4"}:
        return "ATTACK"
    return "UNKNOWN"

def normalize_similarity(distance):
    # Chroma often returns distance, not similarity.
    # This creates a readable monotonic score where smaller distance gives higher score.
    try:
        d = float(distance)
        return 1.0 / (1.0 + max(d, 0.0))
    except Exception:
        return ""

def first_text_preview(text, n=240):
    text = " ".join((text or "").split())
    return text[:n]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--top_k", type=int, default=10)
    parser.add_argument("--collection", default="")
    args = parser.parse_args()

    queries = list(csv.DictReader(open(QUERIES, newline="", encoding="utf-8")))
    chunk_by_id, _ = load_chunk_map()

    try:
        import chromadb
    except Exception as e:
        raise SystemExit(f"ERROR: chromadb is not available in this environment: {e}")

    if not VSTORE.exists():
        raise SystemExit(f"ERROR: vector store path not found: {VSTORE}")

    client = chromadb.PersistentClient(path=str(VSTORE))
    collections = client.list_collections()

    if not collections:
        raise SystemExit("ERROR: no Chroma collections found in vector store")

    collection_names = []
    for c in collections:
        if hasattr(c, "name"):
            collection_names.append(c.name)
        else:
            collection_names.append(str(c))

    if args.collection:
        collection_name = args.collection
    else:
        collection_name = collection_names[0]

    collection = client.get_collection(collection_name)

    print("USING_CHROMA_COLLECTION:", collection_name)
    print("QUERY_COUNT:", len(queries))

    out_rows = []

    with open(OUT_JSONL, "w", encoding="utf-8") as jf:
        for q in queries:
            qid = q["query_id"]
            query_text = q["query_text"]
            top_k = int(q.get("top_k") or args.top_k)

            result = collection.query(
                query_texts=[query_text],
                n_results=top_k,
                include=["documents", "metadatas", "distances"]
            )

            ids = result.get("ids", [[]])[0]
            docs = result.get("documents", [[]])[0]
            metas = result.get("metadatas", [[]])[0]
            distances = result.get("distances", [[]])[0]

            for rank, rid in enumerate(ids, start=1):
                rid_str = str(rid)
                meta = metas[rank - 1] if rank - 1 < len(metas) else {}
                doc_text = docs[rank - 1] if rank - 1 < len(docs) else ""
                dist = distances[rank - 1] if rank - 1 < len(distances) else ""

                chunk = chunk_by_id.get(rid_str, {})

                chunk_id = rid_str
                doc_name = meta.get("doc_name") or chunk.get("doc_name") or ""
                section = meta.get("section") or chunk.get("section") or ""
                source_path = meta.get("source_path") or chunk.get("source_path") or ""
                text = doc_text or chunk.get("text") or ""

                retrieved_family = family_from_doc(doc_name)
                expected_family = q["expected_family"]

                self_hit = 1 if q["run_id"] and q["run_id"] in doc_name else 0
                same_family = 1 if retrieved_family == expected_family else 0
                contamination = 1 if retrieved_family not in {expected_family, "UNKNOWN"} else 0

                expected_side = attack_vs_benign(expected_family)
                retrieved_side = attack_vs_benign(retrieved_family)
                benign_attack_contamination = 1 if expected_side != "UNKNOWN" and retrieved_side != "UNKNOWN" and expected_side != retrieved_side else 0

                row = {
                    "query_id": qid,
                    "run_id": q["run_id"],
                    "query_type": q["query_type"],
                    "query_text": query_text,
                    "expected_class": q["expected_class"],
                    "expected_family": expected_family,
                    "rank": rank,
                    "chunk_id": chunk_id,
                    "doc_name": doc_name,
                    "section": section,
                    "source_path": source_path,
                    "distance": dist,
                    "similarity_score_readable": normalize_similarity(dist),
                    "retrieved_family": retrieved_family,
                    "same_family_flag": same_family,
                    "self_hit_flag": self_hit,
                    "cross_class_contamination_flag": contamination,
                    "benign_attack_contamination_flag": benign_attack_contamination,
                    "text_preview": first_text_preview(text),
                    "retrieval_backend": "chroma_dense_vector",
                    "collection_name": collection_name,
                }

                out_rows.append(row)
                jf.write(json.dumps(row, ensure_ascii=False) + "\n")

    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        fieldnames = [
            "query_id", "run_id", "query_type", "query_text", "expected_class", "expected_family",
            "rank", "chunk_id", "doc_name", "section", "source_path", "distance",
            "similarity_score_readable", "retrieved_family", "same_family_flag", "self_hit_flag",
            "cross_class_contamination_flag", "benign_attack_contamination_flag",
            "text_preview", "retrieval_backend", "collection_name"
        ]
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(out_rows)

    print("WROTE:", OUT_CSV)
    print("WROTE:", OUT_JSONL)
    print("ROWS:", len(out_rows))

if __name__ == "__main__":
    main()
