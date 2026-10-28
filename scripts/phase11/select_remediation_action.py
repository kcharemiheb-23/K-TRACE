#!/usr/bin/env python3
"""
Phase 11 - Remediation Policy Engine
Select severity and action based on attack family and intensity.
"""

def select(family_label: str, intensity: str = "medium") -> dict:
    """
    Input:
        family_label: e.g. A1_HTTP_PORTFLOOD
        intensity: low | medium | high

    Output:
        dict with severity and action_id
    """

    family = family_label.split("_")[0] if family_label else "UNKNOWN"

    # Normalize
    intensity = (intensity or "medium").lower()

    # Default response
    severity = "LOW"
    action_id = "WARN"

    # --- Rules ---
    if family == "A1":
        if intensity == "low":
            severity = "LOW"
            action_id = "WARN"
        else:
            severity = "MEDIUM"
            action_id = "RATE_LIMIT_OR_DENY"

    elif family == "A2":
        if intensity == "low":
            severity = "LOW"
            action_id = "WARN"
        else:
            severity = "MEDIUM"
            action_id = "RATE_LIMIT_OR_DENY"

    elif family == "A3":
        if intensity == "low":
            severity = "MEDIUM"
            action_id = "ISOLATE_POD"
        else:
            severity = "HIGH"
            action_id = "ISOLATE_POD"

    elif family == "A4":
        if intensity == "low":
            severity = "MEDIUM"
            action_id = "RATE_LIMIT_OR_DENY"
        else:
            severity = "HIGH"
            action_id = "RATE_LIMIT_OR_DENY"

    else:
        severity = "LOW"
        action_id = "NONE"

    return {
        "severity": severity,
        "action_id": action_id,
    }
