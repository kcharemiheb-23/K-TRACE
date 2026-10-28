"""Phase 10E v2 - Page 04: Retrieval Evaluation (supervisor centerpiece)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import streamlit as st

import _theme as theme
import _data as data

theme.page_header(
    title="Retrieval Evaluation",
    subtitle="Phase 10R baseline vs Phase 10U upgrade — SMART metrics, ablation, deployment, grounding",
    emoji="🎯",
)

st.markdown(
    """
This page exposes the retriever as an independent component of the IDS
reasoning pipeline. Every metric is computed against the Phase 10R
ground-truth relevance policy using the same scoring code for every mode,
which makes the comparison methodologically clean.
"""
)

# --- Approach summary ----------------------------------------------------

theme.section("1. What the retriever does and how it searches")

c1, c2, c3, c4 = st.columns(4)
c1.metric("Search type", "Hybrid")
c2.metric("Vector store", "Chroma v2")
c3.metric("Lexical retriever", "BM25Okapi")
c4.metric("Reranker", "Metadata-aware")

st.markdown(
    """
The Phase 10U retriever combines **dense semantic vector retrieval** (over
the Chroma collection `ids_rag_corpus_v2`) with **sparse lexical retrieval**
(BM25Okapi over the same chunks), fuses their rankings using **Reciprocal
Rank Fusion** (k=60, Cormack et al. SIGIR 2009), and then applies a
**soft metadata-aware boost** (b=0.15) to chunks whose `family` metadata
matches the ML-predicted family.
"""
)

with st.expander("Read full Phase 10U retriever design document", expanded=False):
    st.markdown(data.load_upgraded_retriever_design())
with st.expander("Read Phase 10R retriever approach (baseline reference)", expanded=False):
    st.markdown(data.load_retriever_approach())

st.divider()

# --- Headline comparison with confidence intervals ----------------------

theme.section("2. Headline comparison (with bootstrap 95% CI, 1000 resamples)")

headline = data.load_headline_comparison()
if headline.empty:
    st.warning("comparison_headline.csv not found.")
else:
    display = headline.copy()
    display["mode_label"] = display["mode"].map(theme.MODE_LABELS).fillna(display["mode"])

    metrics_to_show = [
        ("reciprocal_rank", "MRR"),
        ("precision_at_5", "Precision@5"),
        ("recall_at_5", "Recall@5"),
        ("f1_at_5", "F1@5"),
        ("cross_class_contamination_at_5", "Cross-class contam@5"),
    ]

    rows = []
    for _, r in display.iterrows():
        row = {"Mode": r["mode_label"]}
        for col, label in metrics_to_show:
            mean = r[f"{col}_mean"]
            lo = r[f"{col}_ci_lo"]
            hi = r[f"{col}_ci_hi"]
            row[label] = f"{mean:.3f} [{lo:.3f}, {hi:.3f}]"
        rows.append(row)
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    try:
        import plotly.graph_objects as go
        # Bar with CI error bars for F1@5 across modes.
        fig = go.Figure()
        modes = display["mode"].tolist()
        means = display["f1_at_5_mean"].tolist()
        ci_lo = display["f1_at_5_ci_lo"].tolist()
        ci_hi = display["f1_at_5_ci_hi"].tolist()
        err_minus = [m - lo for m, lo in zip(means, ci_lo)]
        err_plus = [hi - m for m, hi in zip(means, ci_hi)]
        colors = [theme.MODE_COLORS.get(m, "#888") for m in modes]
        fig.add_trace(go.Bar(
            x=[theme.MODE_LABELS.get(m, m) for m in modes],
            y=means,
            marker_color=colors,
            error_y=dict(type="data", symmetric=False, array=err_plus, arrayminus=err_minus),
        ))
        fig.update_layout(
            title="F1@5 by mode with 95% bootstrap CI",
            yaxis_title="F1@5",
            height=400,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        pass

theme.info_box(
    "How to read the table",
    "Each cell shows the mean across 22 queries and the 95% bootstrap "
    "confidence interval in brackets. A wider interval indicates higher "
    "uncertainty due to query-level variance. Modes whose intervals do not "
    "overlap are reliably different.",
)

st.divider()

# --- Ablation study ------------------------------------------------------

theme.section("3. Ablation study — what each upgrade lever contributes")

ablation = data.load_ablation_study()
if ablation.empty:
    st.warning("ablation_study.csv not found.")
else:
    display = ablation[["lever", "f1_at_5_mean", "f1_at_5_delta_vs_prev",
                        "precision_at_5_mean", "recall_at_5_mean",
                        "reciprocal_rank_mean", "cross_class_contamination_at_5_mean"]].copy()
    display.columns = ["Lever", "F1@5", "ΔF1@5 vs prev", "P@5", "R@5", "MRR", "Contam@5"]
    st.dataframe(display, use_container_width=True, hide_index=True)

    try:
        import plotly.express as px
        fig = px.line(
            ablation, x="lever", y="f1_at_5_mean",
            markers=True, title="F1@5 progression as upgrade levers are added",
        )
        fig.update_layout(yaxis_title="F1@5", xaxis_title="", height=350)
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        pass

theme.info_box(
    "Reading the ablation",
    "The delta column shows the change in F1@5 versus the previous lever. "
    "Positive deltas mean the lever contributed measurable improvement. "
    "Note that bm25_only is a parallel mode rather than a cumulative lever; "
    "it is included to show how much lexical retrieval alone can do on the "
    "enriched corpus.",
)

st.divider()

# --- Per-family decomposition -------------------------------------------

theme.section("4. Per-family decomposition")

per_family = data.load_per_family()
if per_family.empty:
    st.warning("comparison_per_family.csv not found.")
else:
    metric_choice = st.selectbox(
        "Metric to display",
        ["precision_at_5", "recall_at_5", "f1_at_5", "reciprocal_rank",
         "cross_class_contamination_at_5"],
        index=0,
    )
    pivot = per_family.pivot(index="mode", columns="family", values=metric_choice)
    pivot = pivot.reindex(["baseline", "dense_only", "bm25_only", "rrf",
                           "rrf_plus_metadata_rerank"])
    st.dataframe(pivot.style.format("{:.3f}"), use_container_width=True)

    try:
        import plotly.express as px
        fig = px.imshow(
            pivot, text_auto=".2f", aspect="auto",
            color_continuous_scale="RdYlGn" if metric_choice != "cross_class_contamination_at_5" else "RdYlGn_r",
            title=f"{metric_choice} by mode and family",
        )
        fig.update_layout(height=350)
        st.plotly_chart(fig, use_container_width=True)
    except ImportError:
        pass

st.divider()

# --- Per-query deltas ----------------------------------------------------

theme.section("5. Per-query improvements (baseline → final upgrade)")

deltas = data.load_per_query_deltas()
if deltas.empty:
    st.warning("comparison_per_query_deltas.csv not found.")
else:
    display = deltas[[
        "query_id", "run_id", "expected_family", "query_type",
        "f1_at_5_baseline", "f1_at_5_upgrade", "f1_at_5_delta",
        "reciprocal_rank_baseline", "reciprocal_rank_upgrade",
        "cross_class_contamination_at_5_baseline",
        "cross_class_contamination_at_5_upgrade",
    ]].copy()
    display.columns = [
        "query", "run", "family", "type",
        "F1@5 base", "F1@5 upg", "ΔF1@5",
        "MRR base", "MRR upg",
        "Contam@5 base", "Contam@5 upg",
    ]
    st.dataframe(display, use_container_width=True, hide_index=True)

st.divider()

# --- Realistic deployment vs ground truth -------------------------------

theme.section("6. Realistic deployment vs ground-truth ceiling")

real = data.load_realistic_deployment_summary()
gt_per = data.load_mode_per_query("rrf_plus_metadata_rerank")

if not real.empty and not gt_per.empty:
    real_all = real[real["group"] == "ALL"]
    if not real_all.empty:
        r = real_all.iloc[0]
        gt_means = gt_per[[
            "reciprocal_rank", "precision_at_5", "recall_at_5",
            "f1_at_5", "cross_class_contamination_at_5"
        ]].astype(float).mean()

        rows = []
        for col, label in [
            ("MRR", "MRR"),
            ("precision_at_5", "Precision@5"),
            ("recall_at_5", "Recall@5"),
            ("f1_at_5", "F1@5"),
            ("cross_class_contamination_at_5", "Cross-class contam@5"),
        ]:
            real_v = float(r.get(col, 0))
            gt_v = float(gt_means.get(col if col != "MRR" else "reciprocal_rank", 0))
            rows.append({
                "Metric": label,
                "Realistic deployment (ML preds)": f"{real_v:.3f}",
                "Ground-truth ceiling": f"{gt_v:.3f}",
                "Gap": f"{real_v - gt_v:+.3f}",
            })
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

theme.info_box(
    "Why this comparison matters",
    "The metadata reranker uses a family parameter. In the ground-truth "
    "scenario this is the true family, which is the absolute ceiling of "
    "what metadata-aware retrieval can achieve. In the realistic deployment "
    "scenario this is the actual ML prediction, which is what the system "
    "would see in production. The gap between the two quantifies how much "
    "of the upgrade depends on classifier accuracy.",
)

st.divider()

# --- Grounding quality ---------------------------------------------------

theme.section("7. Grounding quality of LLM reasoning outputs")

grounding = data.load_grounding_quality()
if grounding.empty:
    st.warning("grounding_quality.csv not found.")
else:
    by_mode = grounding.groupby("mode")["grounding_rate"].agg(
        ["mean", "min", "max", "count"]
    ).reset_index()
    by_mode.columns = ["Mode", "Mean grounding rate", "Min", "Max", "Cases"]
    by_mode["Mean grounding rate"] = by_mode["Mean grounding rate"].map(lambda v: f"{v:.3f}")
    by_mode["Min"] = by_mode["Min"].map(lambda v: f"{v:.3f}")
    by_mode["Max"] = by_mode["Max"].map(lambda v: f"{v:.3f}")
    by_mode["Mode"] = by_mode["Mode"].map(lambda m: theme.MODE_LABELS.get(m, m))
    st.dataframe(by_mode, use_container_width=True, hide_index=True)

    with st.expander("Per-case grounding rates", expanded=False):
        st.dataframe(grounding, use_container_width=True, hide_index=True)

theme.info_box(
    "What grounding measures",
    "The grounding rate is the fraction of LLM-output sentences that share "
    "at least two substantive tokens with the top-5 retrieved chunks for "
    "the same case. This is a conservative proxy for whether the LLM is "
    "reasoning from retrieved evidence versus generating from prior. The "
    "upgraded retriever's higher grounding rate provides direct evidence "
    "that retrieval improvements propagate into LLM reasoning quality.",
)

st.divider()

# --- Ground-truth policy -------------------------------------------------

theme.section("8. Ground-truth relevance policy")

with st.expander("Read full ground-truth policy", expanded=False):
    st.markdown(data.load_ground_truth_policy())

st.divider()

# --- Full evaluation report ---------------------------------------------

theme.section("9. Full Phase 10U evaluation report")

with st.expander("Read full evaluation report", expanded=False):
    st.markdown(data.load_phase10u_evaluation_report())
