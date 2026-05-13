"""SearXNG Image Search tool."""

import logging

from .base_image_search import BaseImageSearchTool
from .const import CONF_SEARXNG_ENGINES, CONF_SEARXNG_IMAGE_NUM_RESULTS, CONF_SEARXNG_URL
from .http_helpers import fetch_json

_LOGGER = logging.getLogger(__name__)


class SearXNGImageSearchTool(BaseImageSearchTool):
    """Image search using a SearXNG instance."""

    source = "searxng"

    def _get_configured_num_results(self) -> int:
        return int(self.config.get(CONF_SEARXNG_IMAGE_NUM_RESULTS, 3))

    async def async_search_images(self, query: str, num_results: int) -> list[dict]:
        base_url = self.config.get(CONF_SEARXNG_URL, "").rstrip("/")
        if not base_url:
            raise RuntimeError("SearXNG server URL not configured")

        params = {
            "q": query,
            "categories": "images",
            "format": "json",
        }
        engines = self.config.get(CONF_SEARXNG_ENGINES, "").strip()
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
            img_src = item.get("img_src", "")
            if not img_src or not img_src.startswith("http"):
                continue
            results.append(
                {
                    "image_url": img_src,
                    "title": item.get("title", ""),
                    "thumbnail_url": item.get("thumbnail_src", ""),
                    "source_url": item.get("url", ""),
                    "source": item.get("engine", ""),
                    "width": None,
                    "height": None,
                }
            )

        return results
