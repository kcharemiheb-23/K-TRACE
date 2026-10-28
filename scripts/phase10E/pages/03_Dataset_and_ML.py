"""Phase 10E v2 - Page 03: Dataset distribution and ML model results."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import streamlit as st

import _theme as theme
import _data as data

theme.page_header(
    title="Dataset and ML Validation",
    subtitle="Phase 7 controlled collection and Phase 9 v2 model results",
    emoji="📊",
)

theme.section("Phase 7 controlled-collection distribution")

ledger = data.load_run_ledger()
if ledger.empty:
    st.error("Run ledger not found at artifacts/phase7/output/run-ledger.csv")
else:
    counts = ledger["class_label"].value_counts().reindex(
        ["A1_HTTP_PORTFLOOD", "A2_INVALID_REQUEST_SPRAY",
         "A3_RUNTIME_RECON", "A4_EXPLOIT_LIKE_PAYLOADS", "BENIGN"]
    ).fillna(0).astype(int)
    counts.index.name = "class_label"
    counts.name = "runs"

    c1, c2 = st.columns([2, 1])
    with c1:
        # Use plotly bar with family colors.
        try:
            import plotly.express as px
            df = counts.reset_index()
            df["family"] = df["class_label"].apply(
                lambda x: x.split("_")[0] if x.startswith("A") else "BENIGN"
            )
            df["color"] = df["family"].map(theme.FAMILY_COLORS)
            fig = px.bar(
                df, x="class_label", y="runs",
                color="family",
                color_discrete_map=theme.FAMILY_COLORS,
                text="runs",
            )
            fig.update_layout(
                showlegend=False, height=380,
                xaxis_title="", yaxis_title="run count",
            )
            st.plotly_chart(fig, use_container_width=True)
        except ImportError:
            st.bar_chart(counts)
    with c2:
        st.dataframe(counts.to_frame(), use_container_width=True)

    theme.info_box(
        "Class imbalance note",
        "BENIGN dominates because controlled benign runs are needed to "
        "validate false-positive behavior across multiple normal load "
        "patterns. A3 has more runs because runtime reconnaissance was "
        "studied at finer intensity granularity. The retriever evaluation "
        "in Page 04 controls for this imbalance through per-family "
        "decomposition.",
    )

st.divider()
theme.section("Phase 9 v2 ML model results")

ml_summary = data.load_phase9v2_supervisor_summary()
if ml_summary:
    with st.expander("Read Phase 9 v2 supervisor summary", expanded=False):
        st.markdown(ml_summary)

st.markdown("**Selected model performance plots**")

pngs = data.list_phase9v2_pngs()
if pngs:
    headline_keywords = [
        "binary_confusion_matrix_DecisionTree",
        "multiclass_confusion_matrix_RandomForest",
        "binary_model_comparison_f1",
        "binary_model_comparison_roc_auc",
        "multiclass_per_class_f1_RandomForest",
        "multiclass_source_importance_RandomForest",
    ]
    headlines = [
        p for p in pngs
        if any(k in p.name for k in headline_keywords)
    ]
    if headlines:
        cols = st.columns(2)
        for i, p in enumerate(headlines[:6]):
            with cols[i % 2]:
                st.image(str(p), caption=p.stem, use_container_width=True)

    with st.expander("Browse all Phase 9 v2 plots", expanded=False):
        for p in pngs:
            st.image(str(p), caption=p.stem, use_container_width=True)
else:
    st.info("No Phase 9 v2 PNGs found.")

theme.info_box(
    "Accepted best models",
    "**Binary task (ATTACK vs BENIGN):** DecisionTree — chosen for "
    "interpretability and strong separation. \n\n"
    "**Multiclass task (BENIGN + A1..A4):** RandomForest — chosen for "
    "robustness on noisy attack-family classification. The multiclass "
    "predictions feed the metadata-aware reranker in Phase 10U.",
)
