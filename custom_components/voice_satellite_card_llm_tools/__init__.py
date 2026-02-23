"""The LLM Extensions integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv

from .const import ADDON_NAME, DOMAIN
from .llm_api import cleanup_llm_api, setup_llm_api

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up the LLM Extensions integration."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up LLM Extensions from a config entry."""
    _LOGGER.info("Setting up %s for entry: %s", ADDON_NAME, entry.entry_id)
    config = {**entry.data, **(entry.options or {})}
    await setup_llm_api(hass, config)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.info("Unloading %s for entry: %s", ADDON_NAME, entry.entry_id)
    await cleanup_llm_api(hass)
    return True
