"""The Voice Satellite Card LLM Tools integration."""

import logging
from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import ADDON_NAME, DOMAIN, WEATHER_ICONS_PATH
from .llm_api import cleanup_llm_api, setup_llm_api

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the Voice Satellite Card LLM Tools integration."""
    hass.data.setdefault(DOMAIN, {"cache": {}, "entries": {}})

    icons_dir = str(Path(__file__).parent / "weather_icons")
    await hass.http.async_register_static_paths(
        [StaticPathConfig(WEATHER_ICONS_PATH, icons_dir, cache_headers=True)]
    )

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Voice Satellite Card LLM Tools from a config entry."""
    _LOGGER.info("Setting up %s for entry: %s", ADDON_NAME, entry.entry_id)
    config = {**entry.data, **(entry.options or {})}
    await setup_llm_api(hass, config, entry.entry_id)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update by reloading the entry."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading %s for entry: %s", ADDON_NAME, entry.entry_id)
    await cleanup_llm_api(hass, entry.entry_id)
    return True
