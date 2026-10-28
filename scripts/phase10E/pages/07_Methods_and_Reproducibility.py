"""Phase 10E v2 - Page 07: Methods and reproducibility."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

import _theme as theme
import _data as data

theme.page_header(
    title="Methods and Reproducibility",
    subtitle="Formal retriever design, evaluation methodology, and exact commands",
    emoji="🔬",
)

theme.section("Phase 10U upgraded retriever — formal design")
st.markdown(data.load_upgraded_retriever_design())

st.divider()
theme.section("Demo walkthrough — three queries across all four modes")
st.markdown(data.load_demo_walkthrough())

st.divider()
theme.section("Reproducibility commands")

st.markdown(
    """
The full evaluation can be reproduced from a clean checkout with the following
commands (executed from `~/cloud-native-ids-azure` with the project venv
active).
"""
)

st.code(
    """\
# Phase 10U Part A — corpus enrichment
python scripts/phase10U/01_enrich_case_corpus.py

# Phase 10U Part B — chunker, embedder, BM25
python scripts/phase10U/02_chunk_corpus_v2.py
python scripts/phase10U/03_embed_and_index_v2.py
python scripts/phase10U/04_build_bm25_index.py
python scripts/phase10U/05_write_vectorstore_v2_report.py

# Phase 10U Part C — upgraded retriever module + four-mode inspection
python scripts/phase10U/07_run_retriever_inspection_v2.py
python scripts/phase10U/08_demo_query_walkthrough.py
python scripts/phase10U/09_write_retriever_design_doc.py

# Phase 10U Part D — research-level evaluation
python scripts/phase10U/10_score_all_modes.py
python scripts/phase10U/11_compute_headline_comparison.py
python scripts/phase10U/12_compute_per_family_comparison.py
python scripts/phase10U/13_compute_per_query_deltas.py
python scripts/phase10U/14_ablation_study.py
python scripts/phase10U/15_realistic_deployment_eval.py
python scripts/phase10U/16_grounding_quality.py
python scripts/phase10U/17_write_phase10u_evaluation_report.py

# Launch this dashboard
streamlit run ~/cloud-native-ids-azure/scripts/phase10E/dashboard_app.py \\
    --server.address 0.0.0.0 --server.port 8501
""",
    language="bash",
)

st.divider()
theme.section("Remote access via SSH tunnel")

st.code(
    """ssh -i intrusion-detection_key.pem -L 8501:localhost:8501 azureuser@72.146.217.8

# then open in your local browser:
# http://localhost:8501
""",
    language="bash",
)

st.divider()
theme.section("Phase 10R baseline (preserved for comparison)")
with st.expander("Phase 10R retriever approach", expanded=False):
    st.markdown(data.load_retriever_approach())
with st.expander("Phase 10R ground-truth policy", expanded=False):
    st.markdown(data.load_ground_truth_policy())
