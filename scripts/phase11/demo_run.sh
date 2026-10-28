#!/usr/bin/env bash
# Phase 11 - one-command demo over the 11 benchmark runs.
set -euo pipefail

ROOT="${HOME}/cloud-native-ids-azure"
BENCH="${ROOT}/artifacts/phase10V/benchmark/validation_benchmark.csv"
ART="${ROOT}/artifacts/phase11"
ORCH="${ROOT}/scripts/phase11/run_response_pipeline.py"
MODE="${1:-dry_run}"

if [[ ! -f "${BENCH}" ]]; then
  echo "ERROR: benchmark CSV missing at ${BENCH}" >&2
  exit 2
fi
if [[ "${MODE}" != "explain_only" && "${MODE}" != "dry_run" && "${MODE}" != "apply" ]]; then
  echo "ERROR: mode must be explain_only|dry_run|apply" >&2
  exit 2
fi

echo "Phase 11 demo - mode=${MODE}"
echo "Resetting incident artifacts (kept under artifacts/phase11/_archive_$(date -u +%Y%m%dT%H%M%SZ))..."
ARCHIVE="${ART}/_archive_$(date -u +%Y%m%dT%H%M%SZ)"
mkdir -p "${ARCHIVE}"
for d in incidents reports actions summary logs; do
  if [[ -d "${ART}/${d}" ]] && [[ -n "$(ls -A "${ART}/${d}" 2>/dev/null || true)" ]]; then
    mv "${ART}/${d}" "${ARCHIVE}/${d}"
    mkdir -p "${ART}/${d}"
  else
    mkdir -p "${ART}/${d}"
  fi
done

# Read run_id column from benchmark CSV (skip header).
RUNS=$(awk -F, 'NR>1 {print $1}' "${BENCH}" | sed 's/\r$//' | sort -u)
N=0
for RID in ${RUNS}; do
  N=$((N+1))
  echo ""
  echo "==> [${N}] ${RID}"
  python3 "${ORCH}" --run_id "${RID}" --mode "${MODE}" || true
done

echo ""
echo "==== Summary ===="
SUM="${ART}/summary/phase11_run_summary.csv"
if [[ -f "${SUM}" ]]; then
  TOT=$(awk -F, 'NR>1' "${SUM}" | wc -l)
  ATK=$(awk -F, 'NR>1 && $4=="PASS_TO_RAG"' "${SUM}" | wc -l)
  BEN=$(awk -F, 'NR>1 && $4=="SKIP_BENIGN"' "${SUM}" | wc -l)
  ERR=$(awk -F, 'NR>1 && $4=="ERROR"' "${SUM}" | wc -l)
  echo "runs processed : ${TOT}"
  echo "attack incidents: ${ATK}"
  echo "benign skipped : ${BEN}"
  echo "errors         : ${ERR}"
fi
echo ""
echo "Open the dashboard:"
echo "  streamlit run ${ROOT}/scripts/phase10E/dashboard_app.py --server.address 0.0.0.0 --server.port 8501"
