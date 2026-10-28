#!/usr/bin/env bash
set -u

RUN_ID="$1"
ATTACK_LABEL="$2"
SOURCE_NS="$3"
SOURCE_POD="$4"
TARGET_SCOPE="$5"
MODE="$6"
PAYLOAD="$7"

LEDGER="$HOME/cloud-native-ids-azure/artifacts/phase6/output/attack-windows.csv"
START_TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
STATUS=0

if [ "$MODE" = "sleep" ]; then
  sleep "$PAYLOAD" || STATUS=$?
elif [ "$MODE" = "script" ]; then
  bash "$PAYLOAD" || STATUS=$?
else
  STATUS=2
fi

END_TS="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"

echo "${RUN_ID},${ATTACK_LABEL},${SOURCE_NS},${SOURCE_POD},${TARGET_SCOPE},${START_TS},${END_TS},${STATUS}" >> "$LEDGER"

echo "[OK] ${RUN_ID} ${ATTACK_LABEL} status=${STATUS}"
