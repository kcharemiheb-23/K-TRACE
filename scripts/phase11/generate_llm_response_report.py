#!/usr/bin/env python3
"""Phase 11 - Generate explanation/impact/recommendation via local Mistral.

Calls the ollama CLI to keep things lightweight and dependency-free.
Returns three markdown blocks. Fails gracefully if Ollama is unavailable.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path.home() / "cloud-native-ids-azure"

PROMPT_TEMPLATE = """You are an offline IDS analyst assistant. The classifier has already
decided this run is an attack of family {family}. Do NOT reclassify and do NOT propose
remediation actions; that is decided by a separate policy engine.

Run identifier: {run_id}
Attack family: {family}
Intensity: {intensity}
Source pod: {source_pod} (namespace: {source_namespace})
Target scope: {target_scope}

Top retrieved evidence (already validated):
{evidence_block}

Produce three short sections, each at most six sentences. Use plain analyst
English. Cite only the evidence above. Do not invent facts.

## Explanation
Why this run looks like family {family}, grounded in the evidence.

## Impact
What an analyst should worry about for this attack family in a cloud-native
microservice environment.

## Recommendation
Free-text analyst recommendation for human review. Do NOT prescribe a
specific Kubernetes action; the policy engine decides that.
"""

SECTION_RE = re.compile(r"##\s+(Explanation|Impact|Recommendation)\s*(.*?)(?=##\s+|\Z)",
                        re.DOTALL | re.IGNORECASE)

def _format_evidence(chunks):
    lines = []
    for c in chunks[:5]:
        prev = (c.get("text_preview") or "").replace("\n", " ").strip()
        if len(prev) > 220:
            prev = prev[:220] + "..."
        lines.append(f"- rank {c['rank']} | {c['doc_name']} ({c.get('family','UNKNOWN')}): {prev}")
    return "\n".join(lines) if lines else "- (no evidence retrieved)"

def call_mistral(prompt: str, model: str = "mistral", timeout_sec: int = 120) -> dict:
    try:
        proc = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True, text=True, timeout=timeout_sec,
        )
    except FileNotFoundError:
        return {"ok": False, "error": "ollama not in PATH", "raw": ""}
    except subprocess.TimeoutExpired:
        return {"ok": False, "error": f"ollama timed out after {timeout_sec}s", "raw": ""}
    if proc.returncode != 0:
        return {"ok": False, "error": proc.stderr.strip()[:300], "raw": proc.stdout}
    return {"ok": True, "raw": proc.stdout}

def split_sections(raw: str) -> dict:
    out = {"explanation_md": "", "impact_md": "", "recommendation_md": ""}
    for m in SECTION_RE.finditer(raw):
        name = m.group(1).strip().lower()
        body = m.group(2).strip()
        out[f"{name}_md"] = body
    if not any(out.values()):
        out["explanation_md"] = raw.strip()
    return out

def generate(run_id: str, family: str, source: dict, retrieval: dict) -> dict:
    prompt = PROMPT_TEMPLATE.format(
        run_id=run_id,
        family=family,
        intensity=source.get("intensity", "unknown"),
        source_pod=source.get("pod", "unknown"),
        source_namespace=source.get("namespace", "unknown"),
        target_scope=source.get("target_scope", "unknown"),
        evidence_block=_format_evidence(retrieval.get("chunks", [])),
    )
    res = call_mistral(prompt)
    if not res["ok"]:
        return {
            "model": "mistral", "ok": False, "error": res["error"],
            "explanation_md": f"_LLM unavailable: {res['error']}_",
            "impact_md": "", "recommendation_md": "",
        }
    parts = split_sections(res["raw"])
    return {"model": "mistral", "ok": True, "raw": res["raw"], **parts}

if __name__ == "__main__":
    # Smoke test
    src = {"namespace":"app","pod":"falco-test","target_scope":"in_container_runtime","intensity":"low"}
    ret = {"chunks":[{"rank":1,"doc_name":"A3_LOW_002.md","family":"A3","text_preview":"runtime reconnaissance ..."}]}
    out = generate("A3_LOW_002", "A3", src, ret)
    print(json.dumps({k:v for k,v in out.items() if k != "raw"}, indent=2)[:1000])
