"""LLM API registration for search services."""

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .brave_image_search import BraveImageSearchTool
from .brave_web_search import BraveWebSearchTool
from .const import (
    CONF_DAILY_WEATHER_ENTITY,
    CONF_FINANCIAL_PROVIDER,
    CONF_FINANCIAL_PROVIDER_FINNHUB,
    CONF_FINNHUB_API_KEY,
    CONF_IMAGE_SEARCH_PROVIDER,
    CONF_IMAGE_SEARCH_PROVIDER_BRAVE,
    CONF_IMAGE_SEARCH_PROVIDER_SEARXNG,
    CONF_TOOL_TYPE,
    CONF_WEB_SEARCH_PROVIDER,
    CONF_WEB_SEARCH_PROVIDER_BRAVE,
    CONF_WEB_SEARCH_PROVIDER_SEARXNG,
    CONF_YOUTUBE_API_KEY,
    DOMAIN,
    FINANCIAL_API_ID,
    FINANCIAL_API_NAME,
    FINANCIAL_SERVICES_PROMPT,
    IMAGE_SEARCH_API_ID,
    IMAGE_SEARCH_API_NAME,
    IMAGE_SEARCH_SERVICES_PROMPT,
    TOOL_TYPE_FINANCIAL,
    TOOL_TYPE_IMAGE_SEARCH,
    TOOL_TYPE_VIDEO_SEARCH,
    TOOL_TYPE_WEATHER,
    TOOL_TYPE_WEB_SEARCH,
    TOOL_TYPE_WIKIPEDIA,
    VIDEO_SEARCH_API_ID,
    VIDEO_SEARCH_API_NAME,
    VIDEO_SEARCH_SERVICES_PROMPT,
    WEATHER_API_ID,
    WEATHER_API_NAME,
    WEATHER_SERVICES_PROMPT,
    WEB_SEARCH_API_ID,
    WEB_SEARCH_API_NAME,
    WEB_SEARCH_SERVICES_PROMPT,
    WIKIPEDIA_API_ID,
    WIKIPEDIA_API_NAME,
    WIKIPEDIA_SERVICES_PROMPT,
)
from .finnhub_financial import FinnhubFinancialTool
from .searxng_image_search import SearXNGImageSearchTool
from .searxng_web_search import SearXNGWebSearchTool
from .weather_forecast import WeatherForecastTool
from .wikipedia_web_search import WikipediaWebSearchTool
from .youtube_video_search import YouTubeVideoSearchTool

_LOGGER = logging.getLogger(__name__)

# Maps a condition (lambda on config data) to a tool class
IMAGE_SEARCH_TOOLS_MAP = [
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

WEB_SEARCH_TOOLS_MAP = [
    (
        lambda data: data.get(CONF_WEB_SEARCH_PROVIDER)
        == CONF_WEB_SEARCH_PROVIDER_BRAVE,
        BraveWebSearchTool,
    ),
    (
        lambda data: data.get(CONF_WEB_SEARCH_PROVIDER)
        == CONF_WEB_SEARCH_PROVIDER_SEARXNG,
        SearXNGWebSearchTool,
    ),
]

FINANCIAL_TOOLS_MAP = [
    (
        lambda data: data.get(CONF_FINANCIAL_PROVIDER)
        == CONF_FINANCIAL_PROVIDER_FINNHUB,
        FinnhubFinancialTool,
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


class WebSearchAPI(llm.API):
    """Web Search API for LLM integration."""

    def __init__(self, hass: HomeAssistant, config_data: dict[str, Any]) -> None:
        """Initialize the Web Search API."""
        super().__init__(
            hass=hass,
            id=WEB_SEARCH_API_ID,
            name=WEB_SEARCH_API_NAME,
        )
        self._config_data = config_data

    def get_enabled_tools(self) -> list:
        """Return list of tool instances for the configured provider."""
        tools = []
        for condition, tool_class in WEB_SEARCH_TOOLS_MAP:
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
            api_prompt=WEB_SEARCH_SERVICES_PROMPT,
            llm_context=llm_context,
            tools=tools,
        )


class WikipediaSearchAPI(llm.API):
    """Wikipedia Search API for LLM integration."""

    def __init__(self, hass: HomeAssistant, config_data: dict[str, Any]) -> None:
        """Initialize the Wikipedia Search API."""
        super().__init__(
            hass=hass,
            id=WIKIPEDIA_API_ID,
            name=WIKIPEDIA_API_NAME,
        )
        self._config_data = config_data

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        """Return an API instance with the Wikipedia search tool."""
        tools = [WikipediaWebSearchTool(self._config_data, self.hass)]
        return llm.APIInstance(
            api=self,
            api_prompt=WIKIPEDIA_SERVICES_PROMPT,
            llm_context=llm_context,
            tools=tools,
        )


class WeatherForecastAPI(llm.API):
    """Weather Forecast API for LLM integration."""

    def __init__(self, hass: HomeAssistant, config_data: dict[str, Any]) -> None:
        """Initialize the Weather Forecast API."""
        super().__init__(
            hass=hass,
            id=WEATHER_API_ID,
            name=WEATHER_API_NAME,
        )
        self._config_data = config_data

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        """Return an API instance with the weather forecast tool."""
        tools = [WeatherForecastTool(self._config_data, self.hass)]
        return llm.APIInstance(
            api=self,
            api_prompt=WEATHER_SERVICES_PROMPT,
            llm_context=llm_context,
            tools=tools,
        )


class FinancialDataAPI(llm.API):
    """Financial Data API for LLM integration."""

    def __init__(self, hass: HomeAssistant, config_data: dict[str, Any]) -> None:
        """Initialize the Financial Data API."""
        super().__init__(
            hass=hass,
            id=FINANCIAL_API_ID,
            name=FINANCIAL_API_NAME,
        )
        self._config_data = config_data

    def get_enabled_tools(self) -> list:
        """Return list of tool instances for the configured provider."""
        tools = []
        for condition, tool_class in FINANCIAL_TOOLS_MAP:
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
            api_prompt=FINANCIAL_SERVICES_PROMPT,
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

    elif tool_type == TOOL_TYPE_WEB_SEARCH:
        api = WebSearchAPI(hass, config_data)
        if api.get_enabled_tools():
            unreg = llm.async_register_api(hass, api)
            hass.data[DOMAIN]["entries"][entry_id] = {
                "config": config_data.copy(),
                "unregister_api": unreg,
            }
            _LOGGER.info("Registered LLM API: %s", WEB_SEARCH_API_NAME)
        else:
            _LOGGER.warning(
                "No web search provider enabled, LLM API not registered"
            )

    elif tool_type == TOOL_TYPE_WIKIPEDIA:
        api = WikipediaSearchAPI(hass, config_data)
        unreg = llm.async_register_api(hass, api)
        hass.data[DOMAIN]["entries"][entry_id] = {
            "config": config_data.copy(),
            "unregister_api": unreg,
        }
        _LOGGER.info("Registered LLM API: %s", WIKIPEDIA_API_NAME)

    elif tool_type == TOOL_TYPE_WEATHER:
        api = WeatherForecastAPI(hass, config_data)
        if config_data.get(CONF_DAILY_WEATHER_ENTITY):
            unreg = llm.async_register_api(hass, api)
            hass.data[DOMAIN]["entries"][entry_id] = {
                "config": config_data.copy(),
                "unregister_api": unreg,
            }
            _LOGGER.info("Registered LLM API: %s", WEATHER_API_NAME)
        else:
            _LOGGER.warning(
                "Daily weather entity not configured, Weather API not registered"
            )

    elif tool_type == TOOL_TYPE_FINANCIAL:
        api = FinancialDataAPI(hass, config_data)
        if api.get_enabled_tools():
            unreg = llm.async_register_api(hass, api)
            hass.data[DOMAIN]["entries"][entry_id] = {
                "config": config_data.copy(),
                "unregister_api": unreg,
            }
            _LOGGER.info("Registered LLM API: %s", FINANCIAL_API_NAME)
        else:
            _LOGGER.warning(
                "No financial data provider enabled, LLM API not registered"
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
