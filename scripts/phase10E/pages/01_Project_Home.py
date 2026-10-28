"""Phase 10E v2 — Page 01: Project Home (Refined Version)"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

import _theme as theme
import _data as data


# =========================
# PAGE HEADER
# =========================
theme.page_header(
    title="Cloud-Native IDS — Research Dashboard",
    subtitle="Evidence-based intrusion detection using ML, RAG, and local LLM reasoning",
    emoji="🛡️",
)


# =========================
# PROJECT OVERVIEW
# =========================
st.markdown(
    """
This project implements a **research-grade, offline cloud-native Intrusion Detection System (IDS)**.

The system integrates:

- **Classical Machine Learning** for detection  
- **Retrieval-Augmented Generation (RAG)** for evidence retrieval  
- **Local Large Language Model (LLM)** for reasoning and explanation  

All experiments are conducted in a **controlled Azure VM environment** using a **single-node K3s cluster**.

---

### 🔬 Experimental Pipeline

Telemetry is collected from:

- Envoy (service mesh)
- Falco (runtime security)
- Prometheus (metrics)

These signals are transformed into a **leakage-safe, run-level dataset**, classified using traditional ML models, and then **interpreted through a RAG-based reasoning pipeline**.

The LLM (Mistral, local via Ollama) produces explanations grounded in **retrieved evidence from the system’s own corpus**, ensuring traceability and reproducibility.
"""
)

st.divider()


# =========================
# HEADLINE RESULT
# =========================
theme.section("🚀 Headline Result — Phase 10U Upgraded Retriever (Realistic Deployment)")

deploy = data.get_realistic_deployment_kpi()
base = data.get_baseline_kpi()

if deploy and base:
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        theme.kpi_card(
            "MRR (Rank-1 Accuracy)",
            f"{deploy['MRR']:.3f}",
            delta=f"{deploy['MRR'] - base['MRR']:+.3f} vs baseline",
            help_text=(
                "Mean Reciprocal Rank under realistic deployment conditions. "
                "Measures how often the correct evidence is ranked first. "
                "1.000 means perfect rank-1 retrieval."
            ),
        )

    with c2:
        theme.kpi_card(
            "Precision@5",
            f"{deploy['precision_at_5']:.3f}",
            delta=f"{deploy['precision_at_5'] - base['precision_at_5']:+.3f} vs baseline",
            help_text=(
                "Proportion of relevant evidence within the top-5 retrieved chunks. "
                "Higher values indicate better retrieval quality."
            ),
        )

    with c3:
        theme.kpi_card(
            "Cross-Class Contamination@5",
            f"{deploy['cross_class_contamination_at_5']:.3f}",
            delta=f"{deploy['cross_class_contamination_at_5'] - base['cross_class_contamination_at_5']:+.3f} vs baseline",
            help_text=(
                "Measures how often retrieved evidence comes from the wrong attack family. "
                "Lower values indicate better class purity — a key supervisor concern."
            ),
        )

    with c4:
        theme.kpi_card(
            "F1@5",
            f"{deploy['f1_at_5']:.3f}",
            delta=f"{deploy['f1_at_5'] - base['f1_at_5']:+.3f} vs baseline",
            help_text="Balanced measure combining Precision@5 and Recall@5.",
        )

st.divider()


# =========================
# BEFORE VS AFTER
# =========================
theme.section("🔍 Phase 10R vs Phase 10U — What Changed")

col_l, col_r = st.columns(2)

with col_l:
    st.markdown("### Phase 10R — Baseline Retriever")
    st.markdown(
        """
- Dense semantic retrieval (MiniLM embeddings)  
- Boilerplate-heavy case corpus (Phase 10A)  
- Weak inter-family differentiation (only ~4 lines difference)  
- No lexical signal (BM25)  
- No metadata awareness  
- No reranking mechanism  
"""
    )

with col_r:
    st.markdown("### Phase 10U — Upgraded Retriever")
    st.markdown(
        """
- Enriched corpus with **run-level telemetry context (Phase 7)**  
- Explicit **attack-family evidence vocabulary**  
- Hybrid retrieval:
  - Dense (semantic)  
  - BM25 (lexical)  
- Reciprocal Rank Fusion (RRF)  
- Metadata-aware reranking using ML predictions  
"""
    )

st.divider()


# =========================
# DEMO GUIDANCE
# =========================
theme.section("🎯 How to Navigate This Dashboard")

theme.info_box(
    "Recommended Demo Flow",
    """
1. **Page 04 — Retrieval Evaluation** (core contribution)  
2. **Pages 02–03 — Environment & Dataset**  
3. **Page 05 — LLM Reasoning (impact of retrieval)**  
4. **Page 07 — Methodology (for technical discussion)**  

This order aligns with how the system was designed and validated.
""",
)

st.divider()


# =========================
# ARCHITECTURE
# =========================
theme.section("⚙️ System Architecture")

st.markdown(
    """
Cloud-native telemetry
        ↓
Dataset engineering (Phase 7)
        ↓
Classical ML detection (binary + multiclass)
        ↓
Predicted attack family
        ↓
RAG corpus (Phase 10U enriched)
        ↓
Hybrid retriever (Dense + BM25 + RRF + Metadata)
        ↓
Top-k evidence
        ↓
Local LLM reasoning (Mistral)
        ↓
Structured JSON + Analyst report + Dashboard
"""
)
