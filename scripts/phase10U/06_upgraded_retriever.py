#!/usr/bin/env python3
"""
Phase 10U Part C - Upgraded retriever module.

Exposes a single reusable function:

    retrieve(query_text, top_k=10, mode="rrf_plus_metadata_rerank",
             expected_family=None, rrf_k=60, metadata_boost=0.15) -> list[dict]

Modes:
  - "dense_only": Chroma vector search over ids_rag_corpus_v2 only.
  - "bm25_only": BM25Okapi search over the same chunks only.
  - "rrf": Reciprocal Rank Fusion of dense and BM25 rankings.
        RRF score = sum over rankers of 1 / (rrf_k + rank).
        rrf_k = 60 is the standard value from Cormack et al. SIGIR 2009.
  - "rrf_plus_metadata_rerank": RRF, then soft boost for chunks whose family
        metadata matches expected_family.
        Boost amount = metadata_boost * (1 / (rrf_k + 1)) so it is on the same
        order of magnitude as a single-rank improvement, and never overrides
        a strongly relevant non-family-matching chunk.

Returns a list of dicts in the same schema as Phase 10R retrieval rows so the
existing scoring pipeline at scripts/phase10R/05_score_retriever_smart_metrics.py
can consume the output directly.
"""
from __future__ import annotations

import json
import pickle
import re
from pathlib import Path
from typing import Optional

HOME = Path.home()
ROOT = HOME / "cloud-native-ids-azure"

CHROMA_PATH = ROOT / "artifacts" / "phase10U" / "vectorstore_v2"
COLLECTION_NAME = "ids_rag_corpus_v2"
BM25_INDEX = ROOT / "artifacts" / "phase10U" / "bm25" / "bm25_index.pkl"
BM25_CHUNKS = ROOT / "artifacts" / "phase10U" / "bm25" / "bm25_chunks.jsonl"
CHUNK_RECORDS = ROOT / "artifacts" / "phase10U" / "chunks" / "chunk_records_v2.jsonl"

VALID_MODES = {"dense_only", "bm25_only", "rrf", "rrf_plus_metadata_rerank"}

TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall((text or "").lower())


def family_of_doc_name(doc_name: str) -> str:
    name = (doc_name or "").upper()
    if name.startswith("BENIGN"):
        return "BENIGN"
    for fam in ("A1", "A2", "A3", "A4"):
        if name.startswith(fam + "_"):
            return fam
    return "UNKNOWN"


class _RetrieverState:
    """Lazy singleton holding loaded indexes so repeated retrieve() calls are cheap."""

    def __init__(self):
        self.collection = None
        self.bm25 = None
        self.bm25_records: list[dict] = []
        self.bm25_index_by_chunk_id: dict[str, int] = {}
        self.chunk_meta_by_id: dict[str, dict] = {}

    def ensure_loaded(self):
        if self.collection is None:
            import chromadb
            client = chromadb.PersistentClient(path=str(CHROMA_PATH))
            self.collection = client.get_collection(COLLECTION_NAME)

        if self.bm25 is None:
            with BM25_INDEX.open("rb") as f:
                self.bm25 = pickle.load(f)
            with BM25_CHUNKS.open(encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        rec = json.loads(line)
                        self.bm25_records.append(rec)
            self.bm25_index_by_chunk_id = {
                r["chunk_id"]: i for i, r in enumerate(self.bm25_records)
            }

        if not self.chunk_meta_by_id:
            with CHUNK_RECORDS.open(encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        r = json.loads(line)
                        self.chunk_meta_by_id[r["chunk_id"]] = r


_STATE = _RetrieverState()


def _dense_rank(query_text: str, n: int) -> list[tuple[str, float]]:
    """Return [(chunk_id, distance), ...] sorted by ascending distance."""
    res = _STATE.collection.query(
        query_texts=[query_text],
        n_results=n,
        include=["distances"],
    )
    ids = res.get("ids", [[]])[0]
    dists = res.get("distances", [[]])[0]
    return list(zip(ids, dists))


def _bm25_rank(query_text: str, n: int) -> list[tuple[str, float]]:
    """Return [(chunk_id, bm25_score), ...] sorted by descending score."""
    scores = _STATE.bm25.get_scores(_tokenize(query_text))
    ranked = sorted(
        ((_STATE.bm25_records[i]["chunk_id"], float(s)) for i, s in enumerate(scores)),
        key=lambda x: -x[1],
    )
    return ranked[:n]


def _rrf_fuse(rankings: list[list[tuple[str, float]]], rrf_k: int) -> dict[str, float]:
    """
    Reciprocal Rank Fusion.
    rankings is a list of per-ranker lists, each already sorted best-first.
    Returns a dict from chunk_id to fused score.
    """
    fused: dict[str, float] = {}
    for ranking in rankings:
        for rank_index, (cid, _score) in enumerate(ranking, start=1):
            fused[cid] = fused.get(cid, 0.0) + 1.0 / (rrf_k + rank_index)
    return fused


def _apply_metadata_boost(
    fused: dict[str, float],
    expected_family: Optional[str],
    rrf_k: int,
    boost: float,
) -> dict[str, float]:
    """Soft-boost chunks whose family metadata matches the expected family."""
    if not expected_family:
        return fused
    out = dict(fused)
    bonus = boost * (1.0 / (rrf_k + 1))
    for cid in list(out.keys()):
        meta = _STATE.chunk_meta_by_id.get(cid, {})
        if meta.get("family") == expected_family:
            out[cid] += bonus
    return out


def _build_result_row(cid: str, rank: int, similarity_value: float,
                      query_text: str) -> dict:
    """
    Render one result row in the Phase 10R-compatible schema so the existing
    scoring pipeline reads our output unchanged.
    """
    meta = _STATE.chunk_meta_by_id.get(cid, {})
    return {
        "chunk_id": cid,
        "doc_name": meta.get("doc_name", ""),
        "section": meta.get("section", ""),
        "source_path": meta.get("source_path", ""),
        "distance": float(similarity_value),
        "similarity_score_readable": float(similarity_value),
        "retrieved_family": meta.get("family", "UNKNOWN"),
        "rank": rank,
        "text_preview": (meta.get("text", "") or "")[:240].replace("\n", " "),
    }


def retrieve(
    query_text: str,
    top_k: int = 10,
    mode: str = "rrf_plus_metadata_rerank",
    expected_family: Optional[str] = None,
    rrf_k: int = 60,
    metadata_boost: float = 0.15,
    candidate_pool: int = 30,
) -> list[dict]:
    """
    Run the upgraded retriever in the requested mode and return top_k rows.

    candidate_pool controls how many candidates each underlying ranker returns
    before fusion. Larger values give RRF more material to work with at the
    cost of more dictionary work.
    """
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be one of {VALID_MODES}, got {mode!r}")

    _STATE.ensure_loaded()

    if mode == "dense_only":
        ranked = _dense_rank(query_text, top_k)
        return [
            _build_result_row(cid, rank=i + 1,
                              similarity_value=1.0 / (1.0 + max(d, 0.0)),
                              query_text=query_text)
            for i, (cid, d) in enumerate(ranked)
        ]

    if mode == "bm25_only":
        ranked = _bm25_rank(query_text, top_k)
        return [
            _build_result_row(cid, rank=i + 1,
                              similarity_value=score,
                              query_text=query_text)
            for i, (cid, score) in enumerate(ranked)
        ]

    # Hybrid modes need a candidate pool from each ranker.
    dense = _dense_rank(query_text, candidate_pool)
    bm25 = _bm25_rank(query_text, candidate_pool)

    fused = _rrf_fuse([dense, bm25], rrf_k=rrf_k)

    if mode == "rrf_plus_metadata_rerank":
        fused = _apply_metadata_boost(
            fused, expected_family=expected_family,
            rrf_k=rrf_k, boost=metadata_boost,
        )

    ordered = sorted(fused.items(), key=lambda kv: -kv[1])[:top_k]
    return [
        _build_result_row(cid, rank=i + 1,
                          similarity_value=score,
                          query_text=query_text)
        for i, (cid, score) in enumerate(ordered)
    ]


if __name__ == "__main__":
    # Smoke test when invoked directly. Not part of the evaluation pipeline.
    probes = [
        ("Retrieve evidence for runtime reconnaissance, shell commands, "
         "process discovery.", "A3"),
        ("Retrieve evidence for HTTP request flooding, port probing, "
         "high request volume.", "A1"),
    ]
    for q, fam in probes:
        print(f"\n=== {fam}: {q[:60]}... ===")
        for mode in ("dense_only", "bm25_only", "rrf",
                     "rrf_plus_metadata_rerank"):
            print(f"\n  mode={mode}")
            for row in retrieve(q, top_k=3, mode=mode, expected_family=fam):
                print(f"    rank={row['rank']} family={row['retrieved_family']} "
                      f"score={row['similarity_score_readable']:.4f} "
                      f"chunk={row['chunk_id']}")
