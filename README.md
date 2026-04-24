# Home Assistant Add-on Repository: SONOFF Water Valve

This repository is structured like a Home Assistant add-on repository, following the same high-level format used by [`zigbee2mqtt/hassio-zigbee2mqtt`](https://github.com/zigbee2mqtt/hassio-zigbee2mqtt):

- a root `repository.json`
- one add-on directory per add-on
- add-on metadata in `config.json`
- container assets such as `Dockerfile`, `run.sh`, and `rootfs/`

## Included add-on

- `sonoff-water-valve`: a time-based scheduler that calls the Home Assistant REST API to control a SONOFF water valve entity

## Expected Home Assistant setup

This add-on assumes:

- your SONOFF water valve already exists in Home Assistant as an entity such as `switch.sonoff_water_valve`
- you have created a Home Assistant long-lived access token
- you will place a schedule file under your Home Assistant config directory, for example:

```text
/config/sonoff-water-valve/schedule.json
```

## Example schedule file

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

## Notes

- This repository format is an adaptation based on the `hassio-zigbee2mqtt` repository structure, not a copy of its implementation.
- The scheduler in this repo is specific to a SONOFF/Home Assistant water valve workflow.
