"""LLM API registration for Voice Satellite tools."""

import logging
from collections.abc import Callable
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .brave_image_search import BraveImageSearchTool
from .brave_web_search import BraveWebSearchTool
from .const import (
    CALENDAR_API_ID,
    CALENDAR_API_NAME,
    CALENDAR_SERVICES_PROMPT,
    CONF_CALENDAR_ENTITIES,
    CONF_DAILY_WEATHER_ENTITY,
    CONF_FINANCIAL_PROVIDER,
    CONF_FINANCIAL_PROVIDER_FINNHUB,
    CONF_FINNHUB_API_KEY,
    CONF_IMAGE_SEARCH_PROVIDER,
    CONF_IMAGE_SEARCH_PROVIDER_BRAVE,
    CONF_IMAGE_SEARCH_PROVIDER_SEARXNG,
    CONF_NEWSAPI_KEY,
    CONF_SPORTS_LEAGUES,
    CONF_TODO_ENTITIES,
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
    NEWS_API_ID,
    NEWS_API_NAME,
    NEWS_SERVICES_PROMPT,
    SPORTS_API_ID,
    SPORTS_API_NAME,
    SPORTS_SERVICES_PROMPT,
    TODO_API_ID,
    TODO_API_NAME,
    TODO_SERVICES_PROMPT,
    TOOL_TYPE_CALENDAR,
    TOOL_TYPE_FINANCIAL,
    TOOL_TYPE_IMAGE_SEARCH,
    TOOL_TYPE_NEWS,
    TOOL_TYPE_SPORTS,
    TOOL_TYPE_TODO,
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
from .ha_calendar import HACalendarTool
from .ha_todo import HATodoTool
from .newsapi_news import NewsAPINewsTool
from .searxng_image_search import SearXNGImageSearchTool
from .searxng_web_search import SearXNGWebSearchTool
from .sports_scores import SportsScoresTool
from .weather_forecast import WeatherForecastTool
from .wikipedia_web_search import WikipediaWebSearchTool
from .youtube_video_search import YouTubeVideoSearchTool

_LOGGER = logging.getLogger(__name__)

_ToolsFactory = Callable[[dict[str, Any], HomeAssistant], list[llm.Tool]]

# Maps provider config values to tool classes for image/web/financial search
_IMAGE_SEARCH_MAP: list[tuple[Callable, type]] = [
    (lambda d: d.get(CONF_IMAGE_SEARCH_PROVIDER) == CONF_IMAGE_SEARCH_PROVIDER_BRAVE, BraveImageSearchTool),
    (lambda d: d.get(CONF_IMAGE_SEARCH_PROVIDER) == CONF_IMAGE_SEARCH_PROVIDER_SEARXNG, SearXNGImageSearchTool),
]

_WEB_SEARCH_MAP: list[tuple[Callable, type]] = [
    (lambda d: d.get(CONF_WEB_SEARCH_PROVIDER) == CONF_WEB_SEARCH_PROVIDER_BRAVE, BraveWebSearchTool),
    (lambda d: d.get(CONF_WEB_SEARCH_PROVIDER) == CONF_WEB_SEARCH_PROVIDER_SEARXNG, SearXNGWebSearchTool),
]

_FINANCIAL_MAP: list[tuple[Callable, type]] = [
    (lambda d: d.get(CONF_FINANCIAL_PROVIDER) == CONF_FINANCIAL_PROVIDER_FINNHUB, FinnhubFinancialTool),
]


def _from_map(tools_map: list[tuple[Callable, type]]) -> _ToolsFactory:
    def factory(cfg: dict, hass: HomeAssistant) -> list[llm.Tool]:
        return [cls(cfg, hass) for cond, cls in tools_map if cond(cfg)]
    return factory


def _single(tool_class: type) -> _ToolsFactory:
    def factory(cfg: dict, hass: HomeAssistant) -> list[llm.Tool]:
        return [tool_class(cfg, hass)]
    return factory


def _conditional(tool_class: type, check_key: str) -> _ToolsFactory:
    def factory(cfg: dict, hass: HomeAssistant) -> list[llm.Tool]:
        return [tool_class(cfg, hass)] if cfg.get(check_key) else []
    return factory


class GenericToolAPI(llm.API):
    """Generic LLM API that wraps an arbitrary set of tools."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_data: dict[str, Any],
        api_id: str,
        api_name: str,
        prompt: str,
        tools_factory: _ToolsFactory,
    ) -> None:
        super().__init__(hass=hass, id=api_id, name=api_name)
        self._config_data = config_data
        self._prompt = prompt
        self._tools_factory = tools_factory

    async def async_get_api_instance(
        self, llm_context: llm.LLMContext
    ) -> llm.APIInstance:
        tools = self._tools_factory(self._config_data, self.hass)
        return llm.APIInstance(
            api=self,
            api_prompt=self._prompt,
            llm_context=llm_context,
            tools=tools,
        )


# Registry: tool_type -> registration descriptor
# ready_check(cfg) -> bool: whether this tool is properly configured
# warn: logged when ready_check fails and the API is skipped
_REGISTRY: dict[str, dict] = {
    TOOL_TYPE_IMAGE_SEARCH: {
        "api_id": IMAGE_SEARCH_API_ID,
        "api_name": IMAGE_SEARCH_API_NAME,
        "prompt": IMAGE_SEARCH_SERVICES_PROMPT,
        "factory": _from_map(_IMAGE_SEARCH_MAP),
        "ready_check": lambda cfg: any(cond(cfg) for cond, _ in _IMAGE_SEARCH_MAP),
        "warn": "No image search provider enabled, LLM API not registered",
    },
    TOOL_TYPE_VIDEO_SEARCH: {
        "api_id": VIDEO_SEARCH_API_ID,
        "api_name": VIDEO_SEARCH_API_NAME,
        "prompt": VIDEO_SEARCH_SERVICES_PROMPT,
        "factory": _conditional(YouTubeVideoSearchTool, CONF_YOUTUBE_API_KEY),
        "ready_check": lambda cfg: bool(cfg.get(CONF_YOUTUBE_API_KEY)),
        "warn": "YouTube API key not configured, Video Search API not registered",
    },
    TOOL_TYPE_WEB_SEARCH: {
        "api_id": WEB_SEARCH_API_ID,
        "api_name": WEB_SEARCH_API_NAME,
        "prompt": WEB_SEARCH_SERVICES_PROMPT,
        "factory": _from_map(_WEB_SEARCH_MAP),
        "ready_check": lambda cfg: any(cond(cfg) for cond, _ in _WEB_SEARCH_MAP),
        "warn": "No web search provider enabled, LLM API not registered",
    },
    TOOL_TYPE_WIKIPEDIA: {
        "api_id": WIKIPEDIA_API_ID,
        "api_name": WIKIPEDIA_API_NAME,
        "prompt": WIKIPEDIA_SERVICES_PROMPT,
        "factory": _single(WikipediaWebSearchTool),
    },
    TOOL_TYPE_WEATHER: {
        "api_id": WEATHER_API_ID,
        "api_name": WEATHER_API_NAME,
        "prompt": WEATHER_SERVICES_PROMPT,
        "factory": _conditional(WeatherForecastTool, CONF_DAILY_WEATHER_ENTITY),
        "ready_check": lambda cfg: bool(cfg.get(CONF_DAILY_WEATHER_ENTITY)),
        "warn": "Daily weather entity not configured, Weather API not registered",
    },
    TOOL_TYPE_FINANCIAL: {
        "api_id": FINANCIAL_API_ID,
        "api_name": FINANCIAL_API_NAME,
        "prompt": FINANCIAL_SERVICES_PROMPT,
        "factory": _from_map(_FINANCIAL_MAP),
        "ready_check": lambda cfg: any(cond(cfg) for cond, _ in _FINANCIAL_MAP),
        "warn": "No financial data provider enabled, LLM API not registered",
    },
    TOOL_TYPE_NEWS: {
        "api_id": NEWS_API_ID,
        "api_name": NEWS_API_NAME,
        "prompt": NEWS_SERVICES_PROMPT,
        "factory": _conditional(NewsAPINewsTool, CONF_NEWSAPI_KEY),
        "ready_check": lambda cfg: bool(cfg.get(CONF_NEWSAPI_KEY)),
        "warn": "NewsAPI key not configured, News Headlines API not registered",
    },
    TOOL_TYPE_CALENDAR: {
        "api_id": CALENDAR_API_ID,
        "api_name": CALENDAR_API_NAME,
        "prompt": CALENDAR_SERVICES_PROMPT,
        "factory": _single(HACalendarTool),
        "ready_check": lambda cfg: bool(cfg.get(CONF_CALENDAR_ENTITIES)),
        "warn": "No calendar entities configured, Calendar API not registered",
    },
    TOOL_TYPE_TODO: {
        "api_id": TODO_API_ID,
        "api_name": TODO_API_NAME,
        "prompt": TODO_SERVICES_PROMPT,
        "factory": _single(HATodoTool),
        "ready_check": lambda cfg: bool(cfg.get(CONF_TODO_ENTITIES)),
        "warn": "No to-do list entities configured, To-do API not registered",
    },
    TOOL_TYPE_SPORTS: {
        "api_id": SPORTS_API_ID,
        "api_name": SPORTS_API_NAME,
        "prompt": SPORTS_SERVICES_PROMPT,
        "factory": _single(SportsScoresTool),
    },
}


async def setup_llm_api(
    hass: HomeAssistant, config_data: dict[str, Any], entry_id: str
) -> None:
    """Register the LLM API for a config entry."""
    hass.data.setdefault(DOMAIN, {"cache": {}, "entries": {}})

    tool_type = config_data.get(CONF_TOOL_TYPE)
    descriptor = _REGISTRY.get(tool_type)

    if descriptor is None:
        _LOGGER.error("Unknown tool type: %s", tool_type)
        return

    ready_check = descriptor.get("ready_check")
    if ready_check and not ready_check(config_data):
        warn = descriptor.get("warn")
        if warn:
            _LOGGER.warning(warn)
        return

    api = GenericToolAPI(
        hass=hass,
        config_data=config_data,
        api_id=descriptor["api_id"],
        api_name=descriptor["api_name"],
        prompt=descriptor["prompt"],
        tools_factory=descriptor["factory"],
    )

    unreg = llm.async_register_api(hass, api)
    hass.data[DOMAIN]["entries"][entry_id] = {
        "config": config_data.copy(),
        "unregister_api": unreg,
    }
    _LOGGER.info("Registered LLM API: %s", descriptor["api_name"])


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

    if not hass.data[DOMAIN].get("entries"):
        hass.data.pop(DOMAIN, None)
