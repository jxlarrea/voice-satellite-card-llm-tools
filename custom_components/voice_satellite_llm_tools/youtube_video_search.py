"""YouTube Video Search tool using YouTube Data API v3."""

import hashlib
import json
import logging
import time

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .base_tool import BaseTool
from .const import (
    CONF_CACHE_TTL,
    CONF_YOUTUBE_API_KEY,
    CONF_YOUTUBE_NUM_RESULTS,
    DEFAULT_CACHE_TTL,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

YOUTUBE_SEARCH_URL = "https://www.googleapis.com/youtube/v3/search"
YOUTUBE_VIDEOS_URL = "https://www.googleapis.com/youtube/v3/videos"


class YouTubeVideoSearchTool(BaseTool):
    """Video search using YouTube Data API v3."""

    source = "youtube"
    name = "search_videos"
    description = (
        "Search YouTube for videos matching a query. "
        "Returns a list of video results with URLs, titles, thumbnails, and channel info. "
        "Use this when the user asks to find, search for, or show videos."
    )

    parameters = vol.Schema(
        {
            vol.Required("query", description="The video search query"): str,
            vol.Optional(
                "num_results",
                description="Number of video results to return (1-10)",
            ): vol.All(int, vol.Range(min=1, max=10)),
            vol.Optional(
                "auto_play",
                description=(
                    "Set to true when the user wants to immediately watch/play a "
                    "specific video. Set to false when the user wants to browse or "
                    "explore multiple results."
                ),
            ): bool,
        }
    )

    def _get_num_results(self, tool_input: llm.ToolInput) -> int:
        """Resolve number of results, capped at the configured maximum."""
        configured_max = int(self.config.get(CONF_YOUTUBE_NUM_RESULTS, 3))
        explicit = tool_input.tool_args.get("num_results")
        if explicit is not None:
            return min(explicit, configured_max)
        return configured_max

    def _make_cache_key(self, query: str, num_results: int) -> str:
        """Build a cache key from query + result count."""
        raw = json.dumps(
            {"type": "video", "q": query.lower().strip(), "n": num_results},
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
        _LOGGER.debug("Video search cache hit for key %s", key)
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
        """Execute the video search tool."""
        query = tool_input.tool_args["query"]
        num_results = self._get_num_results(tool_input)
        auto_play = tool_input.tool_args.get("auto_play", False)

        _LOGGER.info(
            "Video search requested: query='%s', num_results=%d, auto_play=%s",
            query,
            num_results,
            auto_play,
        )

        try:
            cache_key = self._make_cache_key(query, num_results)
            cached = self._cache_get(cache_key)
            if cached is not None:
                return self._format_response(cached, query, auto_play)

            results = await self._search_videos(query, num_results)

            if not results:
                return {
                    "source": self.source,
                    "query": query,
                    "results": [],
                    "auto_play": False,
                    "message": "No videos found for this query.",
                }

            self._cache_set(cache_key, results)
            return self._format_response(results, query, auto_play)

        except Exception as e:
            _LOGGER.exception("Error during video search for '%s': %s", query, e)
            return {"error": f"Video search failed: {e!s}"}

    async def _search_videos(self, query: str, num_results: int) -> list[dict]:
        """Search YouTube and return video results with metadata."""
        api_key = self.config.get(CONF_YOUTUBE_API_KEY, "")
        if not api_key:
            raise RuntimeError("YouTube API key not configured")

        session = async_get_clientsession(self.hass)

        # Step 1: Search for videos
        search_params = {
            "part": "snippet",
            "q": query,
            "type": "video",
            "maxResults": num_results,
            "key": api_key,
        }

        async with session.get(YOUTUBE_SEARCH_URL, params=search_params) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(
                    f"YouTube Search API returned HTTP {resp.status}: {error_text}"
                )
            search_data = await resp.json()

        items = search_data.get("items", [])
        if not items:
            return []

        video_ids = [item["id"]["videoId"] for item in items]

        # Step 2: Get video details (duration, view count, etc.)
        details_params = {
            "part": "contentDetails,statistics",
            "id": ",".join(video_ids),
            "key": api_key,
        }

        async with session.get(YOUTUBE_VIDEOS_URL, params=details_params) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                _LOGGER.warning(
                    "YouTube Videos API returned HTTP %d: %s", resp.status, error_text
                )
                details_map = {}
            else:
                details_data = await resp.json()
                details_map = {
                    item["id"]: item for item in details_data.get("items", [])
                }

        results = []
        for item in items:
            video_id = item["id"]["videoId"]
            snippet = item.get("snippet", {})
            details = details_map.get(video_id, {})
            stats = details.get("statistics", {})
            content = details.get("contentDetails", {})

            thumbnails = snippet.get("thumbnails", {})
            thumbnail_url = (
                thumbnails.get("high", {}).get("url")
                or thumbnails.get("medium", {}).get("url")
                or thumbnails.get("default", {}).get("url", "")
            )

            results.append(
                {
                    "video_url": f"https://www.youtube.com/watch?v={video_id}",
                    "video_id": video_id,
                    "title": snippet.get("title", ""),
                    "description": snippet.get("description", ""),
                    "thumbnail_url": thumbnail_url,
                    "channel_name": snippet.get("channelTitle", ""),
                    "published_at": snippet.get("publishedAt", ""),
                    "duration": content.get("duration", ""),
                    "view_count": stats.get("viewCount", ""),
                }
            )

        return results

    def _format_response(
        self, results: list[dict], query: str, auto_play: bool
    ) -> dict:
        """Format the search results into the LLM response structure."""
        return {
            "source": self.source,
            "query": query,
            "num_results": len(results),
            "auto_play": auto_play,
            "results": results,
            "instruction": (
                "Do NOT include video URLs in your response. "
                "The videos will be displayed automatically by the UI. "
                "Simply tell the user what you found in plain text, e.g. "
                "'Here are some cooking tutorial videos I found on YouTube.'"
            ),
        }
