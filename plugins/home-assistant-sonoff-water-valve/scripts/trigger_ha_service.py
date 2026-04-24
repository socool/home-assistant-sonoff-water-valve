#!/usr/bin/env python3
"""Call the Home Assistant REST API for a SONOFF water valve."""

from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


def call_service(ha_url: str, token: str, domain: str, service: str, entity_id: str) -> dict:
    url = f"{ha_url.rstrip('/')}/api/services/{domain}/{service}"
    payload = json.dumps({"entity_id": entity_id}).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=payload,
        method="POST",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = response.read().decode("utf-8")
        return {"status": response.status, "body": body}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ha-url", required=True, help="Base Home Assistant URL.")
    parser.add_argument("--token", required=True, help="Home Assistant long-lived token.")
    parser.add_argument("--entity-id", required=True, help="Entity ID, for example switch.sonoff_water_valve.")
    parser.add_argument(
        "--service",
        choices=["turn_on", "turn_off", "toggle"],
        default="turn_on",
        help="Service to call.",
    )
    parser.add_argument(
        "--duration-minutes",
        type=float,
        default=0,
        help="If set with turn_on, wait this long and then turn the entity off.",
    )
    args = parser.parse_args()

    if "." not in args.entity_id:
        raise ValueError("Entity ID must include a domain, for example switch.sonoff_water_valve.")

    domain = args.entity_id.split(".", 1)[0]

    try:
        result = call_service(args.ha_url, args.token, domain, args.service, args.entity_id)
        print(json.dumps({"step": args.service, **result}, indent=2))
        if args.service == "turn_on" and args.duration_minutes > 0:
            time.sleep(args.duration_minutes * 60)
            follow_up = call_service(args.ha_url, args.token, domain, "turn_off", args.entity_id)
            print(json.dumps({"step": "turn_off", **follow_up}, indent=2))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise SystemExit(f"Home Assistant returned HTTP {exc.code}: {body}") from exc
    except urllib.error.URLError as exc:
        raise SystemExit(f"Could not reach Home Assistant: {exc}") from exc

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
