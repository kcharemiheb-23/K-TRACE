#!/usr/bin/env bash
set -euo pipefail

DURATION="$1"

kubectl exec -n app falco-test -- sh -c "
END=\$(( \$(date +%s) + $DURATION ))
while [ \"\$(date +%s)\" -lt \"\$END\" ]; do
  whoami >/dev/null
  id >/dev/null
  uname -a >/dev/null
  cat /etc/passwd >/dev/null
  cat /etc/shadow >/dev/null 2>&1 || true
  ls /root >/dev/null 2>&1 || true
  sleep 1
done
"
