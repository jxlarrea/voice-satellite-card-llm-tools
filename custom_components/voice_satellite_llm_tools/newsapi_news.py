"""NewsAPI news headlines tool."""

import hashlib
import json
import logging
import time

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .base_tool import BaseTool
from .const import CONF_NEWS_COUNTRY, CONF_NEWS_NUM_RESULTS, CONF_NEWSAPI_KEY, DOMAIN
from .http_helpers import fetch_json

_LOGGER = logging.getLogger(__name__)

NEWSAPI_URL = "https://newsapi.org/v2/top-headlines"
NEWS_CACHE_TTL = 1800  # 30 min — news goes stale faster than other searches

_CATEGORIES = [
    "business",
    "entertainment",
    "general",
    "health",
    "science",
    "sports",
    "technology",
]


class NewsAPINewsTool(BaseTool):
    """Get current news headlines via NewsAPI."""

    source = "newsapi"
    name = "get_news_headlines"
    description = (
        "Get current news headlines. Optionally filter by topic or category. "
        "Use when the user asks about news, current events, or what's happening."
    )

    parameters = vol.Schema(
        {
            vol.Optional(
                "query",
                description=(
                    "Optional topic to search for, e.g. 'climate change', 'AI', 'football'."
                ),
            ): str,
            vol.Optional(
                "category",
                description=(
                    "Optional category: business, entertainment, general, "
                    "health, science, sports, or technology."
                ),
            ): vol.In(_CATEGORIES),
            vol.Optional(
                "num_results",
                description="Number of headlines to return (1-10).",
            ): vol.All(int, vol.Range(min=1, max=10)),
        }
    )

    def _make_cache_key(self, query: str, category: str, num_results: int) -> str:
        raw = json.dumps(
            {"q": query, "cat": category, "n": num_results}, sort_keys=True
        )
        return "news_" + hashlib.md5(raw.encode()).hexdigest()

    def _cache_get(self, key: str) -> dict | None:
        cache = self.hass.data.get(DOMAIN, {}).get("cache", {})
        entry = cache.get(key)
        if entry is None:
            return None
        if time.time() - entry["ts"] > NEWS_CACHE_TTL:
            cache.pop(key, None)
            return None
        _LOGGER.debug("News cache hit for key %s", key)
        return entry["data"]

    def _cache_set(self, key: str, data: dict) -> None:
        cache = self.hass.data.setdefault(DOMAIN, {}).setdefault("cache", {})
        cache[key] = {"ts": time.time(), "data": data}

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        api_key = self.config.get(CONF_NEWSAPI_KEY, "")
        if not api_key:
            return {"error": "NewsAPI key not configured."}

        query = tool_input.tool_args.get("query", "")
        category = tool_input.tool_args.get("category", "")
        num_results = int(
            tool_input.tool_args.get(
                "num_results", self.config.get(CONF_NEWS_NUM_RESULTS, 5)
            )
        )

        cache_key = self._make_cache_key(query, category, num_results)
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        params: dict = {"apiKey": api_key, "pageSize": min(num_results, 10)}
        country = self.config.get(CONF_NEWS_COUNTRY, "us")
        if country:
            params["country"] = country
        if query:
            params["q"] = query
        if category:
            params["category"] = category

        try:
            data = await fetch_json(hass, NEWSAPI_URL, params=params)
        except Exception as e:
            _LOGGER.error("NewsAPI request failed: %s", e)
            return {"error": f"Failed to retrieve news: {e!s}"}

        articles = [
            {
                "title": a.get("title", ""),
                "source": a.get("source", {}).get("name", ""),
                "description": a.get("description", ""),
                "url": a.get("url", ""),
                "published_at": a.get("publishedAt", ""),
                "image_url": a.get("urlToImage", ""),
            }
            for a in data.get("articles", [])[:num_results]
            if a.get("title") and a.get("title") != "[Removed]"
        ]

        featured_image = next(
            (a["image_url"] for a in articles if a.get("image_url")), None
        )

        response = {
            "source": "newsapi",
            "query": query,
            "category": category,
            "num_results": len(articles),
            "results": articles,
            "featured_image": featured_image,
            "instruction": (
                "Summarize the top news headlines naturally. "
                "Mention 3-5 key stories with their sources. "
                "Do not list URLs. Be concise and conversational."
            ),
        }

        self._cache_set(cache_key, response)
        return response
