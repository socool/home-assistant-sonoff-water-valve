# Home Assistant SONOFF Water Valve Plugin

This plugin helps you run a SONOFF water valve from Home Assistant on a time-based schedule.

It includes:

- a schedule generator that writes Home Assistant YAML automations
- a direct Home Assistant REST API trigger script for testing or one-off runs
- a Codex skill that guides schedule updates

## What it generates

The generated Home Assistant package uses official automation YAML with time triggers and service actions. Each schedule entry:

1. turns the valve on at the configured time
2. waits for the configured duration
3. turns the valve off

The YAML syntax matches the current Home Assistant automation docs:

- [Automation YAML](https://www.home-assistant.io/docs/automation/yaml/)
- [Automation triggers](https://www.home-assistant.io/docs/automation/trigger/)
- [REST API](https://developers.home-assistant.io/docs/api/rest)

## Quick start

Edit the example schedule:

```bash
python3 scripts/generate_ha_package.py \
  --input config/example_schedule.json \
  --output output/sonoff_water_valve_package.yaml
```

Then copy the generated YAML into your Home Assistant packages folder, for example:

```text
/config/packages/sonoff_water_valve_package.yaml
```

Make sure `configuration.yaml` loads packages, for example:

```yaml
homeassistant:
  packages: !include_dir_named packages
```

After copying the file, reload automations or restart Home Assistant.

## Direct API test

Use a Home Assistant long-lived access token:

```bash
python3 scripts/trigger_ha_service.py \
  --ha-url http://homeassistant.local:8123 \
  --token YOUR_LONG_LIVED_TOKEN \
  --entity-id switch.sonoff_water_valve \
  --service turn_on \
  --duration-minutes 1
```

That command turns the valve on, waits one minute, then turns it off.

## Schedule format

The plugin expects a JSON file shaped like this:

```json
{
  "automation_id_prefix": "garden_valve",
  "alias_prefix": "Garden Valve",
  "entity_id": "switch.sonoff_water_valve",
  "timezone": "Asia/Bangkok",
  "schedules": [
    {
      "name": "morning",
      "time": "06:00",
      "duration_minutes": 10,
      "weekdays": ["mon", "wed", "fri"],
      "enabled": true
    }
  ]
}
```

Notes:

- `timezone` is documented for operators; Home Assistant uses its own configured timezone.
- `weekdays` is optional. Omit it to run every day.
- `enabled: false` skips generating that automation.

## Recommended Home Assistant entity

Most SONOFF water valves exposed to Home Assistant behave like a switch entity. If your device uses a different domain, update the `entity_id` accordingly. The generator derives the service domain from the entity prefix, so `switch.sonoff_water_valve` maps to `switch.turn_on` and `switch.turn_off`.
