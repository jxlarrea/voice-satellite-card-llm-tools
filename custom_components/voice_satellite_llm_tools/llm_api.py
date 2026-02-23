"""LLM API registration for search services."""

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
    CONF_TOOL_TYPE,
    CONF_YOUTUBE_API_KEY,
    DOMAIN,
    IMAGE_SEARCH_API_ID,
    IMAGE_SEARCH_API_NAME,
    IMAGE_SEARCH_SERVICES_PROMPT,
    TOOL_TYPE_IMAGE_SEARCH,
    TOOL_TYPE_VIDEO_SEARCH,
    VIDEO_SEARCH_API_ID,
    VIDEO_SEARCH_API_NAME,
    VIDEO_SEARCH_SERVICES_PROMPT,
)
from .google_image_search import GoogleImageSearchTool
from .searxng_image_search import SearXNGImageSearchTool
from .youtube_video_search import YouTubeVideoSearchTool

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

    def __init__(self, hass: HomeAssistant, config_data: dict[str, Any]) -> None:
        """Initialize the Image Search API."""
        super().__init__(
            hass=hass,
            id=IMAGE_SEARCH_API_ID,
            name=IMAGE_SEARCH_API_NAME,
        )
        self._config_data = config_data

    def get_enabled_tools(self) -> list:
        """Return list of tool instances for the configured provider."""
        tools = []
        for condition, tool_class in IMAGE_SEARCH_TOOLS_MAP:
            if callable(condition) and condition(self._config_data):
                tools.append(tool_class(self._config_data, self.hass))
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


class VideoSearchAPI(llm.API):
    """Video Search API for LLM integration."""

    def __init__(self, hass: HomeAssistant, config_data: dict[str, Any]) -> None:
        """Initialize the Video Search API."""
        super().__init__(
            hass=hass,
            id=VIDEO_SEARCH_API_ID,
            name=VIDEO_SEARCH_API_NAME,
        )
        self._config_data = config_data

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        """Return an API instance with the YouTube video search tool."""
        tools = []
        if self._config_data.get(CONF_YOUTUBE_API_KEY):
            tools.append(YouTubeVideoSearchTool(self._config_data, self.hass))

        return llm.APIInstance(
            api=self,
            api_prompt=VIDEO_SEARCH_SERVICES_PROMPT,
            llm_context=llm_context,
            tools=tools,
        )


async def setup_llm_api(
    hass: HomeAssistant, config_data: dict[str, Any], entry_id: str
) -> None:
    """Register a search API for a specific config entry."""
    hass.data.setdefault(DOMAIN, {"cache": {}, "entries": {}})

    tool_type = config_data.get(CONF_TOOL_TYPE)

    if tool_type == TOOL_TYPE_IMAGE_SEARCH:
        api = ImageSearchAPI(hass, config_data)
        if api.get_enabled_tools():
            unreg = llm.async_register_api(hass, api)
            hass.data[DOMAIN]["entries"][entry_id] = {
                "config": config_data.copy(),
                "unregister_api": unreg,
            }
            _LOGGER.info("Registered LLM API: %s", IMAGE_SEARCH_API_NAME)
        else:
            _LOGGER.warning(
                "No image search provider enabled, LLM API not registered"
            )

    elif tool_type == TOOL_TYPE_VIDEO_SEARCH:
        api = VideoSearchAPI(hass, config_data)
        if config_data.get(CONF_YOUTUBE_API_KEY):
            unreg = llm.async_register_api(hass, api)
            hass.data[DOMAIN]["entries"][entry_id] = {
                "config": config_data.copy(),
                "unregister_api": unreg,
            }
            _LOGGER.info("Registered LLM API: %s", VIDEO_SEARCH_API_NAME)
        else:
            _LOGGER.warning(
                "YouTube API key not configured, Video Search API not registered"
            )


async def cleanup_llm_api(hass: HomeAssistant, entry_id: str) -> None:
    """Unregister a specific entry's API."""
    if DOMAIN not in hass.data:
        return

    entry_data = hass.data[DOMAIN].get("entries", {}).pop(entry_id, None)
    if entry_data:
        unreg = entry_data.get("unregister_api")
        if unreg:
            try:
                unreg()
            except Exception as e:
                _LOGGER.debug("Error unregistering LLM API: %s", e)

    # Clean up domain data when last entry is removed
    if not hass.data[DOMAIN].get("entries"):
        hass.data.pop(DOMAIN, None)
