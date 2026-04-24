#!/usr/bin/env python3
"""Home Assistant add-on scheduler for a SONOFF water valve."""

from __future__ import annotations

import json
import threading
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo


OPTIONS_PATH = Path("/data/options.json")
VALID_WEEKDAYS = {"mon", "tue", "wed", "thu", "fri", "sat", "sun"}


@dataclass(frozen=True)
class ScheduleEntry:
    name: str
    time_text: str
    duration_minutes: int
    weekdays: list[str] | None


def log(level: str, message: str) -> None:
    print(f"[{level}] {message}", flush=True)


def load_options() -> dict[str, Any]:
    options = json.loads(OPTIONS_PATH.read_text(encoding="utf-8"))
    required = {"ha_url", "ha_token", "entity_id", "schedule_file", "timezone"}
    missing = sorted(required - set(options))
    if missing:
        raise ValueError("Missing required add-on options: " + ", ".join(missing))
    return options


def normalize_time(value: str) -> str:
    value = value.strip()
    parts = value.split(":")
    if len(parts) not in {2, 3}:
        raise ValueError(f"Invalid time '{value}'.")
    if any(not part.isdigit() for part in parts):
        raise ValueError(f"Invalid time '{value}'.")
    hours, minutes = int(parts[0]), int(parts[1])
    seconds = int(parts[2]) if len(parts) == 3 else 0
    if hours not in range(24) or minutes not in range(60) or seconds not in range(60):
        raise ValueError(f"Invalid time '{value}'.")
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def load_schedule_file(path: str) -> list[ScheduleEntry]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    schedules = []
    for raw in data.get("schedules", []):
        if not raw.get("enabled", True):
            continue
        name = str(raw["name"]).strip()
        duration = int(raw["duration_minutes"])
        if duration <= 0:
            raise ValueError(f"Schedule '{name}' must use a positive duration.")
        weekdays = raw.get("weekdays")
        if weekdays is not None:
            weekdays = [str(day).lower() for day in weekdays]
            invalid = [day for day in weekdays if day not in VALID_WEEKDAYS]
            if invalid:
                raise ValueError(
                    f"Schedule '{name}' contains invalid weekdays: {', '.join(invalid)}."
                )
        schedules.append(
            ScheduleEntry(
                name=name,
                time_text=normalize_time(str(raw["time"])),
                duration_minutes=duration,
                weekdays=weekdays,
            )
        )
    return schedules


def call_service(options: dict[str, Any], service: str) -> None:
    entity_id = options["entity_id"]
    domain = entity_id.split(".", 1)[0]
    url = f"{options['ha_url'].rstrip('/')}/api/services/{domain}/{service}"
    payload = json.dumps({"entity_id": entity_id}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {options['ha_token']}",
            "Content-Type": "application/json",
        },
    )
    timeout = int(options.get("request_timeout_seconds", 30))
    with urllib.request.urlopen(request, timeout=timeout) as response:
        response.read()


def execute_schedule(options: dict[str, Any], schedule: ScheduleEntry) -> None:
    log("info", f"Running schedule '{schedule.name}' for {schedule.duration_minutes} minute(s)")
    if options.get("dry_run", False):
        log("info", f"[dry-run] Would turn on {options['entity_id']}")
        log("info", f"[dry-run] Would wait {schedule.duration_minutes} minute(s)")
        log("info", f"[dry-run] Would turn off {options['entity_id']}")
        return

    try:
        call_service(options, "turn_on")
        log("info", f"Turned on {options['entity_id']}")
        time.sleep(schedule.duration_minutes * 60)
        call_service(options, "turn_off")
        log("info", f"Turned off {options['entity_id']}")
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        log("error", f"Home Assistant returned HTTP {exc.code}: {body}")
    except urllib.error.URLError as exc:
        log("error", f"Could not reach Home Assistant: {exc}")
    except Exception as exc:  # pragma: no cover
        log("error", f"Unexpected scheduler error: {exc}")


def should_run(schedule: ScheduleEntry, now: datetime) -> bool:
    if schedule.weekdays:
        weekday = now.strftime("%a").lower()[:3]
        if weekday not in schedule.weekdays:
            return False
    return now.strftime("%H:%M") == schedule.time_text[:5]


def main() -> int:
    options = load_options()
    entity_id = str(options["entity_id"])
    if "." not in entity_id:
        raise ValueError("entity_id must include a domain, for example switch.sonoff_water_valve")

    try:
        timezone = ZoneInfo(str(options["timezone"]))
    except Exception as exc:
        raise ValueError(f"Invalid timezone '{options['timezone']}': {exc}") from exc
    poll_interval = max(5, int(options.get("poll_interval_seconds", 20)))
    fired_keys: set[str] = set()

    log("info", f"Using timezone {options['timezone']}")
    log("info", f"Loading schedules from {options['schedule_file']}")

    while True:
        now = datetime.now(timezone).replace(microsecond=0)
        try:
            schedules = load_schedule_file(str(options["schedule_file"]))
            active_prefix = now.strftime("%Y-%m-%d")
            fired_keys = {key for key in fired_keys if key.startswith(active_prefix)}
            for schedule in schedules:
                fire_key = f"{active_prefix}:{schedule.name}:{schedule.time_text[:5]}"
                if fire_key in fired_keys:
                    continue
                if should_run(schedule, now):
                    fired_keys.add(fire_key)
                    thread = threading.Thread(
                        target=execute_schedule,
                        args=(options, schedule),
                        daemon=True,
                    )
                    thread.start()
        except FileNotFoundError:
            log("warning", f"Schedule file not found: {options['schedule_file']}")
        except Exception as exc:  # pragma: no cover
            log("error", f"Failed to process schedule file: {exc}")

        time.sleep(poll_interval)


if __name__ == "__main__":
    raise SystemExit(main())
