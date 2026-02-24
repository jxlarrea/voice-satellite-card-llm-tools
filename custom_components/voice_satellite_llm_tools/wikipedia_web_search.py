"""Wikipedia Search tool."""

import hashlib
import json
import logging
import time
from urllib.parse import quote

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .base_tool import BaseTool
from .const import (
    CONF_CACHE_TTL,
    CONF_WIKIPEDIA_DETAIL,
    DEFAULT_CACHE_TTL,
    DOMAIN,
    WIKIPEDIA_DETAIL_DETAILED,
)

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
        """Search Wikipedia and return the best matching article."""
        query = tool_input.tool_args["query"]

        _LOGGER.info("Wikipedia search requested: query='%s'", query)

        try:
            # Check cache
            cache_key = self._make_cache_key(query)
            cached = self._cache_get(cache_key)
            if cached is not None:
                return cached

            session = async_get_clientsession(self.hass)

            # Step 1: Search for the best matching article
            search_params = {
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": 3,
                "format": "json",
            }

            async with session.get(
                WIKIPEDIA_SEARCH_URL,
                params=search_params,
                headers={"User-Agent": USER_AGENT},
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise RuntimeError(
                        f"Wikipedia Search API returned HTTP {resp.status}: {error_text}"
                    )
                search_data = await resp.json()

            search_results = search_data.get("query", {}).get("search", [])
            if not search_results:
                return {
                    "source": "wikipedia",
                    "query": query,
                    "message": "No Wikipedia article found for this query.",
                }

            # Step 2: Fetch summaries for top results, take first non-disambiguation
            summary = await self._fetch_best_summary(
                session, [item["title"] for item in search_results]
            )

            if summary is None:
                return {
                    "source": "wikipedia",
                    "query": query,
                    "message": "No Wikipedia article found for this query.",
                }

            # Step 3: Build response
            thumbnail = summary.get("thumbnail", {})
            thumbnail_url = thumbnail.get("source", "") if thumbnail else ""
            article_url = (
                summary.get("content_urls", {})
                .get("desktop", {})
                .get("page", "")
            )
            title = summary.get("title", "")

            # Fetch content based on detail level
            detailed = self.config.get(CONF_WIKIPEDIA_DETAIL) == WIKIPEDIA_DETAIL_DETAILED
            if detailed:
                extract = await self._fetch_full_intro(session, title)
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

    async def _fetch_best_summary(
        self, session, titles: list[str]
    ) -> dict | None:
        """Fetch summaries and return the first non-disambiguation article."""
        for title in titles:
            encoded_title = quote(title.replace(" ", "_"), safe="")
            url = f"{WIKIPEDIA_SUMMARY_URL}/{encoded_title}"
            try:
                async with session.get(
                    url,
                    headers={
                        "User-Agent": USER_AGENT,
                        "Accept": "application/json",
                    },
                ) as resp:
                    if resp.status != 200:
                        _LOGGER.debug(
                            "Wikipedia summary for '%s' returned HTTP %d",
                            title,
                            resp.status,
                        )
                        continue
                    summary = await resp.json()

                    if summary.get("type") == "disambiguation":
                        continue

                    return summary
            except Exception as e:
                _LOGGER.debug(
                    "Error fetching Wikipedia summary for '%s': %s", title, e
                )
                continue
        return None

    async def _fetch_full_intro(self, session, title: str) -> str | None:
        """Fetch the full introduction section via the MediaWiki extracts API."""
        params = {
            "action": "query",
            "titles": title,
            "prop": "extracts",
            "exintro": "",
            "explaintext": "",
            "format": "json",
        }
        try:
            async with session.get(
                WIKIPEDIA_SEARCH_URL,
                params=params,
                headers={"User-Agent": USER_AGENT},
            ) as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()

            pages = data.get("query", {}).get("pages", {})
            for page in pages.values():
                extract = page.get("extract", "")
                if extract:
                    return extract
        except Exception as e:
            _LOGGER.debug("Error fetching full intro for '%s': %s", title, e)
        return None

    def _make_cache_key(self, query: str) -> str:
        """Build a cache key for a Wikipedia query."""
        detail = self.config.get(CONF_WIKIPEDIA_DETAIL, "concise")
        raw = json.dumps(
            {"type": "wikipedia", "q": query.lower().strip(), "d": detail},
            sort_keys=True,
        )
        return hashlib.md5(raw.encode()).hexdigest()

    def _cache_get(self, key: str) -> dict | None:
        """Retrieve from in-memory cache if not expired."""
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
        """Store in in-memory cache."""
        cache = self.hass.data.setdefault(DOMAIN, {}).setdefault("cache", {})
        cache[key] = {"ts": time.time(), "data": data}
