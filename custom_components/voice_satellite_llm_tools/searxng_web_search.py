"""SearXNG Web Search tool."""

import logging

from .base_web_search import BaseWebSearchTool
from .const import CONF_SEARXNG_URL, CONF_SEARXNG_WEB_ENGINES, CONF_SEARXNG_WEB_NUM_RESULTS
from .http_helpers import fetch_json

_LOGGER = logging.getLogger(__name__)


class SearXNGWebSearchTool(BaseWebSearchTool):
    """Web search using a SearXNG instance."""

    source = "searxng"

    def _get_configured_num_results(self) -> int:
        return int(self.config.get(CONF_SEARXNG_WEB_NUM_RESULTS, 3))

    async def async_search_web(self, query: str, num_results: int) -> list[dict]:
        """Search the web via SearXNG."""
        base_url = self.config.get(CONF_SEARXNG_URL, "").rstrip("/")
        if not base_url:
            raise RuntimeError("SearXNG server URL not configured")

        params = {
            "q": query,
            "categories": "general",
            "format": "json",
        }
        engines = self.config.get(CONF_SEARXNG_WEB_ENGINES, "").strip()
        if engines:
            params["engines"] = engines

        data = await fetch_json(
            self.hass,
            f"{base_url}/search",
            headers={"Accept": "application/json"},
            params=params,
        )

        results = []
        for item in data.get("results", []):
            if len(results) >= num_results:
                break
            url = item.get("url", "")
            if not url or not url.startswith("http"):
                continue
            thumb = (
                item.get("img_src", "")
                or item.get("thumbnail", "")
                or item.get("thumbnail_src", "")
            )
            results.append(
                {
                    "url": url,
                    "title": item.get("title", ""),
                    "snippet": item.get("content", ""),
                    "thumbnail_url": thumb if thumb and thumb.startswith("http") else "",
                }
            )

        return results
