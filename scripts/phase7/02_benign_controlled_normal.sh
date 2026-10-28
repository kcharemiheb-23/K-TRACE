#!/usr/bin/env bash
set -euo pipefail

DURATION="$1"

bash "$HOME/cloud-native-ids-azure/scripts/phase7/set_loadgenerator_mode.sh" normal
sleep "$DURATION"
