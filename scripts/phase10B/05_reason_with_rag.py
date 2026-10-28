#!/usr/bin/env python3
import argparse
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import json
import ollama

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"
VDBDIR = ROOT / "artifacts" / "phase10B" / "vectorstore"
OUTDIR = ROOT / "artifacts" / "phase10B" / "query_results"

EMBED_MODEL = "all-MiniLM-L6-v2"
COLLECTION_NAME = "ids_rag_corpus"

PROMPT_TEMPLATE = """You are assisting a cloud-native intrusion detection project.

Use only the retrieved evidence below.
Do not invent missing facts.
Your job is to:
1. answer the question
2. justify the answer with evidence
3. mention the most relevant source documents
4. keep reasoning aligned with the ML-oriented project context

Question:
{question}

Retrieved evidence:
{context}

Return your answer in this structure:

Decision:
Explanation:
Evidence used:
Recommended analyst action:
"""

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--question", required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--top_k", type=int, default=4)
    parser.add_argument("--save_name", default="last_reasoning")
    args = parser.parse_args()

    em = SentenceTransformer(EMBED_MODEL)
    qvec = em.encode([args.question]).tolist()[0]

    client = chromadb.PersistentClient(path=str(VDBDIR))
    collection = client.get_collection(COLLECTION_NAME)

    res = collection.query(
        query_embeddings=[qvec],
        n_results=args.top_k,
    )

    docs = res["documents"][0]
    metas = res["metadatas"][0]
    ids = res["ids"][0]

    context_parts = []
    source_rows = []
    for cid, meta, doc in zip(ids, metas, docs):
        context_parts.append(
            f"[SOURCE: {meta['doc_name']} | SECTION: {meta['section']} | CHUNK_ID: {cid}]\n{doc}\n"
        )
        source_rows.append({
            "chunk_id": cid,
            "doc_name": meta["doc_name"],
            "section": meta["section"],
            "source_path": meta["source_path"],
        })

    context = "\n---\n".join(context_parts)
    prompt = PROMPT_TEMPLATE.format(question=args.question, context=context)

    resp = ollama.generate(model=args.model, prompt=prompt)
    answer = resp["response"]

    out = {
        "question": args.question,
        "model": args.model,
        "top_k": args.top_k,
        "sources": source_rows,
        "answer": answer,
    }

    out_path = OUTDIR / f"{args.save_name}.json"
    with open(out_path, "w") as f:
        json.dump(out, f, indent=2)

    print("MODEL:", args.model)
    print("QUESTION:", args.question)
    print("SAVED:", out_path)
    print("\nANSWER:\n")
    print(answer)

    print("\nSOURCES:")
    for s in source_rows:
        print("-", s["doc_name"], "|", s["section"], "|", s["chunk_id"])

if __name__ == "__main__":
    main()
