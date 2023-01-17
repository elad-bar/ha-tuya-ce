"""Support for Tuya Smart devices."""
from __future__ import annotations

import logging

import requests
from tuya_iot import (
    AuthType,
    TuyaDeviceManager,
    TuyaHomeManager,
    TuyaOpenAPI,
    TuyaOpenMQ,
)

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import device_registry as dr, entity_registry as er
from homeassistant.helpers.entity_registry import RegistryEntry

from .helpers.const import (
    CONF_ACCESS_ID,
    CONF_ACCESS_SECRET,
    CONF_APP_TYPE,
    CONF_AUTH_TYPE,
    CONF_COUNTRY_CODE,
    CONF_ENDPOINT,
    CONF_PASSWORD,
    CONF_PROJECT_TYPE,
    CONF_USERNAME,
    DEVICE_CONFIG_MANAGER,
    DOMAIN,
    PLATFORMS,
    SERVICE_UPDATE_REMOTE_CONFIGURATION,
    TUYA_DISCOVERY_NEW,
    TUYA_HA_SIGNAL_UPDATE_ENTITY,
)
from .helpers.tuya_legacy_mapping import TUYA_LEGACY_CATEGORIES, TUYA_LEGACY_MAPPING
from .managers.tuya_configuration_manager import TuyaConfigurationManager
from .managers.tuya_device_listener import DeviceListener
from .models.ha_tuya_data import HomeAssistantTuyaData

_LOGGER = logging.getLogger(__package__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Async setup hass config entry."""
    hass.data.setdefault(DOMAIN, {})

    await TuyaConfigurationManager.load(hass)

    # Project type has been renamed to auth type in the upstream Tuya IoT SDK.
    # This migrates existing config entries to reflect that name change.
    if CONF_PROJECT_TYPE in entry.data:
        data = {**entry.data, CONF_AUTH_TYPE: entry.data[CONF_PROJECT_TYPE]}
        data.pop(CONF_PROJECT_TYPE)
        hass.config_entries.async_update_entry(entry, data=data)

    auth_type = AuthType(entry.data[CONF_AUTH_TYPE])
    api = TuyaOpenAPI(
        endpoint=entry.data[CONF_ENDPOINT],
        access_id=entry.data[CONF_ACCESS_ID],
        access_secret=entry.data[CONF_ACCESS_SECRET],
        auth_type=auth_type,
    )

    api.set_dev_channel("hass")

    try:
        if auth_type == AuthType.CUSTOM:
            response = await hass.async_add_executor_job(
                api.connect, entry.data[CONF_USERNAME], entry.data[CONF_PASSWORD]
            )
        else:
            response = await hass.async_add_executor_job(
                api.connect,
                entry.data[CONF_USERNAME],
                entry.data[CONF_PASSWORD],
                entry.data[CONF_COUNTRY_CODE],
                entry.data[CONF_APP_TYPE],
            )
    except requests.exceptions.RequestException as err:
        raise ConfigEntryNotReady(err) from err

    if response.get("success", False) is False:
        raise ConfigEntryNotReady(response)

    tuya_mq = TuyaOpenMQ(api)
    tuya_mq.start()

    device_ids: set[str] = set()
    device_manager = TuyaDeviceManager(api, tuya_mq)
    home_manager = TuyaHomeManager(api, tuya_mq, device_manager)
    listener = DeviceListener(hass, device_manager, device_ids)
    device_manager.add_device_listener(listener)

    hass.data[DOMAIN][entry.entry_id] = HomeAssistantTuyaData(
        device_listener=listener,
        device_manager=device_manager,
        home_manager=home_manager,
    )

    # Get devices & clean up device entities
    await hass.async_add_executor_job(home_manager.update_device_cache)
    await cleanup_device_registry(hass, device_manager)

    # Migrate old unique_ids to the new format
    async_migrate_entities_unique_ids(hass, entry, device_manager)

    # Register known device IDs
    device_registry = dr.async_get(hass)
    for device in device_manager.device_map.values():
        device_registry.async_get_or_create(
            config_entry_id=entry.entry_id,
            identifiers={(DOMAIN, device.id)},
            manufacturer="Tuya",
            name=device.name,
            model=f"{device.product_name} (unsupported)",
        )
        device_ids.add(device.id)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def cleanup_device_registry(
    hass: HomeAssistant, device_manager: TuyaDeviceManager
) -> None:
    """Remove deleted device registry entry if there are no remaining entities."""
    device_registry = dr.async_get(hass)
    for dev_id, device_entry in list(device_registry.devices.items()):
        for item in device_entry.identifiers:
            if DOMAIN == item[0] and item[1] not in device_manager.device_map:
                device_registry.async_remove_device(dev_id)
                break


@callback
def async_migrate_entities_unique_ids(
    hass: HomeAssistant, config_entry: ConfigEntry, device_manager: TuyaDeviceManager
) -> None:
    """Migrate unique_ids in the entity registry to the new format."""
    entity_registry = er.async_get(hass)
    registry_entries = er.async_entries_for_config_entry(entity_registry, config_entry.entry_id)

    entries = {
        entry.unique_id: entry
        for entry in registry_entries
        if entry.domain in TUYA_LEGACY_MAPPING
    }

    for device in device_manager.device_map.values():
        tuya_device_id = f"tuya.{device.id}"

        domain = TUYA_LEGACY_CATEGORIES.get(device.category)
        legacy_mapping = TUYA_LEGACY_MAPPING.get(domain, {})

        for key in legacy_mapping:
            dp_code = legacy_mapping.get(key)

            legacy_unique_id = f"{tuya_device_id}{key}"
            new_unique_id = f"{tuya_device_id}{dp_code}"

            entry: RegistryEntry | None = entries.get(legacy_unique_id)

            if entry is not None and new_unique_id not in entries:
                entity_registry.async_update_entity(entry.entity_id, new_unique_id=new_unique_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unloading the Tuya platforms."""
    unload = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload:
        hass_data: HomeAssistantTuyaData = hass.data[DOMAIN][entry.entry_id]
        hass_data.device_manager.mq.stop()
        hass_data.device_manager.remove_device_listener(hass_data.device_listener)

        hass.data[DOMAIN].pop(entry.entry_id)
        if not hass.data[DOMAIN]:
            hass.data.pop(DOMAIN)

    return unload
