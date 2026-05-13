"""Wikipedia Search tool."""

import hashlib
import json
import logging
import time
from urllib.parse import quote

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .base_tool import BaseTool
from .const import (
    CONF_CACHE_TTL,
    CONF_WIKIPEDIA_DETAIL,
    DEFAULT_CACHE_TTL,
    DOMAIN,
    WIKIPEDIA_DETAIL_DETAILED,
)
from .http_helpers import fetch_json

_LOGGER = logging.getLogger(__name__)

WIKIPEDIA_SEARCH_URL = "https://en.wikipedia.org/w/api.php"
WIKIPEDIA_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary"
USER_AGENT = "HomeAssistant VoiceSatelliteCard/1.0"


class WikipediaWebSearchTool(BaseTool):
    """Search Wikipedia for encyclopedic information."""

    source = "wikipedia"
    name = "search_wikipedia"
    description = (
        "Look up a topic on Wikipedia. Returns the most relevant article's "
        "summary and thumbnail. Use when the user asks about a topic, person, "
        "place, event, or concept."
    )

    parameters = vol.Schema(
        {
            vol.Required("query", description="The Wikipedia search query"): str,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        query = tool_input.tool_args["query"]
        _LOGGER.info("Wikipedia search requested: query='%s'", query)

        try:
            cache_key = self._make_cache_key(query)
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

            search_data = await fetch_json(
                self.hass,
                WIKIPEDIA_SEARCH_URL,
                params={
                    "action": "query",
                    "list": "search",
                    "srsearch": query,
                    "srlimit": 3,
                    "format": "json",
                },
                headers={"User-Agent": USER_AGENT},
            )

            search_results = search_data.get("query", {}).get("search", [])
            if not search_results:
                return {
                    "source": "wikipedia",
                    "query": query,
                    "message": "No Wikipedia article found for this query.",
                }

            summary = await self._fetch_best_summary(
                [item["title"] for item in search_results]
            )

            if summary is None:
                return {
                    "source": "wikipedia",
                    "query": query,
                    "message": "No Wikipedia article found for this query.",
                }

            thumbnail = summary.get("thumbnail", {})
            thumbnail_url = thumbnail.get("source", "") if thumbnail else ""
            article_url = (
                summary.get("content_urls", {}).get("desktop", {}).get("page", "")
            )
            title = summary.get("title", "")

            detailed = self.config.get(CONF_WIKIPEDIA_DETAIL) == WIKIPEDIA_DETAIL_DETAILED
            if detailed:
                extract = await self._fetch_full_intro(title)
                if not extract:
                    extract = summary.get("extract", "")
            else:
                extract = summary.get("extract", "")

            response = {
                "source": "wikipedia",
                "query": query,
                "title": title,
                "url": article_url,
                "summary": extract,
                "featured_image": thumbnail_url if thumbnail_url else None,
                "instruction": (
                    "Relay the key information from this Wikipedia article in a concise, "
                    "conversational way. Do NOT mention Wikipedia, the URL, or that this "
                    "came from an article — just share the knowledge naturally."
                ),
            }

            self._cache_set(cache_key, response)
            return response

        except Exception as e:
            _LOGGER.exception("Error during Wikipedia search for '%s': %s", query, e)
            return {"error": f"Wikipedia search failed: {e!s}"}

    async def _fetch_best_summary(self, titles: list[str]) -> dict | None:
        for title in titles:
            encoded_title = quote(title.replace(" ", "_"), safe="")
            url = f"{WIKIPEDIA_SUMMARY_URL}/{encoded_title}"
            try:
                data = await fetch_json(
                    self.hass,
                    url,
                    headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
                )
                if data.get("type") == "disambiguation":
                    continue
                return data
            except Exception as e:
                _LOGGER.debug("Wikipedia summary for '%s' failed: %s", title, e)
                continue
        return None

    async def _fetch_full_intro(self, title: str) -> str | None:
        try:
            data = await fetch_json(
                self.hass,
                WIKIPEDIA_SEARCH_URL,
                params={
                    "action": "query",
                    "titles": title,
                    "prop": "extracts",
                    "exintro": "",
                    "explaintext": "",
                    "format": "json",
                },
                headers={"User-Agent": USER_AGENT},
            )
            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                extract = page.get("extract", "")
                if extract:
                    return extract
        except Exception as e:
            _LOGGER.debug("Error fetching full intro for '%s': %s", title, e)
        return None

    def _make_cache_key(self, query: str) -> str:
        detail = self.config.get(CONF_WIKIPEDIA_DETAIL, "concise")
        raw = json.dumps(
            {"type": "wikipedia", "q": query.lower().strip(), "d": detail},
            sort_keys=True,
        )
        return hashlib.md5(raw.encode()).hexdigest()

    def _cache_get(self, key: str) -> dict | None:
        cache = self.hass.data.get(DOMAIN, {}).get("cache", {})
        entry = cache.get(key)
        if entry is None:
            return None
        ttl = int(self.config.get(CONF_CACHE_TTL, DEFAULT_CACHE_TTL))
        if time.time() - entry["ts"] > ttl:
            cache.pop(key, None)
            return None
        _LOGGER.debug("Wikipedia cache hit for key %s", key)
        return entry["data"]

    def _cache_set(self, key: str, data: dict) -> None:
        cache = self.hass.data.setdefault(DOMAIN, {}).setdefault("cache", {})
        cache[key] = {"ts": time.time(), "data": data}
