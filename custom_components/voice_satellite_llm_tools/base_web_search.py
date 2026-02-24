"""Base web search tool with shared logic and caching."""

import hashlib
import json
import logging
import time
from urllib.parse import urlparse

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .base_tool import BaseTool
from .const import CONF_CACHE_TTL, DEFAULT_CACHE_TTL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BaseWebSearchTool(BaseTool):
    """Base class for web search tools."""

    name = "search_web"
    description = (
        "Search the internet for information on a topic. "
        "Returns web page results with titles and snippets. "
        "Use this when the user asks a question requiring current information, "
        "facts, or general knowledge."
    )

    parameters = vol.Schema(
        {
            vol.Required("query", description="The web search query"): str,
            vol.Optional(
                "num_results",
                description="Number of web results to return (1-6)",
            ): vol.All(int, vol.Range(min=1, max=6)),
        }
    )

    async def async_search_web(self, query: str, num_results: int) -> list[dict]:
        """Perform the web search. Subclasses must implement this.

        Returns a list of dicts with keys:
            url, title, snippet, thumbnail_url (optional)
        """
        raise NotImplementedError

    def _get_num_results(self, tool_input: llm.ToolInput) -> int:
        """Resolve number of results, capped at the configured maximum."""
        configured_max = min(self._get_configured_num_results(), 6)
        explicit = tool_input.tool_args.get("num_results")
        if explicit is not None:
            return min(explicit, configured_max)
        return configured_max

    def _get_configured_num_results(self) -> int:
        """Get the provider-specific configured default. Override in subclass."""
        return 3

    def _make_cache_key(self, query: str, num_results: int) -> str:
        """Build a cache key from query + result count."""
        raw = json.dumps(
            {"type": "web", "q": query.lower().strip(), "n": num_results},
            sort_keys=True,
        )
        return hashlib.md5(raw.encode()).hexdigest()

    def _cache_get(self, key: str) -> list[dict] | None:
        """Retrieve from in-memory cache if not expired."""
        cache = self.hass.data.get(DOMAIN, {}).get("cache", {})
        entry = cache.get(key)
        if entry is None:
            return None
        ttl = int(self.config.get(CONF_CACHE_TTL, DEFAULT_CACHE_TTL))
        if time.time() - entry["ts"] > ttl:
            cache.pop(key, None)
            return None
        _LOGGER.debug("Web search cache hit for key %s", key)
        return entry["data"]

    def _cache_set(self, key: str, data: list[dict]) -> None:
        """Store in in-memory cache."""
        cache = self.hass.data.setdefault(DOMAIN, {}).setdefault("cache", {})
        cache[key] = {"ts": time.time(), "data": data}

    def _extract_featured_image(self, results: list[dict]) -> str | None:
        """Extract the best thumbnail from results for the card's media panel."""
        for r in results:
            thumb = r.get("thumbnail_url", "")
            if thumb and thumb.startswith("http"):
                return thumb
        return None

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the web search tool."""
        query = tool_input.tool_args["query"]
        num_results = self._get_num_results(tool_input)

        _LOGGER.info(
            "Web search requested: query='%s', num_results=%d",
            query,
            num_results,
        )

        try:
            cache_key = self._make_cache_key(query, num_results)
            cached = self._cache_get(cache_key)
            if cached is not None:
                return self._format_response(cached, query)

            results = await self.async_search_web(query, num_results)

            if not results:
                return {
                    "source": self.source,
                    "query": query,
                    "results": [],
                    "featured_image": None,
                    "message": "No results found for this query.",
                }

            self._cache_set(cache_key, results)
            return self._format_response(results, query)

        except Exception as e:
            _LOGGER.exception("Error during web search for '%s': %s", query, e)
            return {"error": f"Web search failed: {e!s}"}

    @staticmethod
    def _extract_site_name(url: str) -> str:
        """Extract a clean site name from a URL (e.g. 'reddit.com')."""
        try:
            hostname = urlparse(url).hostname or ""
            if hostname.startswith("www."):
                hostname = hostname[4:]
            return hostname
        except Exception:
            return ""

    def _format_response(self, results: list[dict], query: str) -> dict:
        """Format the search results into the LLM response structure."""
        return {
            "source": self.source,
            "query": query,
            "num_results": len(results),
            "results": [
                {
                    "url": r["url"],
                    "title": r["title"],
                    "snippet": r.get("snippet", ""),
                    "site_name": self._extract_site_name(r.get("url", "")),
                }
                for r in results
            ],
            "featured_image": self._extract_featured_image(results),
            "instruction": (
                "Summarize the key information from these search results in 2-3 concise sentences. "
                "Do NOT list individual URLs, titles, or sources. "
                "The user cannot see the raw results — synthesize the information into a helpful answer."
            ),
        }
