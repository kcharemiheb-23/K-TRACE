#!/usr/bin/env bash
set -euo pipefail

kubectl exec -n app falco-test -- sh -c '
whoami >/dev/null
id >/dev/null
uname -a >/dev/null
cat /etc/passwd >/dev/null
ls /proc >/dev/null
nslookup kubernetes.default.svc.cluster.local >/dev/null
'
