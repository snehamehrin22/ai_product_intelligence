#!/usr/bin/env bash
# Start mitmproxy for iPhone capture. Usage: scripts/ios_proxy.sh <app-name>
# Prints the Wi-Fi proxy settings to enter on the phone, then logs analytics to
# data/ios_<app>_<timestamp>.jsonl. Label funnel steps with scripts/ios_mark.sh.
set -euo pipefail
cd "$(dirname "$0")/.."
source .venv/bin/activate

APP="${1:?usage: ios_proxy.sh <app-name>}"
PORT="${PORT:-8080}"
IP="$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || true)"
[ -n "$IP" ] || { echo "No Wi-Fi IP found; is the Mac on Wi-Fi?" >&2; exit 1; }

export FUNNEL_OUT="data/ios_${APP}_$(date +%Y%m%d_%H%M%S).jsonl"
export FUNNEL_STEP_FILE="data/ios_step.txt"
mkdir -p data && echo "launch" > "$FUNNEL_STEP_FILE"

cat <<EOF
iPhone: Settings > Wi-Fi > (i) on your network > Configure Proxy > Manual
        Server: $IP    Port: $PORT    Authentication: off
Then open http://mitm.it in Safari to install the cert, and enable it under
Settings > General > About > Certificate Trust Settings.
Logging to: $FUNNEL_OUT   (mark steps: scripts/ios_mark.sh "paywall")
EOF
exec mitmdump --listen-port "$PORT" -s scripts/mitm_addon.py --set termlog_verbosity=warn
