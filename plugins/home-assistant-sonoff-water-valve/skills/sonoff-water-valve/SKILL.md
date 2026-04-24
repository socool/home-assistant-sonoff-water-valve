---
name: sonoff-water-valve
description: Generate or update a Home Assistant time-based watering schedule for a SONOFF water valve using this plugin's scripts and config files.
---

# SONOFF Water Valve

Use this skill when the user wants to:

- schedule a SONOFF water valve by time
- adjust watering duration or weekdays
- generate Home Assistant YAML from a simple JSON schedule
- test the valve through the Home Assistant REST API

## Workflow

1. Edit `config/example_schedule.json` or create a new schedule JSON file.
2. Run:

```bash
python3 scripts/generate_ha_package.py --input config/example_schedule.json --output output/sonoff_water_valve_package.yaml
```

3. Review the YAML under `output/`.
4. Tell the user to copy the generated package into Home Assistant and reload automations.

## API test

For a one-off run or connectivity check:

```bash
python3 scripts/trigger_ha_service.py \
  --ha-url http://homeassistant.local:8123 \
  --token YOUR_LONG_LIVED_TOKEN \
  --entity-id switch.sonoff_water_valve \
  --service turn_on \
  --duration-minutes 1
```

## Assumptions

- The valve is exposed in Home Assistant as an entity such as `switch.sonoff_water_valve`.
- Home Assistant already has a working SONOFF integration path.
- Time-based scheduling should be executed by Home Assistant automations, not by a long-running local process.
