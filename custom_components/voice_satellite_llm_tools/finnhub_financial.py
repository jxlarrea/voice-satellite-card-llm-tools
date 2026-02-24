"""Finnhub financial data tool implementation."""

import logging

from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .base_financial import BaseFinancialTool
from .const import CONF_FINNHUB_API_KEY

_LOGGER = logging.getLogger(__name__)

FINNHUB_BASE_URL = "https://finnhub.io/api/v1"
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Mapping of crypto ticker symbols to CoinGecko IDs
CRYPTO_COINGECKO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "XRP": "ripple",
    "SOL": "solana",
    "ADA": "cardano",
    "DOGE": "dogecoin",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "LINK": "chainlink",
    "MATIC": "matic-network",
    "UNI": "uniswap",
    "SHIB": "shiba-inu",
    "LTC": "litecoin",
    "BCH": "bitcoin-cash",
    "ATOM": "cosmos",
    "XLM": "stellar",
    "ALGO": "algorand",
    "FIL": "filecoin",
    "NEAR": "near",
    "APT": "aptos",
    "ARB": "arbitrum",
    "OP": "optimism",
    "BNB": "binancecoin",
    "TRX": "tron",
    "ETC": "ethereum-classic",
    "XMR": "monero",
    "PEPE": "pepe",
    "SUI": "sui",
    "SEI": "sei-network",
}


class FinnhubFinancialTool(BaseFinancialTool):
    """Financial data using Finnhub API."""

    source = "finnhub"

    def _get_crypto_base(self, symbol: str) -> str:
        """Strip common quote-currency suffixes to get the crypto base symbol."""
        base = symbol.upper()
        for suffix in ("USDT", "USD", "EUR", "GBP"):
            if base.endswith(suffix) and len(base) > len(suffix):
                return base[: -len(suffix)]
        return base

    async def async_get_stock_quote(self, symbol: str) -> dict:
        """Get stock quote from Finnhub, with crypto fallback via CoinGecko."""
        api_key = self.config.get(CONF_FINNHUB_API_KEY, "")
        if not api_key:
            raise RuntimeError("Finnhub API key not configured")

        # Check if this looks like a crypto symbol — try CoinGecko first
        base = self._get_crypto_base(symbol)
        if base in CRYPTO_COINGECKO_IDS:
            crypto = await self._try_crypto_quote(base)
            if crypto:
                return crypto

        session = async_get_clientsession(self.hass)
        params = {"symbol": symbol, "token": api_key}

        async with session.get(
            f"{FINNHUB_BASE_URL}/quote", params=params
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(
                    f"Finnhub quote returned HTTP {resp.status}: {error_text}"
                )
            quote = await resp.json()

        if quote.get("c") is None or quote.get("c") == 0:
            # Stock not found — try crypto as last resort
            crypto = await self._try_crypto_quote(base)
            if crypto:
                return crypto
            raise RuntimeError(
                f"No quote data found for symbol '{symbol}'. "
                "Check that the ticker is valid."
            )

        # Fetch company profile for name, exchange, logo
        profile = {}
        try:
            async with session.get(
                f"{FINNHUB_BASE_URL}/stock/profile2", params=params
            ) as resp:
                if resp.status == 200:
                    profile = await resp.json()
        except Exception:
            _LOGGER.debug("Could not fetch company profile for %s", symbol)

        return {
            "symbol": symbol,
            "name": profile.get("name", ""),
            "exchange": profile.get("exchange", ""),
            "currency": profile.get("currency", "USD"),
            "current_price": quote["c"],
            "change": quote.get("d"),
            "percent_change": quote.get("dp"),
            "high": quote.get("h"),
            "low": quote.get("l"),
            "open": quote.get("o"),
            "previous_close": quote.get("pc"),
            "logo_url": profile.get("logo", ""),
        }

    async def _try_crypto_quote(self, base_symbol: str) -> dict | None:
        """Try to get a crypto quote via CoinGecko."""
        coingecko_id = CRYPTO_COINGECKO_IDS.get(base_symbol)
        if not coingecko_id:
            return None

        session = async_get_clientsession(self.hass)

        try:
            async with session.get(
                f"{COINGECKO_BASE_URL}/coins/markets",
                params={
                    "vs_currency": "usd",
                    "ids": coingecko_id,
                    "price_change_percentage": "24h",
                },
            ) as resp:
                if resp.status != 200:
                    _LOGGER.debug(
                        "CoinGecko returned HTTP %s for %s",
                        resp.status,
                        coingecko_id,
                    )
                    return None
                data = await resp.json()
        except Exception:
            _LOGGER.debug("CoinGecko lookup failed for %s", coingecko_id)
            return None

        if not data:
            return None

        coin = data[0]
        _LOGGER.info(
            "Crypto quote resolved via CoinGecko: %s → %s",
            base_symbol,
            coingecko_id,
        )

        return {
            "is_crypto": True,
            "source": "coingecko",
            "symbol": coin.get("symbol", base_symbol).upper(),
            "name": coin.get("name", base_symbol),
            "exchange": "Crypto",
            "currency": "USD",
            "current_price": coin.get("current_price"),
            "change": coin.get("price_change_24h"),
            "percent_change": coin.get("price_change_percentage_24h"),
            "high": coin.get("high_24h"),
            "low": coin.get("low_24h"),
            "market_cap": coin.get("market_cap"),
            "logo_url": coin.get("image", ""),
        }

    async def async_get_currency_rate(
        self, from_currency: str, to_currency: str
    ) -> float:
        """Get exchange rate from Finnhub."""
        api_key = self.config.get(CONF_FINNHUB_API_KEY, "")
        if not api_key:
            raise RuntimeError("Finnhub API key not configured")

        session = async_get_clientsession(self.hass)

        async with session.get(
            f"{FINNHUB_BASE_URL}/forex/rates",
            params={"base": from_currency, "token": api_key},
        ) as resp:
            if resp.status != 200:
                error_text = await resp.text()
                raise RuntimeError(
                    f"Finnhub forex returned HTTP {resp.status}: {error_text}"
                )
            data = await resp.json()

        rates = data.get("quote", {})
        if to_currency not in rates:
            raise RuntimeError(
                f"Exchange rate for {from_currency} → {to_currency} not available."
            )

        return float(rates[to_currency])
