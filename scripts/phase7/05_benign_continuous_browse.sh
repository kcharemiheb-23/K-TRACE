#!/usr/bin/env bash
set -euo pipefail

DURATION="$1"

bash "$HOME/cloud-native-ids-azure/scripts/phase7/set_loadgenerator_mode.sh" continuous_browse
bash "$HOME/cloud-native-ids-azure/scripts/phase7/benign_browser_loop.sh" "$DURATION" 1
