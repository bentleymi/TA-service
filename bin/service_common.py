"""Shared collection logic for TA-service scripted inputs (systemctl)."""
import json
import os
import subprocess
import sys

SYSTEMCTL = os.environ.get("TA_SERVICE_SYSTEMCTL", "systemctl")
MAX_FAILED_UNITS = 50


def run_units(state=None):
    """Return list-units lines as a list, or None if systemctl is unavailable."""
    cmd = [SYSTEMCTL, "list-units", "--type=service", "--all", "--no-legend", "--no-pager", "--plain"]
    if state:
        cmd.append("--state=" + state)
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=25)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if p.returncode != 0:
        return None
    return [ln for ln in p.stdout.splitlines() if ln.strip()]


def discover():
    failed_lines = run_units("failed")
    if failed_lines is None:
        return {
            "status": "absent",
            "units_total": 0,
            "active_count": 0,
            "failed_count": 0,
            "failed_units": [],
        }
    failed_units = []
    for ln in failed_lines:
        tok = ln.split()
        if tok:
            failed_units.append(tok[0])
    active = run_units("active")
    total = run_units()
    return {
        "status": "alarm" if failed_lines else "ok",
        "units_total": len(total) if total is not None else 0,
        "active_count": len(active) if active is not None else 0,
        "failed_count": len(failed_lines),
        "failed_units": failed_units[:MAX_FAILED_UNITS],
    }


def metrics_payload(data):
    payload = {}
    for key in ("units_total", "active_count", "failed_count"):
        v = data.get(key)
        if v is not None:
            payload[key] = int(v)
    return payload


def emit(payload):
    sys.stdout.write(json.dumps(payload, sort_keys=True) + "\n")
    sys.stdout.flush()


def fail(message):
    sys.stderr.write("TA-service collection error: %s\n" % message)
    return 1
