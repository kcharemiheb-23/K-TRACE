"""
Phase 10E v2 - Centralized visual theme for the dashboard.

Defines the family color palette, fonts, and small reusable display helpers.
All pages import from this module so the dashboard looks consistent.
"""
from __future__ import annotations

import streamlit as st

# Attack-family color palette. Used everywhere a family appears.
FAMILY_COLORS = {
    "A1": "#E63946",       # red: HTTP flood, traffic-volume danger
    "A2": "#F4A261",       # orange: invalid requests, warning
    "A3": "#7B2CBF",       # purple: runtime recon, privilege concern
    "A4": "#9D0208",       # dark red: exploit payloads, critical
    "BENIGN": "#2A9D8F",   # green: normal activity
    "UNKNOWN": "#808080",  # gray: methodology, glossary
}

MODE_COLORS = {
    "baseline": "#6C757D",
    "dense_only": "#0096C7",
    "bm25_only": "#FFB703",
    "rrf": "#3A86FF",
    "rrf_plus_metadata_rerank": "#06A77D",
    "realistic_deployment": "#118AB2",
}

MODE_LABELS = {
    "baseline": "Phase 10R baseline",
    "dense_only": "+ corpus enrichment (dense)",
    "bm25_only": "BM25-only on enriched corpus",
    "rrf": "+ hybrid RRF",
    "rrf_plus_metadata_rerank": "+ metadata-aware rerank (final)",
    "realistic_deployment": "Realistic deployment (ML preds)",
}

FAMILY_HUMAN_NAMES = {
    "A1": "A1 — HTTP port flood",
    "A2": "A2 — Invalid request spray",
    "A3": "A3 — Runtime reconnaissance",
    "A4": "A4 — Exploit-like payloads",
    "BENIGN": "BENIGN — normal activity",
    "UNKNOWN": "UNKNOWN — non-case docs",
}


def page_header(title: str, subtitle: str = "", emoji: str = ""):
    """Render a consistent page header."""
    if emoji:
        st.title(f"{emoji} {title}")
    else:
        st.title(title)
    if subtitle:
        st.caption(subtitle)
    st.divider()


def kpi_card(label: str, value: str, help_text: str | None = None,
             delta: str | None = None):
    """Wrapper over st.metric with consistent help-text styling."""
    st.metric(label=label, value=value, delta=delta, help=help_text)


def info_box(title: str, body: str):
    """Consistent info box for interpretation paragraphs."""
    with st.container(border=True):
        st.markdown(f"**{title}**")
        st.markdown(body)


def warning_box(body: str):
    st.warning(body)


def family_badge(family: str) -> str:
    """Return a small inline HTML badge for a family label."""
    color = FAMILY_COLORS.get(family, "#808080")
    return (
        f"<span style='background-color:{color};color:white;padding:2px 8px;"
        f"border-radius:10px;font-weight:600;font-size:0.85em'>{family}</span>"
    )


def section(title: str):
    """Render a consistent section header within a page."""
    st.markdown(f"### {title}")
