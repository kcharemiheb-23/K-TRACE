"""Phase 10E v2 - Page 08: Integrated IDS Response (Phase 11)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.parent))
import _theme as theme  # noqa: E402

ROOT = Path.home() / "cloud-native-ids-azure"
ART = ROOT / "artifacts/phase11"
INCIDENTS = ART / "incidents"
REPORTS = ART / "reports"
ACTIONS = ART / "actions"
LOGS = ART / "logs"
SUMMARY_CSV = ART / "summary/phase11_run_summary.csv"

theme.page_header(
    title="Integrated IDS Response",
    subtitle="Phase 11 - end-to-end orchestrated response workflow",
    emoji="🛡️",
)

st.markdown(
    """
This page exposes the full lifecycle of every processed run. The ML
classifier acts as the attack gate: BENIGN runs are logged and skipped;
ATTACK runs are passed to the upgraded Phase 10U retriever, the Mistral
LLM (explanation only), the deterministic policy engine, and the
remediation executor. Action selection is **never** taken by the LLM.
"""
)

# --- Top metrics --------------------------------------------------------

theme.section("1. Lifecycle metrics")

if not SUMMARY_CSV.exists():
    st.info("No Phase 11 runs yet. Run `bash scripts/phase11/demo_run.sh` "
            "to populate this page.")
    st.stop()

summary = pd.read_csv(SUMMARY_CSV)
total = len(summary)
attacks = (summary["gate_decision"] == "PASS_TO_RAG").sum()
benigns = (summary["gate_decision"] == "SKIP_BENIGN").sum()
errors = (summary["gate_decision"] == "ERROR").sum() if "gate_decision" in summary else 0
applied = (summary.get("applied", pd.Series([False]*total)).astype(str).str.lower() == "true").sum()
dryruns = ((summary["mode"] == "dry_run") & (summary["gate_decision"] == "PASS_TO_RAG")).sum()

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Runs processed", total)
c2.metric("Attack incidents", attacks)
c3.metric("Benign skipped", benigns)
c4.metric("Dry-run actions", dryruns)
c5.metric("Applied actions", applied)

st.divider()

# --- Filters ------------------------------------------------------------

theme.section("2. Incidents")

incidents_only = summary[summary["gate_decision"] == "PASS_TO_RAG"].copy()

if incidents_only.empty:
    st.info("No attack incidents recorded yet.")
else:
    families = ["(all)"] + sorted(incidents_only["family"].dropna().unique().tolist())
    severities = ["(all)"] + sorted(incidents_only["severity"].dropna().unique().tolist())
    modes = ["(all)"] + sorted(incidents_only["mode"].dropna().unique().tolist())

    f1, f2, f3, f4 = st.columns(4)
    fam = f1.selectbox("Family", families, index=0)
    sev = f2.selectbox("Severity", severities, index=0)
    mod = f3.selectbox("Action mode", modes, index=0)
    rid = f4.text_input("Run ID contains", "")

    df = incidents_only.copy()
    if fam != "(all)": df = df[df["family"] == fam]
    if sev != "(all)": df = df[df["severity"] == sev]
    if mod != "(all)": df = df[df["mode"] == mod]
    if rid: df = df[df["run_id"].astype(str).str.contains(rid, case=False, na=False)]

    show = df[["timestamp_utc","run_id","family","severity","action_id","mode",
               "applied","incident_id"]].rename(columns={
        "timestamp_utc":"time","incident_id":"incident",
    })
    st.dataframe(show, use_container_width=True, hide_index=True)

    # --- Incident details ----------------------------------------------
    st.divider()
    theme.section("3. Incident detail")

    incident_choices = df["incident_id"].tolist()
    if incident_choices:
        chosen = st.selectbox("Select an incident to inspect", incident_choices)
        json_path = INCIDENTS / f"{chosen}.json"
        md_path = REPORTS / f"{chosen}.md"

        if json_path.exists():
            inc = json.loads(json_path.read_text())

            colA, colB = st.columns([1, 2])
            with colA:
                st.markdown("**ML breakdown**")
                ml = inc.get("ml", {})
                st.write({
                    "binary": ml.get("binary_pred"),
                    "multiclass": ml.get("multiclass_pred"),
                    "family": ml.get("family"),
                    "gate": ml.get("gate_decision"),
                })
                st.markdown("**Policy decision**")
                pol = inc.get("policy", {})
                st.write({
                    "severity": pol.get("severity"),
                    "action": pol.get("action_id"),
                    "matched_rule": pol.get("matched_rule"),
                    "rationale": pol.get("rationale"),
                })

            with colB:
                st.markdown("**Top retrieved evidence**")
                ret = inc.get("retrieval", {})
                rows = []
                for c in ret.get("chunks", [])[:5]:
                    rows.append({
                        "rank": c.get("rank"),
                        "doc": c.get("doc_name"),
                        "family": c.get("family"),
                        "section": c.get("section"),
                        "score": round(c.get("score", 0), 4),
                    })
                if rows:
                    st.dataframe(pd.DataFrame(rows), hide_index=True, use_container_width=True)
                else:
                    st.write("(no chunks)")

            st.markdown("**LLM analyst reasoning**")
            llm = inc.get("llm", {})
            if not llm.get("ok", False):
                st.warning(f"LLM unavailable: {llm.get('error', 'unknown error')}")
            for label, key in [("Explanation","explanation_md"),
                               ("Impact","impact_md"),
                               ("Recommendation","recommendation_md")]:
                v = (llm.get(key) or "").strip()
                if v:
                    st.markdown(f"**{label}**")
                    st.markdown(v)

            st.markdown("**Remediation**")
            rem = inc.get("remediation", {})
            st.write({
                "mode": rem.get("mode"),
                "applied": rem.get("applied"),
                "kubectl_command": rem.get("kubectl_command"),
                "manifest_path": rem.get("manifest_path"),
                "rollback_path": rem.get("rollback_path"),
            })
            if rem.get("manifest_path") and Path(rem["manifest_path"]).exists():
                with st.expander("Generated NetworkPolicy manifest", expanded=False):
                    st.code(Path(rem["manifest_path"]).read_text(), language="yaml")
            if rem.get("rollback_path") and Path(rem["rollback_path"]).exists():
                with st.expander("Rollback script", expanded=False):
                    st.code(Path(rem["rollback_path"]).read_text(), language="bash")
            if rem.get("kubectl_stdout"):
                with st.expander("kubectl stdout", expanded=False):
                    st.code(rem["kubectl_stdout"])
            if rem.get("kubectl_stderr"):
                with st.expander("kubectl stderr", expanded=False):
                    st.code(rem["kubectl_stderr"])

            st.markdown("**Replay command** (reproducibility):")
            st.code(
                f"python3 scripts/phase11/run_response_pipeline.py "
                f"--run_id {inc.get('run_id','')} --mode {rem.get('mode','dry_run')}",
                language="bash",
            )

            with st.expander("Full markdown analyst report", expanded=False):
                if md_path.exists():
                    st.markdown(md_path.read_text())
                else:
                    st.write("(markdown report missing)")

            with st.expander("Raw incident JSON (debug)", expanded=False):
                st.json(inc)
        else:
            st.warning(f"Incident JSON not found: {json_path}")

# --- Skipped benign panel ----------------------------------------------
st.divider()
theme.section("4. Benign runs skipped by ML gate")

skipped_files = sorted(LOGS.glob("skipped_benign_*.csv"))
if not skipped_files:
    st.info("No benign-skip log present.")
else:
    parts = [pd.read_csv(p) for p in skipped_files]
    skip_df = pd.concat(parts, ignore_index=True)
    st.dataframe(skip_df, use_container_width=True, hide_index=True)
    st.caption("These runs never reached the RAG retriever or the LLM. "
               "This panel is the proof that the attack gate works.")

st.divider()
theme.section("5. Reproducibility")

st.markdown(
    f"""
- One command runs the whole demo: `bash scripts/phase11/demo_run.sh dry_run`
- The deterministic policy is in `scripts/phase11/policies/remediation_rules.yaml`
- Every incident has a JSON, a markdown report, a manifest, and a rollback script.
- Default action mode is `dry_run`. `apply` mode requires the explicit flag and
  the target must pass the allowlist defined in the policy file.
"""
)
