"""SearXNG Image Search tool."""

import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .base_image_search import BaseImageSearchTool
from .const import CONF_SEARXNG_ENGINES, CONF_SEARXNG_IMAGE_NUM_RESULTS, CONF_SEARXNG_URL

_LOGGER = logging.getLogger(__name__)


class SearXNGImageSearchTool(BaseImageSearchTool):
    """Image search using a SearXNG instance."""

    def _get_configured_num_results(self) -> int:
        return int(self.config.get(CONF_SEARXNG_IMAGE_NUM_RESULTS, 3))

    async def async_search_images(self, query: str, num_results: int) -> list[dict]:
        base_url = self.config.get(CONF_SEARXNG_URL, "")

        if not base_url:
            raise RuntimeError("SearXNG server URL not configured")

        session = async_get_clientsession(self.hass)
        base_url = base_url.rstrip("/")

        params = {
            "q": query,
            "categories": "images",
            "format": "json",
        }

        engines = self.config.get(CONF_SEARXNG_ENGINES, "").strip()
        if engines:
            params["engines"] = engines

        async with session.get(
            f"{base_url}/search", headers={"Accept": "application/json"}, params=params
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(
                    f"SearXNG returned HTTP {resp.status}: {error_text}"
                )

            data = await resp.json()
            results = []

            for item in data.get("results", []):
                if len(results) >= num_results:
                    break

                img_src = item.get("img_src", "")

                # Skip results without a valid direct image URL
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
