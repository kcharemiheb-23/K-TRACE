#!/usr/bin/env python3
"""Phase 11 - Render an analyst-readable markdown report from an incident JSON."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"

def render(incident: dict) -> str:
    src = incident.get("source", {})
    ml = incident.get("ml", {})
    ret = incident.get("retrieval", {})
    llm = incident.get("llm", {})
    pol = incident.get("policy", {})
    rem = incident.get("remediation", {})

    lines = [
        f"# Incident {incident.get('incident_id', '')}",
        "",
        f"- run_id: `{incident.get('run_id', '')}`",
        f"- timestamp_utc: {incident.get('timestamp_utc', '')}",
        "",
        "## Source context",
        f"- namespace: {src.get('namespace', 'unknown')}",
        f"- pod: {src.get('pod', 'unknown')}",
        f"- target_scope: {src.get('target_scope', 'unknown')}",
        f"- intensity: {src.get('intensity', 'unknown')}",
        f"- duration_sec: {src.get('duration_sec', 'unknown')}",
        "",
        "## ML attack gate",
        f"- binary: `{ml.get('binary_pred','')}` (model {ml.get('binary_model','')})",
        f"- multiclass: `{ml.get('multiclass_pred','')}` (model {ml.get('multiclass_model','')})",
        f"- family: **{ml.get('family','')}**",
        f"- gate_decision: **{ml.get('gate_decision','')}**",
        "",
        "## Top retrieved evidence",
        f"- mode: `{ret.get('mode','')}`  top_k: {ret.get('top_k','')}",
        "",
    ]
    for c in ret.get("chunks", []):
        prev = (c.get("text_preview") or "").replace("\n", " ").strip()
        if len(prev) > 220: prev = prev[:220] + "..."
        lines.append(f"  {c['rank']}. `{c['doc_name']}` ({c.get('family','?')}, {c.get('section','?')}) — score {c.get('score',0):.4f}")
        if prev: lines.append(f"     > {prev}")
    lines.append("")

    lines.extend([
        "## LLM analyst reasoning",
        f"- model: {llm.get('model','')}",
        f"- ok: {llm.get('ok', False)}",
        "",
        "### Explanation",
        llm.get("explanation_md", "_(none)_") or "_(none)_",
        "",
        "### Impact",
        llm.get("impact_md", "_(none)_") or "_(none)_",
        "",
        "### Recommendation",
        llm.get("recommendation_md", "_(none)_") or "_(none)_",
        "",
        "## Policy decision (deterministic)",
        f"- family: {pol.get('family','')}  intensity: {pol.get('intensity','')}",
        f"- severity: **{pol.get('severity','')}**",
        f"- action: **{pol.get('action_id','')}**",
        f"- matched_rule: `{pol.get('matched_rule','')}`",
        f"- rationale: {pol.get('rationale','')}",
        "",
        "## Remediation",
        f"- mode: `{rem.get('mode','')}`",
        f"- applied: {rem.get('applied', False)}",
        f"- manifest_path: `{rem.get('manifest_path','')}`",
        f"- rollback_path: `{rem.get('rollback_path','')}`",
        f"- kubectl_command: `{rem.get('kubectl_command','')}`",
    ])
    if rem.get("guardrail_blocked"):
        lines.append(f"- **guardrail_blocked**: {rem.get('guardrail_reason','')}")
    if rem.get("kubectl_stdout"):
        lines.extend(["", "```", rem["kubectl_stdout"], "```"])
    if rem.get("kubectl_stderr"):
        lines.extend(["", "**stderr:**", "```", rem["kubectl_stderr"], "```"])
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("usage: render_incident_report.py <incident.json>")
        raise SystemExit(2)
    inc = json.loads(Path(sys.argv[1]).read_text())
    print(render(inc))
