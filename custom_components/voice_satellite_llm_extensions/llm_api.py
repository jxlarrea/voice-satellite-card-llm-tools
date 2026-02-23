"""LLM API registration for image search services."""

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .brave_image_search import BraveImageSearchTool
from .const import (
    CONF_IMAGE_SEARCH_PROVIDER,
    CONF_IMAGE_SEARCH_PROVIDER_BRAVE,
    CONF_IMAGE_SEARCH_PROVIDER_GOOGLE,
    CONF_IMAGE_SEARCH_PROVIDER_SEARXNG,
    DOMAIN,
    IMAGE_SEARCH_API_ID,
    IMAGE_SEARCH_API_NAME,
    IMAGE_SEARCH_SERVICES_PROMPT,
)
from .google_image_search import GoogleImageSearchTool
from .searxng_image_search import SearXNGImageSearchTool

_LOGGER = logging.getLogger(__name__)

# Maps a condition (lambda on config data) to a tool class
IMAGE_SEARCH_TOOLS_MAP = [
    (
        lambda data: data.get(CONF_IMAGE_SEARCH_PROVIDER)
        == CONF_IMAGE_SEARCH_PROVIDER_GOOGLE,
        GoogleImageSearchTool,
    ),
    (
        lambda data: data.get(CONF_IMAGE_SEARCH_PROVIDER)
        == CONF_IMAGE_SEARCH_PROVIDER_BRAVE,
        BraveImageSearchTool,
    ),
    (
        lambda data: data.get(CONF_IMAGE_SEARCH_PROVIDER)
        == CONF_IMAGE_SEARCH_PROVIDER_SEARXNG,
        SearXNGImageSearchTool,
    ),
]


class ImageSearchAPI(llm.API):
    """Image Search API for LLM integration."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the Image Search API."""
        super().__init__(
            hass=hass,
            id=IMAGE_SEARCH_API_ID,
            name=IMAGE_SEARCH_API_NAME,
        )

    def get_enabled_tools(self) -> list:
        """Return list of tool instances for the configured provider."""
        config_data = self.hass.data.get(DOMAIN, {}).get("config", {})
        tools = []

        for condition, tool_class in IMAGE_SEARCH_TOOLS_MAP:
            enabled = False
            if callable(condition):
                enabled = condition(config_data)

            if enabled:
                tools.append(tool_class(config_data, self.hass))

        return tools

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        """Return an API instance with enabled tools."""
        tools = self.get_enabled_tools()
        return llm.APIInstance(
            api=self,
            api_prompt=IMAGE_SEARCH_SERVICES_PROMPT,
            llm_context=llm_context,
            tools=tools,
        )


async def setup_llm_api(hass: HomeAssistant, config_data: dict[str, Any]) -> None:
    """Register the image search API with HA's LLM system."""
    if (
        DOMAIN in hass.data
        and "api" in hass.data[DOMAIN]
        and hass.data[DOMAIN].get("config") == config_data
    ):
        return

    if DOMAIN in hass.data and "api" in hass.data[DOMAIN]:
        await cleanup_llm_api(hass)

    hass.data.setdefault(DOMAIN, {})
    api = ImageSearchAPI(hass)

    hass.data[DOMAIN]["api"] = api
    hass.data[DOMAIN]["config"] = config_data.copy()
    hass.data[DOMAIN]["unregister_api"] = []

    if api.get_enabled_tools():
        hass.data[DOMAIN]["unregister_api"].append(
            llm.async_register_api(hass, api)
        )
        _LOGGER.info("Registered LLM API: %s", IMAGE_SEARCH_API_NAME)
    else:
        _LOGGER.warning("No image search provider enabled, LLM API not registered")


async def cleanup_llm_api(hass: HomeAssistant) -> None:
    """Unregister and clean up."""
    if DOMAIN not in hass.data:
        return

    for unreg_func in hass.data[DOMAIN].get("unregister_api", []):
        try:
            unreg_func()
        except Exception as e:
            _LOGGER.debug("Error unregistering LLM API: %s", e)

    hass.data.pop(DOMAIN, None)
