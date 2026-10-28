#!/usr/bin/env python3
"""Phase 11 - Render and conditionally execute a remediation manifest.

Modes:
  - explain_only : write manifest + rollback file, do not run kubectl.
  - dry_run      : write files, run kubectl apply --dry-run=client.
  - apply        : write files, run kubectl apply, subject to guardrails.

Guardrails for apply mode are read from remediation_rules.yaml and reject
any target outside the allowlist. The default mode is dry_run.
"""
from __future__ import annotations

import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

ROOT = Path.home() / "cloud-native-ids-azure"
TEMPLATES = ROOT / "scripts/phase11/policies/manifest_templates"
POLICY = ROOT / "scripts/phase11/policies/remediation_rules.yaml"
ACTIONS_DIR = ROOT / "artifacts/phase11/actions"

VALID_MODES = {"explain_only", "dry_run", "apply"}
ACTION_TO_TEMPLATE = {
    "ISOLATE_POD": "isolate_pod.yaml.j2",
    "RATE_LIMIT_OR_DENY": "rate_limit_or_deny.yaml.j2",
}

ENV = Environment(
    loader=FileSystemLoader(str(TEMPLATES)),
    autoescape=select_autoescape(),
    keep_trailing_newline=True,
)

def _load_guardrails() -> dict:
    return yaml.safe_load(POLICY.read_text()).get("apply_guardrails", {})

def _short_id(incident_id: str) -> str:
    short = re.sub(r"[^a-zA-Z0-9]+", "-", incident_id).lower()
    return short[:50].strip("-")

def render_manifest(action_id: str, incident_id: str, run_id: str,
                    family: str, severity: str, source: dict) -> str:
    if action_id in ("NONE", "WARN"):
        return ""  # no manifest needed
    if action_id not in ACTION_TO_TEMPLATE:
        raise ValueError(f"unknown action_id {action_id!r}")
    tmpl = ENV.get_template(ACTION_TO_TEMPLATE[action_id])
    ctx = {
        "incident_id": incident_id,
        "incident_id_short": _short_id(incident_id),
        "run_id": run_id,
        "family": family,
        "severity": severity,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "target_namespace": source.get("namespace", "app"),
        "frontend_namespace": "app",
        "target_pod_label": source.get("pod", "unknown"),
        "attacker_pod_label": source.get("pod", "unknown"),
    }
    return tmpl.render(**ctx)

def _check_apply_guardrails(action_id: str, source: dict) -> tuple[bool, str]:
    g = _load_guardrails()
    target_ns = source.get("namespace", "")
    target_pod = source.get("pod", "")
    if target_ns not in g.get("allowed_target_namespaces", []):
        return False, f"namespace {target_ns!r} not in apply allowlist"
    if target_pod in g.get("forbidden_target_pod_names", []):
        return False, f"pod {target_pod!r} is in the forbidden core-services list"
    if action_id == "ISOLATE_POD":
        prefixes = g.get("allowed_attacker_pod_prefixes", [])
        if not any(target_pod.startswith(p) for p in prefixes):
            return False, f"pod {target_pod!r} does not match any allowed attacker prefix"
    return True, ""

def execute(action_id: str, incident_id: str, run_id: str, family: str,
            severity: str, source: dict, mode: str = "dry_run") -> dict:
    if mode not in VALID_MODES:
        raise ValueError(f"mode must be one of {VALID_MODES}, got {mode!r}")
    ACTIONS_DIR.mkdir(parents=True, exist_ok=True)

    short = _short_id(incident_id)
    manifest_path = ACTIONS_DIR / f"{short}.yaml"
    rollback_path = ACTIONS_DIR / f"{short}.rollback.sh"

    out = {
        "mode": mode,
        "manifest_path": "",
        "rollback_path": "",
        "kubectl_command": "",
        "kubectl_stdout": "",
        "kubectl_stderr": "",
        "applied": False,
        "guardrail_blocked": False,
        "guardrail_reason": "",
    }

    if action_id in ("NONE", "WARN"):
        out["kubectl_stdout"] = f"action {action_id}; no manifest produced."
        return out

    manifest_text = render_manifest(action_id, incident_id, run_id, family, severity, source)
    manifest_path.write_text(manifest_text)
    out["manifest_path"] = str(manifest_path)

    rollback_path.write_text(f"#!/bin/bash\nkubectl delete -f {manifest_path} || true\n")
    rollback_path.chmod(0o755)
    out["rollback_path"] = str(rollback_path)

    if mode == "explain_only":
        out["kubectl_command"] = "(none; explain_only mode)"
        return out

    kctl = shutil.which("kubectl")
    if not kctl:
        out["kubectl_stderr"] = "kubectl not found in PATH"
        return out

    if mode == "apply":
        ok, reason = _check_apply_guardrails(action_id, source)
        if not ok:
            out["guardrail_blocked"] = True
            out["guardrail_reason"] = reason
            out["kubectl_stderr"] = f"apply blocked by guardrails: {reason}"
            return out
        cmd = [kctl, "apply", "-f", str(manifest_path)]
    else:
        cmd = [kctl, "apply", "-f", str(manifest_path), "--dry-run=client"]

    out["kubectl_command"] = " ".join(cmd)
    res = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
    out["kubectl_stdout"] = res.stdout.strip()
    out["kubectl_stderr"] = res.stderr.strip()
    out["applied"] = (mode == "apply" and res.returncode == 0)
    return out

if __name__ == "__main__":
    src = {"namespace": "app", "pod": "falco-test", "intensity": "low"}
    res = execute("ISOLATE_POD", "INC_DEMO_A3_LOW_002", "A3_LOW_002",
                  "A3", "MEDIUM", src, mode="dry_run")
    print(json.dumps(res, indent=2))
