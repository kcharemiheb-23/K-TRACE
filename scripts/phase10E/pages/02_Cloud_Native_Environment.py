"""Phase 10E v2 - Page 02: Cloud-native environment context."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import streamlit as st

import _theme as theme

theme.page_header(
    title="Cloud-Native Environment",
    subtitle="Single Azure VM, single-node K3s, namespace-separated workloads",
    emoji="☁️",
)

st.markdown(
    """
The project runs on a single Azure VM hosting a single-node K3s cluster.
Logical separation between application, attack, telemetry, and observability
workloads is achieved through Kubernetes namespaces rather than physical
isolation.
"""
)

theme.section("Namespace layout")

st.markdown(
    """
| Namespace | Purpose | Key workloads |
|---|---|---|
| `app` | Online Boutique microservices | frontend, productcatalogservice, cartservice, etc. |
| `attacks` | Internal attacker pod | `netshoot` runs all controlled attacks |
| `istio-system` | Service mesh | Istio control plane, Envoy sidecars |
| `falco` | Runtime security | Falco daemonset + Falcosidekick |
| `monitoring` | Metrics | Prometheus, kube-state-metrics, node-exporter |
"""
)

theme.section("Telemetry sources")

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("**Envoy / Istio**")
    st.markdown(
        "HTTP request and response logs from the service mesh. Source for "
        "request rate, response codes, URI paths, and request volume signals."
    )
with c2:
    st.markdown("**Falco**")
    st.markdown(
        "Runtime security alerts from the kernel. Source for shell execution, "
        "filesystem inspection, and container runtime anomalies."
    )
with c3:
    st.markdown("**Prometheus**")
    st.markdown(
        "Application and infrastructure metrics. Source for resource usage, "
        "request rate counters, and pod-level activity signals."
    )

theme.section("Attack taxonomy (final accepted)")

st.markdown("The project uses five mutually exclusive controlled scenario classes:")

for fam in ["A1", "A2", "A3", "A4", "BENIGN"]:
    color = theme.FAMILY_COLORS[fam]
    name = theme.FAMILY_HUMAN_NAMES[fam]
    st.markdown(
        f"<div style='background-color:{color};color:white;padding:8px 14px;"
        f"border-radius:6px;margin-bottom:6px;font-weight:600'>{name}</div>",
        unsafe_allow_html=True,
    )

theme.info_box(
    "Why this taxonomy",
    "The original taxonomy was redesigned after supervisor feedback and "
    "confusion-matrix analysis. The current five classes are the minimal set "
    "that produces clean class boundaries in the run-level dataset while "
    "still covering the four attack categories most relevant to a "
    "cloud-native microservice deployment.",
)
