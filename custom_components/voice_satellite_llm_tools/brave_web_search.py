"""Brave Web Search tool using Brave Search API."""

import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .base_web_search import BaseWebSearchTool
from .const import CONF_BRAVE_API_KEY, CONF_BRAVE_WEB_NUM_RESULTS

_LOGGER = logging.getLogger(__name__)

BRAVE_WEB_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"


class BraveWebSearchTool(BaseWebSearchTool):
    """Web search using Brave Search API."""

    source = "brave"

    def _get_configured_num_results(self) -> int:
        return int(self.config.get(CONF_BRAVE_WEB_NUM_RESULTS, 3))

    async def async_search_web(self, query: str, num_results: int) -> list[dict]:
        """Search the web via Brave Search API."""
        api_key = self.config.get(CONF_BRAVE_API_KEY, "")

        if not api_key:
            raise RuntimeError("Brave API key not configured")

        session = async_get_clientsession(self.hass)

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": api_key,
        }

        params = {
            "q": query,
            "count": num_results,
            "result_filter": "web",
            "extra_snippets": "true",
        }

        async with session.get(
            BRAVE_WEB_ENDPOINT, headers=headers, params=params
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(
                    f"Brave Web Search returned HTTP {resp.status}: {error_text}"
                )

            data = await resp.json()
            results = []

            for item in data.get("web", {}).get("results", []):
                thumbnail = item.get("thumbnail", {})
                thumbnail_url = thumbnail.get("src", "") if thumbnail else ""

                snippet = item.get("description", "")
                extra = item.get("extra_snippets", [])
                if extra:
                    snippet = snippet + " " + " ".join(extra)

                results.append(
                    {
                        "url": item.get("url", ""),
                        "title": item.get("title", ""),
                        "snippet": snippet,
                        "thumbnail_url": thumbnail_url,
                    }
                )

            return results
