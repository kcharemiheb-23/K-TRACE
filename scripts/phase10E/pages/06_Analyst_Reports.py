"""Phase 10E v2 - Page 06: Analyst report viewer."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

import _theme as theme
import _data as data

ROOT = Path.home() / "cloud-native-ids-azure"

theme.page_header(
    title="Analyst Reports",
    subtitle="Markdown reports as they would be delivered to a SOC team",
    emoji="📄",
)

reports_dir = ROOT / "artifacts/phase10D/reports"
md_files = sorted(reports_dir.glob("*.md")) if reports_dir.exists() else []

if not md_files:
    st.warning("No Phase 10D markdown reports found.")
else:
    # Highlight the supervisor summary first if it exists.
    summary_files = [p for p in md_files if "summary" in p.stem.lower()]
    case_files = [p for p in md_files if "summary" not in p.stem.lower()]

    if summary_files:
        theme.section("Phase 10D summary documents")
        choice = st.selectbox(
            "Choose a summary",
            [p.stem for p in summary_files],
            key="summary_choice",
        )
        chosen = next(p for p in summary_files if p.stem == choice)
        with st.expander(f"Read: {chosen.name}", expanded=True):
            st.markdown(chosen.read_text(encoding="utf-8"))

    if case_files:
        theme.section("Per-case analyst reports")
        choice = st.selectbox(
            "Choose a case report",
            [p.stem for p in case_files],
            key="case_choice",
        )
        chosen = next(p for p in case_files if p.stem == choice)
        st.markdown(chosen.read_text(encoding="utf-8"))
