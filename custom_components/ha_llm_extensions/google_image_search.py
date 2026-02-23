"""Google Custom Search image search tool."""

import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .base_image_search import BaseImageSearchTool
from .const import (
    CONF_GOOGLE_CSE_API_KEY,
    CONF_GOOGLE_CSE_CX,
    CONF_GOOGLE_CSE_NUM_RESULTS,
)

_LOGGER = logging.getLogger(__name__)

GOOGLE_CSE_ENDPOINT = "https://www.googleapis.com/customsearch/v1"


class GoogleImageSearchTool(BaseImageSearchTool):
    """Image search using Google Custom Search API."""

    def _get_configured_num_results(self) -> int:
        return int(self.config.get(CONF_GOOGLE_CSE_NUM_RESULTS, 3))

    async def async_search_images(self, query: str, num_results: int) -> list[dict]:
        api_key = self.config.get(CONF_GOOGLE_CSE_API_KEY, "")
        cx = self.config.get(CONF_GOOGLE_CSE_CX, "")

        if not api_key:
            raise RuntimeError("Google Custom Search API key not configured")
        if not cx:
            raise RuntimeError("Google Custom Search Engine ID (cx) not configured")

        session = async_get_clientsession(self.hass)

        params = {
            "key": api_key,
            "cx": cx,
            "q": query,
            "searchType": "image",
            "num": min(num_results, 10),
        }

        async with session.get(GOOGLE_CSE_ENDPOINT, params=params) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(
                    f"Google Custom Search returned HTTP {resp.status}: {error_text}"
                )

            data = await resp.json()
            results = []

            for item in data.get("items", []):
                image_info = item.get("image", {})
                results.append(
                    {
                        "image_url": item.get("link", ""),
                        "title": item.get("title", ""),
                        "thumbnail_url": image_info.get("thumbnailLink", ""),
                        "source_url": image_info.get("contextLink", ""),
                        "source": item.get("displayLink", ""),
                        "width": image_info.get("width"),
                        "height": image_info.get("height"),
                    }
                )

            return results
