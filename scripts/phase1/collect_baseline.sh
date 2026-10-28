#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-$HOME/cloud-native-ids-azure/docs/proofs/phase1_recheck}"
mkdir -p "$OUT_DIR"

whoami > "$OUT_DIR/whoami.txt"
hostname > "$OUT_DIR/hostname.txt"
date -u > "$OUT_DIR/utc_date.txt"
timedatectl > "$OUT_DIR/timedatectl.txt"
cat /etc/os-release > "$OUT_DIR/os-release.txt"
uname -a > "$OUT_DIR/uname-a.txt"
free -h > "$OUT_DIR/free-h.txt"
lscpu > "$OUT_DIR/lscpu.txt"
lsblk -f > "$OUT_DIR/lsblk-f.txt"
df -h > "$OUT_DIR/df-h.txt"
ip a > "$OUT_DIR/ip-a.txt"
ip route > "$OUT_DIR/ip-route.txt"
ss -tulpn > "$OUT_DIR/ss-tulpn.txt"
tree -L 3 "$HOME/cloud-native-ids-azure" > "$OUT_DIR/repo-tree.txt"

echo "[OK] baseline collected in $OUT_DIR"
