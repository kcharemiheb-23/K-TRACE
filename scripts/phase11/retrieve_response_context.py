#!/usr/bin/env python3
"""Phase 11 - Retrieve evidence context for an incident.

Thin wrapper over scripts/phase10U/06_upgraded_retriever.py:retrieve.
Always uses mode='rrf_plus_metadata_rerank' with the predicted family.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"
RETRIEVER_PATH = ROOT / "scripts/phase10U/06_upgraded_retriever.py"

_spec = importlib.util.spec_from_file_location("upgraded_retriever", RETRIEVER_PATH)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)

def retrieve_for_incident(run_id: str, predicted_family: str, top_k: int = 5) -> dict:
    query_text = (
        f"Retrieve evidence explaining IDS case {run_id} and its "
        f"security-relevant telemetry behavior."
    )
    rows = _mod.retrieve(
        query_text=query_text,
        top_k=top_k,
        mode="rrf_plus_metadata_rerank",
        expected_family=predicted_family,
    )
    chunks = [
        {
            "rank": r["rank"],
            "chunk_id": r["chunk_id"],
            "doc_name": r["doc_name"],
            "section": r["section"],
            "family": r.get("retrieved_family", "UNKNOWN"),
            "score": float(r.get("similarity_score_readable", 0.0)),
            "text_preview": r.get("text_preview", ""),
        }
        for r in rows
    ]
    return {
        "mode": "rrf_plus_metadata_rerank",
        "top_k": top_k,
        "query_text": query_text,
        "predicted_family_used": predicted_family,
        "chunks": chunks,
    }

if __name__ == "__main__":
    import sys
    rid = sys.argv[1] if len(sys.argv) > 1 else "A3_LOW_002"
    fam = sys.argv[2] if len(sys.argv) > 2 else "A3"
    print(json.dumps(retrieve_for_incident(rid, fam, 5), indent=2)[:1200])
