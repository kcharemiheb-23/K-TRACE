#!/usr/bin/env python3
from pathlib import Path
import json

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

CHUNKS = ROOT / "artifacts" / "phase10B" / "chunks" / "chunk_records.jsonl"
VSTORE = ROOT / "artifacts" / "phase10B" / "vectorstore"
OUT = ROOT / "artifacts" / "phase10R" / "reports" / "retriever_approach.md"

def count_chunks(path):
    if not path.exists():
        return 0
    with open(path, "r", encoding="utf-8") as f:
        return sum(1 for _ in f if _.strip())

def inspect_sections(path):
    sections = {}
    examples = []
    if not path.exists():
        return sections, examples

    with open(path, "r", encoding="utf-8") as f:
        for i, line in enumerate(f):
            if not line.strip():
                continue
            row = json.loads(line)
            sec = row.get("section", "UNKNOWN")
            sections[sec] = sections.get(sec, 0) + 1
            if len(examples) < 5:
                examples.append({
                    "chunk_id": row.get("chunk_id"),
                    "doc_name": row.get("doc_name"),
                    "section": sec,
                    "source_path": row.get("source_path")
                })
    return sections, examples

chunk_count = count_chunks(CHUNKS)
sections, examples = inspect_sections(CHUNKS)
vectorstore_files = []
if VSTORE.exists():
    vectorstore_files = [str(p.relative_to(ROOT)) for p in VSTORE.rglob("*") if p.is_file()][:30]

with open(OUT, "w", encoding="utf-8") as f:
    f.write("# Phase 10R Retriever Approach\n\n")

    f.write("## Current retriever type\n\n")
    f.write("The current implemented retriever is a **dense semantic vector retriever**.\n\n")
    f.write("It is not an exact keyword search engine and it is not a BM25 lexical retriever unless a separate BM25 component is later added.\n\n")

    f.write("## Retrieval formulation\n\n")
    f.write("The retrieval process is formulated as:\n\n")
    f.write("```text\n")
    f.write("query text\n")
    f.write("→ embedding(query)\n")
    f.write("→ vector similarity search against embedded corpus chunks\n")
    f.write("→ ranked top-k chunks\n")
    f.write("→ retrieved evidence passed to the LLM reasoning layer\n")
    f.write("```\n\n")

    f.write("More formally:\n\n")
    f.write("```text\n")
    f.write("q = embedding(query)\n")
    f.write("d_i = embedding(document_chunk_i)\n")
    f.write("score(q, d_i) = vector similarity(q, d_i)\n")
    f.write("top-k = highest scoring chunks\n")
    f.write("```\n\n")

    f.write("## Search classification\n\n")
    f.write("| Search approach | Used in current system? | Explanation |\n")
    f.write("|---|---:|---|\n")
    f.write("| Exact keyword search | No | The current retriever does not only match identical terms. |\n")
    f.write("| BM25 sparse lexical search | No | BM25 is not currently the implemented retrieval formulation. |\n")
    f.write("| Dense semantic search | Yes | Query and chunks are encoded into vectors and compared semantically. |\n")
    f.write("| Hybrid lexical + semantic search | Not yet | This can be proposed later as a Phase 10U upgrade. |\n\n")

    f.write("## Embedding and vector storage\n\n")
    f.write("- Embedding model used in the project design: `all-MiniLM-L6-v2`\n")
    f.write("- Vector database used in the project design: `Chroma`\n")
    f.write("- Chunk file inspected: `artifacts/phase10B/chunks/chunk_records.jsonl`\n")
    f.write("- Vector store inspected: `artifacts/phase10B/vectorstore`\n\n")

    f.write("## Relationship between the researcher and the embedding\n\n")
    f.write("The researcher defines the corpus, chunking policy, query formulation, relevance criteria, and evaluation metrics. ")
    f.write("The embedding model transforms query text and document chunks into a vector space. ")
    f.write("The retriever then ranks chunks according to vector similarity. ")
    f.write("Therefore, the embedding model is not the research contribution by itself; the contribution is the controlled design, evaluation, and interpretation of retrieval behavior in the IDS reasoning pipeline.\n\n")

    f.write("## Corpus/chunk inspection\n\n")
    f.write(f"- chunk_count: {chunk_count}\n")
    f.write("- section_counts:\n")
    for sec, count in sorted(sections.items()):
        f.write(f"  - {sec}: {count}\n")
    f.write("\n")

    f.write("## Example chunks\n\n")
    for ex in examples:
        f.write(f"- chunk_id={ex['chunk_id']} | doc={ex['doc_name']} | section={ex['section']}\n")
    f.write("\n")

    f.write("## Vector store files observed\n\n")
    for p in vectorstore_files:
        f.write(f"- {p}\n")

    f.write("\n## Known limitation\n\n")
    f.write("Dense semantic retrieval can retrieve conceptually similar but class-wrong evidence. ")
    f.write("This is why Phase 10R evaluates class-family contamination, same-family retrieval ratio, rank quality, and Recall@k.\n")

print("WROTE:", OUT)
