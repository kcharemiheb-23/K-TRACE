# Project Glossary

## RAG and retrieval terms
- **RAG**: Retrieval-Augmented Generation. A pipeline pattern in which a retrieval step provides evidence chunks to an LLM before reasoning.
- **LLM**: Large Language Model. The reasoning component of the pipeline.
- **Top-k retrieval**: selecting the k most relevant retrieved chunks for the LLM to reason over.
- **Dense semantic retrieval**: ranking chunks by cosine similarity in embedding space.
- **BM25**: a sparse lexical ranking function based on term frequency and inverse document frequency.
- **Hybrid retrieval**: combining dense and BM25 rankings, often using Reciprocal Rank Fusion.
- **Reciprocal Rank Fusion (RRF)**: a parameter-free score fusion method that combines multiple rankings using the formula score = sum over rankers of 1 / (k + rank).
- **Metadata-aware reranking**: post-retrieval reordering using structured chunk metadata such as attack family or document type.

## Telemetry source terms
- **Envoy**: service-mesh proxy. Source of HTTP request and response telemetry.
- **Falco**: runtime security telemetry. Source of syscall and container behavior alerts.
- **Prometheus**: metrics telemetry source for infrastructure and application metrics.

## ML task terms
- **Binary task**: ATTACK vs BENIGN classification.
- **Multiclass task**: BENIGN plus A1 plus A2 plus A3 plus A4 classification.
- **Run-level dataset**: each row corresponds to one controlled run, not one packet.

## Corpus terms
- **Case document**: one run-level knowledge document built from validated outputs of a single controlled run.
- **Corpus**: the full document collection that is chunked and embedded for retrieval.
- **Chunk**: a substring of a corpus document used as the unit of retrieval.

## Attack family taxonomy

### A1 - HTTP_PORTFLOOD
HTTP request flooding and port probing attacks. Characterized by elevated frontend request volume, high HTTP request count per unit time, port probing patterns, and traffic pressure on the service mesh. Common vocabulary includes A1, HTTP_PORTFLOOD, portflood, http flood, flood, request volume, request count, traffic pressure, port probing, frontend request, high request.

### A2 - INVALID_REQUEST_SPRAY
Malformed HTTP requests, invalid methods, and suspicious URI behavior. Characterized by elevated 4xx responses, malformed HTTP methods including TRACE, abnormal URI patterns, suspicious paths, and application-layer probing. Common vocabulary includes A2, INVALID_REQUEST_SPRAY, invalid request, malformed, bad path, suspicious path, 4xx, TRACE, abnormal uri, application-layer probing.

### A3 - RUNTIME_RECON
Runtime reconnaissance behavior inside containers. Characterized by shell execution, process discovery, filesystem inspection, and Falco runtime alerts. Common vocabulary includes A3, RUNTIME_RECON, runtime recon, runtime reconnaissance, Falco, shell, process, filesystem, whoami, uname, cat /etc/passwd, container activity.

### A4 - EXPLOIT_LIKE_PAYLOADS
Exploit-like HTTP payloads. Characterized by path traversal sequences, injection-like URLs, and suspicious encoded payloads in HTTP request URIs. Common vocabulary includes A4, EXPLOIT_LIKE_PAYLOADS, exploit-like, payload, path traversal, injection, encoded payload, suspicious URL, suspicious URI.

### BENIGN
Benign cloud-native microservice activity. Characterized by normal browse and idle behaviors against the frontend service, with no attack signatures. Common vocabulary includes BENIGN, benign, normal, idle, browse, non-attack, baseline, normal load, controlled idle, continuous browse.

## Benign run subtypes
- **CONTROLLED_IDLE**: the system is held idle with no user load, used to validate the no-traffic baseline.
- **CONTROLLED_NORMAL**: the system runs the load generator at normal rate.
- **CONTROLLED_PEAK**: the system runs the load generator at peak rate to validate high-but-benign behavior.
- **CONTINUOUS_NORMAL**: continuous-collection benign run at normal rate.
- **CONTINUOUS_BROWSE**: continuous-collection benign browsing pattern.
