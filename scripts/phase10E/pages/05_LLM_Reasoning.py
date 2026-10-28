"""Phase 10E v2 - Page 05: LLM reasoning outputs with retrieval grounding."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

import _theme as theme
import _data as data

theme.page_header(
    title="LLM Reasoning",
    subtitle="Phase 10D integrated reasoning outputs grounded in retrieved evidence",
    emoji="🧠",
)

st.markdown(
    """
This page shows how the local Mistral LLM reasons about specific IDS cases
using retrieved evidence as context. Each case combines:
- the run's metadata (family, intensity, ML prediction),
- top-k retrieved chunks (the evidence),
- the LLM's structured reasoning (JSON + markdown).
"""
)

runs = data.list_phase10d_runs()
if not runs:
    st.warning("No Phase 10D results found at artifacts/phase10D/results/")
else:
    selected = st.selectbox("Select a case to inspect", runs, index=0)

    result = data.load_phase10d_result(selected)
    report = data.load_phase10d_report(selected)

    c1, c2 = st.columns([1, 2])
    with c1:
        theme.section("Case identity")
        meta_keys = ["run_id", "class_label", "binary_label", "subtype",
                     "intensity", "best_binary_model", "best_multiclass_model",
                     "binary_pred_label", "multiclass_pred_label"]
        for k in meta_keys:
            v = result.get(k)
            if v is not None:
                st.markdown(f"**{k}:** `{v}`")

    with c2:
        theme.section("LLM reasoning")
        llm_text = (
            result.get("llm_reasoning")
            or result.get("reasoning")
            or result.get("answer")
            or result.get("output")
            or ""
        )
        if llm_text:
            st.markdown(llm_text)
        elif report:
            st.markdown(report)
        else:
            st.code(json.dumps(result, indent=2)[:2000], language="json")

    st.divider()
    theme.section("Retrieved evidence (sources)")
    sources = result.get("sources") or result.get("retrieved_chunks") or []
    if sources:
        for i, s in enumerate(sources, start=1):
            with st.container(border=True):
                st.markdown(
                    f"**rank {i}**  &nbsp; "
                    f"chunk_id: `{s.get('chunk_id', '?')}`  &nbsp; "
                    f"doc: `{s.get('doc_name', '?')}`"
                )
                preview = s.get("text") or s.get("text_preview") or ""
                if preview:
                    st.caption(preview[:400])
    else:
        st.info("Source chunks were not preserved in this case's JSON.")

    st.divider()
    theme.section("Full analyst report")
    if report:
        with st.expander("Read full markdown report", expanded=False):
            st.markdown(report)
