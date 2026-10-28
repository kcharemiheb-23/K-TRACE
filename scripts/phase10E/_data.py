"""
Phase 10E v2 - Centralized data loaders.

Every page imports from this module rather than hardcoding paths. Streamlit's
@st.cache_data decorator ensures that file reads happen at most once per
session per file.
"""
from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import streamlit as st

ROOT = Path.home() / "cloud-native-ids-azure"


def _read_csv_or_empty(p: Path) -> pd.DataFrame:
    if p.exists():
        return pd.read_csv(p)
    return pd.DataFrame()


def _read_text_or_empty(p: Path) -> str:
    if p.exists():
        return p.read_text(encoding="utf-8")
    return ""


# ---------- Phase 10U Part D artifacts (the headline evaluation) ----------

@st.cache_data
def load_headline_comparison() -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT / "artifacts/phase10U/output/comparison_headline.csv"
    )


@st.cache_data
def load_ablation_study() -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT / "artifacts/phase10U/output/ablation_study.csv"
    )


@st.cache_data
def load_per_family() -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT / "artifacts/phase10U/output/comparison_per_family.csv"
    )


@st.cache_data
def load_per_query_deltas() -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT / "artifacts/phase10U/output/comparison_per_query_deltas.csv"
    )


@st.cache_data
def load_grounding_quality() -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT / "artifacts/phase10U/output/grounding_quality.csv"
    )


@st.cache_data
def load_realistic_deployment_summary() -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT
        / "artifacts/phase10U/output/scoring_realistic_deployment/retrieval_metrics_summary.csv"
    )


@st.cache_data
def load_realistic_deployment_per_query() -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT
        / "artifacts/phase10U/output/scoring_realistic_deployment/retrieval_metrics_by_query.csv"
    )


@st.cache_data
def load_mode_per_query(mode: str) -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT
        / f"artifacts/phase10U/output/scoring_{mode}/retrieval_metrics_by_query.csv"
    )


@st.cache_data
def load_mode_ranked_results(mode: str) -> pd.DataFrame:
    if mode == "baseline":
        return _read_csv_or_empty(
            ROOT / "artifacts/phase10R/output/retrieval_ranked_results.csv"
        )
    return _read_csv_or_empty(
        ROOT / f"artifacts/phase10U/output/retrieval_ranked_results_v2_{mode}.csv"
    )


# ---------- Phase 10R baseline (kept for reference) ----------

@st.cache_data
def load_phase10r_summary() -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT / "artifacts/phase10R/output/retrieval_metrics_summary.csv"
    )


# ---------- Phase 10A corpus + queries + ground truth ----------

@st.cache_data
def load_queries() -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT / "artifacts/phase10R/benchmark/retriever_queries.csv"
    )


@st.cache_data
def load_ground_truth() -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT / "artifacts/phase10R/scoring/retriever_ground_truth.csv"
    )


# ---------- Phase 7 dataset ----------

@st.cache_data
def load_run_ledger() -> pd.DataFrame:
    return _read_csv_or_empty(
        ROOT / "artifacts/phase7/output/run-ledger.csv"
    )


# ---------- Phase 10D LLM reasoning outputs ----------

@st.cache_data
def list_phase10d_runs() -> list[str]:
    d = ROOT / "artifacts/phase10D/results"
    if not d.exists():
        return []
    return sorted([p.stem for p in d.glob("*.json")])


@st.cache_data
def load_phase10d_result(run_id: str) -> dict:
    p = ROOT / f"artifacts/phase10D/results/{run_id}.json"
    if not p.exists():
        return {}
    try:
        return json.loads(p.read_text())
    except Exception:
        return {}


@st.cache_data
def load_phase10d_report(run_id: str) -> str:
    return _read_text_or_empty(
        ROOT / f"artifacts/phase10D/reports/{run_id}.md"
    )


# ---------- Reports and policy documents ----------

@st.cache_data
def load_retriever_approach() -> str:
    return _read_text_or_empty(
        ROOT / "artifacts/phase10R/reports/retriever_approach.md"
    )


@st.cache_data
def load_ground_truth_policy() -> str:
    return _read_text_or_empty(
        ROOT / "artifacts/phase10R/reports/ground_truth_policy.md"
    )


@st.cache_data
def load_upgraded_retriever_design() -> str:
    return _read_text_or_empty(
        ROOT / "artifacts/phase10U/reports/upgraded_retriever_design.md"
    )


@st.cache_data
def load_phase10u_evaluation_report() -> str:
    return _read_text_or_empty(
        ROOT / "artifacts/phase10U/reports/phase10U_evaluation_report.md"
    )


@st.cache_data
def load_demo_walkthrough() -> str:
    return _read_text_or_empty(
        ROOT / "artifacts/phase10U/reports/demo_walkthrough.md"
    )


# ---------- Phase 9 v2 ML assets ----------

@st.cache_data
def list_phase9v2_pngs() -> list[Path]:
    d = ROOT / "artifacts/phase9_v2/png_export"
    if not d.exists():
        return []
    return sorted(d.glob("*.png"))


@st.cache_data
def load_phase9v2_supervisor_summary() -> str:
    return _read_text_or_empty(
        ROOT / "artifacts/phase9_v2/reports/phase9_supervisor_summary.md"
    )


# ---------- Headline KPI helpers used by the home page ----------

def get_realistic_deployment_kpi() -> dict:
    """Pull the most important deployment numbers for the home page."""
    df = load_realistic_deployment_summary()
    if df.empty:
        return {}
    row = df[df["group"] == "ALL"]
    if row.empty:
        return {}
    r = row.iloc[0]
    return {
        "MRR": float(r.get("MRR", 0)),
        "precision_at_5": float(r.get("precision_at_5", 0)),
        "recall_at_5": float(r.get("recall_at_5", 0)),
        "f1_at_5": float(r.get("f1_at_5", 0)),
        "cross_class_contamination_at_5": float(r.get("cross_class_contamination_at_5", 0)),
    }


def get_baseline_kpi() -> dict:
    df = load_phase10r_summary()
    if df.empty:
        return {}
    row = df[df["group"] == "ALL"]
    if row.empty:
        return {}
    r = row.iloc[0]
    return {
        "MRR": float(r.get("MRR", 0)),
        "precision_at_5": float(r.get("precision_at_5", 0)),
        "recall_at_5": float(r.get("recall_at_5", 0)),
        "f1_at_5": float(r.get("f1_at_5", 0)),
        "cross_class_contamination_at_5": float(r.get("cross_class_contamination_at_5", 0)),
    }
