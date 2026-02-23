"""Base image search tool with shared logic and caching."""

import hashlib
import json
import logging
import time

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .base_tool import BaseTool
from .const import CONF_CACHE_TTL, DEFAULT_CACHE_TTL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BaseImageSearchTool(BaseTool):
    """Base class for image search tools."""

    name = "search_images"
    description = (
        "Search the internet for images matching a query. "
        "Returns a list of image results with URLs, titles, and thumbnails. "
        "Use this when the user asks to find, search for, or show images."
    )

    parameters = vol.Schema(
        {
            vol.Required("query", description="The image search query"): str,
            vol.Optional(
                "num_results",
                description="Number of image results to return (1-10)",
            ): vol.All(int, vol.Range(min=1, max=10)),
            vol.Optional(
                "auto_display",
                description=(
                    "Set to true when the user wants to see a specific image "
                    "displayed immediately (e.g. 'show me the Mona Lisa'). "
                    "Set to false when the user wants to browse multiple results."
                ),
            ): bool,
        }
    )

    async def async_search_images(self, query: str, num_results: int) -> list[dict]:
        """Perform the image search. Subclasses must implement this.

        Returns a list of dicts with keys:
            image_url, title, thumbnail_url, source_url, source, width, height
        """
        raise NotImplementedError

    def _get_num_results(self, tool_input: llm.ToolInput) -> int:
        """Resolve number of results, capped at the configured maximum."""
        configured_max = self._get_configured_num_results()
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
            {"q": query.lower().strip(), "n": num_results}, sort_keys=True
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
        _LOGGER.debug("Image search cache hit for key %s", key)
        return entry["data"]

    def _cache_set(self, key: str, data: list[dict]) -> None:
        """Store in in-memory cache."""
        cache = self.hass.data.setdefault(DOMAIN, {}).setdefault("cache", {})
        cache[key] = {"ts": time.time(), "data": data}

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the image search tool."""
        query = tool_input.tool_args["query"]
        num_results = self._get_num_results(tool_input)
        auto_display = tool_input.tool_args.get("auto_display", False)

        _LOGGER.info(
            "Image search requested: query='%s', num_results=%d, auto_display=%s",
            query,
            num_results,
            auto_display,
        )

        try:
            cache_key = self._make_cache_key(query, num_results)
            cached = self._cache_get(cache_key)
            if cached is not None:
                return self._format_response(cached, query, auto_display)

            results = await self.async_search_images(query, num_results)

            if not results:
                return {
                    "query": query,
                    "results": [],
                    "auto_display": False,
                    "message": "No images found for this query.",
                }

            self._cache_set(cache_key, results)
            return self._format_response(results, query, auto_display)

        except Exception as e:
            _LOGGER.exception("Error during image search for '%s': %s", query, e)
            return {"error": f"Image search failed: {e!s}"}

    def _format_response(
        self, results: list[dict], query: str, auto_display: bool
    ) -> dict:
        """Format the search results into the LLM response structure."""
        return {
            "query": query,
            "num_results": len(results),
            "auto_display": auto_display,
            "results": [
                {
                    "image_url": r["image_url"],
                    "title": r["title"],
                    "thumbnail_url": r.get("thumbnail_url", ""),
                    "source_url": r.get("source_url", ""),
                    "source": r.get("source", ""),
                    "width": r.get("width"),
                    "height": r.get("height"),
                }
                for r in results
            ],
            "instruction": (
                "Do NOT include image URLs or markdown image syntax in your response. "
                "The images will be displayed automatically by the UI. "
                "Simply tell the user what you found in plain text, e.g. "
                "'Here are some cat images I found from Unsplash and Google Images.'"
            ),
        }
