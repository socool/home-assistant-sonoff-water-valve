#!/usr/bin/with-contenv sh
set -eu

echo "[info] Starting SONOFF Water Valve add-on"
exec python3 /usr/bin/sonoff_scheduler.py
