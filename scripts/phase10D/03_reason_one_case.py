#!/usr/bin/env python3
import argparse
import json
from pathlib import Path
import chromadb
from sentence_transformers import SentenceTransformer
import ollama

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

CASE_DIR = ROOT / "artifacts" / "phase10A" / "corpus" / "cases"
VDBDIR = ROOT / "artifacts" / "phase10B" / "vectorstore"
OUTDIR = ROOT / "artifacts" / "phase10D" / "results"

COLLECTION_NAME = "ids_rag_corpus"
EMBED_MODEL = "all-MiniLM-L6-v2"
LLM_MODEL = "mistral"

BEST_BINARY_MODEL = "DecisionTree"
BEST_MULTICLASS_MODEL = "RandomForest"

PROMPT_TEMPLATE = """You are the reasoning layer of a cloud-native intrusion detection project.

You must use only the retrieved evidence and the case metadata.
Do not invent facts.
Do not override the available evidence.

Return ONLY valid JSON with this exact structure:
{{
  "llm_decision": "",
  "llm_explanation": "",
  "llm_evidence_used": "",
  "recommended_action": "",
  "confidence_statement": ""
}}

Case metadata:
{case_metadata}

Retrieved evidence:
{context}
"""

def extract_field(text, prefix):
    for line in text.splitlines():
        if line.startswith(prefix):
            return line.split(":", 1)[1].strip()
    return ""

def load_case(run_id):
    case_path = CASE_DIR / f"{run_id}.md"
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

    return obj, text

def retrieve_context(question, top_k):
    em = SentenceTransformer(EMBED_MODEL)
    qvec = em.encode([question]).tolist()[0]

    client = chromadb.PersistentClient(path=str(VDBDIR))
    collection = client.get_collection(COLLECTION_NAME)

    res = collection.query(query_embeddings=[qvec], n_results=top_k)

    docs = res["documents"][0]
    metas = res["metadatas"][0]
    ids = res["ids"][0]

    context_parts = []
    sources = []
    for cid, meta, doc in zip(ids, metas, docs):
        context_parts.append(
            f"[SOURCE: {meta['doc_name']} | SECTION: {meta['section']} | CHUNK_ID: {cid}]\n{doc}\n"
        )
        sources.append({
            "chunk_id": cid,
            "doc_name": meta["doc_name"],
            "section": meta["section"],
            "source_path": meta["source_path"]
        })

    return "\n---\n".join(context_parts), sources

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run_id", required=True)
    parser.add_argument("--top_k", type=int, default=4)
    args = parser.parse_args()

    case_obj, case_text = load_case(args.run_id)

    question = f"Analyze run {args.run_id}. Based on the ML context and retrieved evidence, decide whether this case should be treated as an attack or benign, explain why, and recommend the next analyst action."

    context, sources = retrieve_context(question, args.top_k)

    prompt = PROMPT_TEMPLATE.format(
        case_metadata=json.dumps(case_obj, indent=2),
        context=context
    )

    resp = ollama.generate(model=LLM_MODEL, prompt=prompt)
    raw = resp["response"].strip()

    try:
        llm_json = json.loads(raw)
    except Exception:
        llm_json = {
            "llm_decision": "PARSE_ERROR",
            "llm_explanation": raw,
            "llm_evidence_used": "The model did not return valid JSON.",
            "recommended_action": "Inspect the raw response manually.",
            "confidence_statement": "Low confidence due to formatting failure."
        }

    final_obj = {
        **case_obj,
        "retrieved_sources": sources,
        "llm_model": LLM_MODEL,
        **llm_json
    }

    out_path = OUTDIR / f"{args.run_id}.json"
    with open(out_path, "w") as f:
        json.dump(final_obj, f, indent=2)

    print("SAVED:", out_path)
    print(json.dumps(final_obj, indent=2))

if __name__ == "__main__":
    main()
