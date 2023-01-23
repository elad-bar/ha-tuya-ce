# Tuya CE

## Description

Fork of the original Tuya integration support devices settings over JSON file instead of code for faster adoption of new devices

## How to

### Installations via HACS

- Add as custom repository
- look for "Tuya CE" and install and restart
- In Settings  --> Devices & Services - (Lower Right) "Add Integration"

### Setup

To add integration use Configuration -> Integrations -> Add `Tuya CE`
Add details as described in the [original integration page in HA](https://www.home-assistant.io/integrations/tuya/)

### Add unsupported devices

Follow the following [manual](SUPPORT_NEW_DEVICES.md)

### Debugging

To set the log level of the component to DEBUG, please set it from the options of the component if installed, otherwise, set it within configuration YAML of HA:

```yaml
logger:
  default: warning
  logs:
    custom_components.tuya_ce: debug
```
