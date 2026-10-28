#!/usr/bin/env python3
import csv
import pathlib
import random

HOME = pathlib.Path.home()
ROOT = HOME / "cloud-native-ids-azure"
PLANS = ROOT / "scripts" / "phase7" / "plans"
PLANS.mkdir(parents=True, exist_ok=True)

pilot_path = PLANS / "pilot_plan.csv"
full_path = PLANS / "full_plan.csv"

fields = [
    "run_id","class_label","scenario_family","subtype","intensity","benign_type",
    "source_namespace","source_pod","target_scope","duration_sec",
    "trim_start_sec","trim_end_sec","payload_cmd"
]

pilot_rows = [
    {
        "run_id":"PILOT_BENIGN_CONTROLLED_NORMAL_001","class_label":"BENIGN","scenario_family":"BENIGN",
        "subtype":"CONTROLLED_NORMAL","intensity":"none","benign_type":"CONTROLLED",
        "source_namespace":"app","source_pod":"loadgenerator","target_scope":"frontend","duration_sec":"180",
        "trim_start_sec":"10","trim_end_sec":"10",
        "payload_cmd":f'bash "{ROOT}/scripts/phase7/02_benign_controlled_normal.sh" 180'
    },
    {
        "run_id":"PILOT_BENIGN_CONTINUOUS_BROWSE_001","class_label":"BENIGN","scenario_family":"BENIGN",
        "subtype":"CONTINUOUS_BROWSE","intensity":"none","benign_type":"CONTINUOUS",
        "source_namespace":"app","source_pod":"benign-browser","target_scope":"frontend","duration_sec":"300",
        "trim_start_sec":"10","trim_end_sec":"10",
        "payload_cmd":f'bash "{ROOT}/scripts/phase7/05_benign_continuous_browse.sh" 300'
    },
    {
        "run_id":"PILOT_A1_LOW_001","class_label":"A1_HTTP_PORTFLOOD","scenario_family":"ATTACK",
        "subtype":"A1_HTTP_PORTFLOOD","intensity":"low","benign_type":"NA",
        "source_namespace":"attacks","source_pod":"netshoot","target_scope":"internal_app_services","duration_sec":"120",
        "trim_start_sec":"10","trim_end_sec":"10",
        "payload_cmd":f'bash "{ROOT}/scripts/phase7/11_attack_http_portflood.sh" 120 low'
    },
    {
        "run_id":"PILOT_A2_LOW_001","class_label":"A2_INVALID_REQUEST_SPRAY","scenario_family":"ATTACK",
        "subtype":"A2_INVALID_REQUEST_SPRAY","intensity":"low","benign_type":"NA",
        "source_namespace":"attacks","source_pod":"netshoot","target_scope":"frontend_http","duration_sec":"120",
        "trim_start_sec":"10","trim_end_sec":"10",
        "payload_cmd":f'bash "{ROOT}/scripts/phase7/12_attack_invalid_request_spray.sh" 120 low'
    },
    {
        "run_id":"PILOT_A3_LOW_001","class_label":"A3_RUNTIME_RECON","scenario_family":"ATTACK",
        "subtype":"A3_RUNTIME_RECON","intensity":"low","benign_type":"NA",
        "source_namespace":"app","source_pod":"falco-test","target_scope":"in_container_runtime","duration_sec":"120",
        "trim_start_sec":"10","trim_end_sec":"10",
        "payload_cmd":f'bash "{ROOT}/scripts/phase7/13_attack_runtime_recon.sh" 120 low'
    },
    {
        "run_id":"PILOT_A4_LOW_001","class_label":"A4_EXPLOIT_LIKE_PAYLOADS","scenario_family":"ATTACK",
        "subtype":"A4_EXPLOIT_LIKE_PAYLOADS","intensity":"low","benign_type":"NA",
        "source_namespace":"attacks","source_pod":"netshoot","target_scope":"frontend_http","duration_sec":"120",
        "trim_start_sec":"10","trim_end_sec":"10",
        "payload_cmd":f'bash "{ROOT}/scripts/phase7/14_attack_exploit_like_payloads.sh" 120 low'
    },
]

full_rows = []

def add_attack(label, script_name):
    prefix = {
        "A1_HTTP_PORTFLOOD":"A1",
        "A2_INVALID_REQUEST_SPRAY":"A2",
        "A3_RUNTIME_RECON":"A3",
        "A4_EXPLOIT_LIKE_PAYLOADS":"A4",
    }[label]
    src_ns = "app" if label == "A3_RUNTIME_RECON" else "attacks"
    src_pod = "falco-test" if label == "A3_RUNTIME_RECON" else "netshoot"
    target = "in_container_runtime" if label == "A3_RUNTIME_RECON" else ("internal_app_services" if label == "A1_HTTP_PORTFLOOD" else "frontend_http")
    for intensity in ["low","medium","high"]:
        for rep in range(1, 6):
            full_rows.append({
                "run_id":f"{prefix}_{intensity.upper()}_{rep:03d}",
                "class_label":label,
                "scenario_family":"ATTACK",
                "subtype":label,
                "intensity":intensity,
                "benign_type":"NA",
                "source_namespace":src_ns,
                "source_pod":src_pod,
                "target_scope":target,
                "duration_sec":"120",
                "trim_start_sec":"10",
                "trim_end_sec":"10",
                "payload_cmd":f'bash "{ROOT}/scripts/phase7/{script_name}" 120 {intensity}'
            })

def add_benign(prefix, subtype, benign_type, source_pod, duration, count, script_name):
    for rep in range(1, count + 1):
        full_rows.append({
            "run_id":f"{prefix}_{rep:03d}",
            "class_label":"BENIGN",
            "scenario_family":"BENIGN",
            "subtype":subtype,
            "intensity":"none",
            "benign_type":benign_type,
            "source_namespace":"app",
            "source_pod":source_pod,
            "target_scope":"frontend",
            "duration_sec":str(duration),
            "trim_start_sec":"10",
            "trim_end_sec":"10",
            "payload_cmd":f'bash "{ROOT}/scripts/phase7/{script_name}" {duration}'
        })

add_attack("A1_HTTP_PORTFLOOD", "11_attack_http_portflood.sh")
add_attack("A2_INVALID_REQUEST_SPRAY", "12_attack_invalid_request_spray.sh")
add_attack("A3_RUNTIME_RECON", "13_attack_runtime_recon.sh")
add_attack("A4_EXPLOIT_LIKE_PAYLOADS", "14_attack_exploit_like_payloads.sh")

add_benign("BENIGN_CONTROLLED_IDLE", "CONTROLLED_IDLE", "CONTROLLED", "none", 180, 10, "01_benign_controlled_idle.sh")
add_benign("BENIGN_CONTROLLED_NORMAL", "CONTROLLED_NORMAL", "CONTROLLED", "loadgenerator", 180, 10, "02_benign_controlled_normal.sh")
add_benign("BENIGN_CONTROLLED_PEAK", "CONTROLLED_PEAK", "CONTROLLED", "benign-browser", 180, 10, "03_benign_controlled_peak.sh")
add_benign("BENIGN_CONTINUOUS_NORMAL", "CONTINUOUS_NORMAL", "CONTINUOUS", "loadgenerator", 300, 15, "04_benign_continuous_normal.sh")
add_benign("BENIGN_CONTINUOUS_BROWSE", "CONTINUOUS_BROWSE", "CONTINUOUS", "benign-browser", 300, 15, "05_benign_continuous_browse.sh")

rng = random.Random(42)
rng.shuffle(full_rows)

for path, rows in [(pilot_path, pilot_rows), (full_path, full_rows)]:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

print(f"Wrote {pilot_path}")
print(f"Wrote {full_path}")
print(f"Pilot rows: {len(pilot_rows)}")
print(f"Full rows: {len(full_rows)}")
