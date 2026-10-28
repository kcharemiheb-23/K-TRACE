"""
Phase 10E v2 - Cloud-Native IDS RAG Reasoning Dashboard.

Entry point. Streamlit auto-discovers pages in the pages/ directory.
This module configures the global page-set behavior and renders a sidebar
welcome screen when invoked directly.
"""
from __future__ import annotations

from pathlib import Path
import sys

# Make the local _theme and _data modules importable from pages/.
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st

import _theme as theme
import _data as data

st.set_page_config(
    page_title="Cloud-Native IDS RAG Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Force the home page if user lands at the entry point.
st.sidebar.title("🛡️ Cloud-Native IDS")
st.sidebar.markdown("Research dashboard")
st.sidebar.divider()
st.sidebar.markdown(
    "**Navigate using the page list above this sidebar block.** "
    "The recommended reading order is the page numbering."
)
st.sidebar.divider()

# Quick stats in the sidebar so they are visible from any page.
deploy = data.get_realistic_deployment_kpi()
if deploy:
    st.sidebar.markdown("**Deployment KPI snapshot**")
    st.sidebar.metric("MRR (deployment)", f"{deploy['MRR']:.3f}")
    st.sidebar.metric("Precision@5 (deployment)", f"{deploy['precision_at_5']:.3f}")
    st.sidebar.metric(
        "Cross-class contamination@5",
        f"{deploy['cross_class_contamination_at_5']:.3f}",
    )

# When the user opens dashboard_app.py directly, redirect them to the home page
# by rendering a clear pointer.
st.title("🛡️ Cloud-Native IDS — RAG Reasoning Research Dashboard")
st.markdown(
    "This dashboard presents the experimental results of the cloud-native "
    "Intrusion Detection System enhanced with classical ML, RAG retrieval, "
    "and local LLM reasoning. **Open the page list (top-left) and start with "
    "page 01.**"
)
st.info(
    "Recommended reading order:\n\n"
    "1. **Project Home** — what this project is and the headline result\n"
    "2. **Cloud-Native Environment** — Kubernetes layout and telemetry sources\n"
    "3. **Dataset & ML** — Phase 7 collection and Phase 9 v2 model results\n"
    "4. **Retrieval Evaluation** — the core supervisor-facing analysis\n"
    "5. **LLM Reasoning** — example reasoning outputs grounded in retrieval\n"
    "6. **Analyst Reports** — markdown reports as delivered to a SOC team\n"
    "7. **Methods & Reproducibility** — exact retrieval design and commands"
)
