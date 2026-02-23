"""Brave Image Search tool."""

import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .base_image_search import BaseImageSearchTool
from .const import (
    CONF_BRAVE_API_KEY,
    CONF_BRAVE_IMAGE_NUM_RESULTS,
    CONF_BRAVE_SAFESEARCH,
)

_LOGGER = logging.getLogger(__name__)

BRAVE_IMAGE_ENDPOINT = "https://api.search.brave.com/res/v1/images/search"


class BraveImageSearchTool(BaseImageSearchTool):
    """Image search using Brave Image Search API."""

    source = "brave"

    def _get_configured_num_results(self) -> int:
        return int(self.config.get(CONF_BRAVE_IMAGE_NUM_RESULTS, 3))

    async def async_search_images(self, query: str, num_results: int) -> list[dict]:
        api_key = self.config.get(CONF_BRAVE_API_KEY, "")

        if not api_key:
            raise RuntimeError("Brave API key not configured")

        safesearch = self.config.get(CONF_BRAVE_SAFESEARCH, "moderate")
        session = async_get_clientsession(self.hass)

        headers = {
            "Accept": "application/json",
            "X-Subscription-Token": api_key,
        }

        params = {
            "q": query,
            "count": num_results,
            "safesearch": safesearch,
        }

        async with session.get(
            BRAVE_IMAGE_ENDPOINT, headers=headers, params=params
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(
                    f"Brave Image Search returned HTTP {resp.status}: {error_text}"
                )

            data = await resp.json()
            results = []

            for item in data.get("results", []):
                properties = item.get("properties", {})
                thumbnail = item.get("thumbnail", {})
                results.append(
                    {
                        "image_url": properties.get("url", ""),
                        "title": item.get("title", ""),
                        "thumbnail_url": thumbnail.get("src", ""),
                        "source_url": item.get("url", ""),
                        "source": item.get("source", ""),
                        "width": properties.get("width"),
                        "height": properties.get("height"),
                    }
                )

            return results
