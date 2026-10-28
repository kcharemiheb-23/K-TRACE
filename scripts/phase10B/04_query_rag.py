#!/usr/bin/env python3
import argparse
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import json

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
VDBDIR = ROOT / "artifacts" / "phase10B" / "vectorstore"
OUTDIR = ROOT / "artifacts" / "phase10B" / "query_results"

MODEL_NAME = "all-MiniLM-L6-v2"
COLLECTION_NAME = "ids_rag_corpus"

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--top_k", type=int, default=4)
    parser.add_argument("--save_name", default="last_query")
    args = parser.parse_args()

    model = SentenceTransformer(MODEL_NAME)
    qvec = model.encode([args.question]).tolist()[0]

    client = chromadb.PersistentClient(path=str(VDBDIR))
    collection = client.get_collection(COLLECTION_NAME)

    res = collection.query(
        query_embeddings=[qvec],
        n_results=args.top_k,
    )

    out_path = OUTDIR / f"{args.save_name}.json"
    with open(out_path, "w") as f:
        json.dump(res, f, indent=2)

    print("QUESTION:", args.question)
    print("TOP_K:", args.top_k)
    print("SAVED:", out_path)

    docs = res["documents"][0]
    metas = res["metadatas"][0]
    ids = res["ids"][0]

    for i, (cid, meta, doc) in enumerate(zip(ids, metas, docs), start=1):
        print(f"\n[{i}] {cid}")
        print("section:", meta["section"])
        print("doc_name:", meta["doc_name"])
        print("source_path:", meta["source_path"])
        print("text_preview:", doc[:300].replace("\n", " "))

if __name__ == "__main__":
    main()
