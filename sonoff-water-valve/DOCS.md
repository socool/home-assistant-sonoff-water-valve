# SONOFF Water Valve

This add-on runs a simple time-based scheduler for a SONOFF water valve exposed in Home Assistant.

## Configuration

Example add-on options:

```yaml
ha_url: http://homeassistant.local:8123
ha_token: YOUR_LONG_LIVED_ACCESS_TOKEN
entity_id: switch.sonoff_water_valve
schedule_file: /config/sonoff-water-valve/schedule.json
timezone: Asia/Bangkok
request_timeout_seconds: 30
poll_interval_seconds: 20
log_level: info
dry_run: false
```

## Schedule file

Create the schedule file at the configured path, for example `/config/sonoff-water-valve/schedule.json`.

Example:

```json
{
  "schedules": [
    {
      "name": "morning",
      "time": "06:00",
      "duration_minutes": 10,
      "weekdays": ["mon", "wed", "fri"],
      "enabled": true
    },
    {
      "name": "evening",
      "time": "18:00",
      "duration_minutes": 8,
      "enabled": true
    }
  ]
}
```

Fields:

- `name`: label used in logs
- `time`: local time in `HH:MM` or `HH:MM:SS`
- `duration_minutes`: how long to keep the valve on
- `weekdays`: optional list of `mon` through `sun`
- `enabled`: optional boolean, defaults to `true`

## Behavior

- The add-on polls the schedule file repeatedly.
- When the current local time matches a schedule entry, it calls the Home Assistant REST API to turn the valve on.
- After the configured duration, it calls the API again to turn the valve off.
- `dry_run: true` logs actions without sending API requests.

## Notes

- This add-on expects your device to be controllable through a Home Assistant entity like `switch.sonoff_water_valve`.
- If two schedules overlap, they may run at the same time in separate worker threads.
