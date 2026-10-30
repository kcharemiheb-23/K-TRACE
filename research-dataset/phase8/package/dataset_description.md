Dataset Name:
Cloud Native Security Telemetry Dataset

Sources:
- Envoy Access Logs
- Prometheus Metrics
- Falco Runtime Alerts

Attack Classes:
A1_PORT_SCAN
A2_HTTP_FLOOD
A3_INVALID_REQUEST_SPRAY
A4_RUNTIME_RECON
A5_LATERAL_MOVEMENT
A6_EXPLOIT_LIKE_PAYLOADS

Features:
timestamp
source_namespace
source_pod
destination_service
protocol
method
status_code
latency_ms
bytes_in
bytes_out
event_type
runtime_rule
attack_label

Dataset Uses:
- Intrusion detection
- Anomaly detection
- Machine learning baselines
- LLM security reasoning
