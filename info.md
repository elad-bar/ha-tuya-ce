# EdgeOS

## Description

[Changelog](https://github.com/elad-bar/ha-tuya-dynamic/blob/master/CHANGELOG.md)

## How to

#### Requirements


#### Installations via HACS
- In HACS, look for "Tuya Dynamic" and install and restart
- In Settings  --> Devices & Services - (Lower Right) "Add Integration"

#### Setup

To add integration use Configuration -> Integrations -> Add `Duya Dunamic`
Integration supports **multiple** EdgeOS devices

| Fields name | Type | Required | Default | Description |
|-------------|------|----------|---------|-------------|
| -           | *    | +        | -       | *           |

#### Debugging

To set the log level of the component to DEBUG, please set it from the options of the component if installed, otherwise, set it within configuration YAML of HA:

```yaml
logger:
  default: warning
  logs:
    custom_components.tuya_dynamic: debug
```
