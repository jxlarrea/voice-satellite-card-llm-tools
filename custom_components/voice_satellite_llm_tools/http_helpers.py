"""Shared HTTP utilities with timeout and retry logic."""

import asyncio
import logging

import aiohttp
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_LOGGER = logging.getLogger(__name__)

DEFAULT_TIMEOUT = aiohttp.ClientTimeout(total=10)
_RETRY_STATUSES = {429, 502, 503}


async def fetch_json(
    hass: HomeAssistant,
    url: str,
    *,
    params: dict | None = None,
    headers: dict | None = None,
    timeout: aiohttp.ClientTimeout = DEFAULT_TIMEOUT,
    retries: int = 1,
) -> dict:
    """GET a URL and return parsed JSON. Retries once on 429/502/503.

    Raises RuntimeError on HTTP >= 400 (after retries) or network failure.
    """
    session = async_get_clientsession(hass)
    last_exc: Exception | None = None

    for attempt in range(retries + 1):
        try:
            async with session.get(
                url, params=params, headers=headers, timeout=timeout
            ) as resp:
                if resp.status in _RETRY_STATUSES and attempt < retries:
                    _LOGGER.debug(
                        "HTTP %d from %s, retrying (attempt %d)", resp.status, url, attempt + 1
                    )
                    await asyncio.sleep(1)
                    continue
                if resp.status >= 400:
                    text = await resp.text()
                    raise RuntimeError(f"HTTP {resp.status}: {text[:300]}")
                return await resp.json()
        except (aiohttp.ClientError, asyncio.TimeoutError) as exc:
            last_exc = exc
            if attempt < retries:
                _LOGGER.debug("Request to %s failed (%s), retrying", url, exc)
                await asyncio.sleep(1)

    raise last_exc or RuntimeError(f"Request to {url} failed")
