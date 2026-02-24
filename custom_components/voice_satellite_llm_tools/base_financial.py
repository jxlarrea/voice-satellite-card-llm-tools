"""Base financial data tool with shared logic."""

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .base_tool import BaseTool

_LOGGER = logging.getLogger(__name__)

QUERY_TYPE_STOCK = "stock"
QUERY_TYPE_CURRENCY = "currency"


class BaseFinancialTool(BaseTool):
    """Base class for financial data tools."""

    name = "get_financial_data"
    description = (
        "Get stock prices, cryptocurrency prices, or convert currencies. "
        "Use query_type 'stock' with a ticker symbol (e.g. 'AAPL', 'TSLA', 'MSFT') "
        "or a crypto symbol (e.g. 'BTC', 'ETH', 'DOGE') to get the current price. "
        "Use query_type 'currency' with from_currency and to_currency codes "
        "(e.g. 'USD', 'EUR', 'GBP') to get exchange rates or convert amounts."
    )

    parameters = vol.Schema(
        {
            vol.Required(
                "query_type",
                description="'stock' for stock/equity price, 'currency' for exchange rate.",
            ): vol.In([QUERY_TYPE_STOCK, QUERY_TYPE_CURRENCY]),
            vol.Optional(
                "symbol",
                description="Stock ticker (e.g. 'AAPL', 'TSLA') or crypto symbol (e.g. 'BTC', 'ETH'). Required for stock queries.",
            ): str,
            vol.Optional(
                "from_currency",
                description="Source currency code (e.g. 'USD'). Required for currency queries.",
            ): str,
            vol.Optional(
                "to_currency",
                description="Target currency code (e.g. 'EUR'). Required for currency queries.",
            ): str,
            vol.Optional(
                "amount",
                description="Amount to convert. Default is 1.",
            ): vol.Coerce(float),
        }
    )

    async def async_get_stock_quote(self, symbol: str) -> dict:
        """Get stock quote data. Subclasses must implement this.

        Returns a dict with keys:
            symbol, name, exchange, currency, current_price, change,
            percent_change, high, low, open, previous_close, logo_url (optional)
        """
        raise NotImplementedError

    async def async_get_currency_rate(
        self, from_currency: str, to_currency: str
    ) -> float:
        """Get exchange rate. Subclasses must implement this.

        Returns the exchange rate as a float.
        """
        raise NotImplementedError

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the financial data tool."""
        query_type = tool_input.tool_args["query_type"]

        try:
            if query_type == QUERY_TYPE_STOCK:
                return await self._handle_stock(tool_input)
            if query_type == QUERY_TYPE_CURRENCY:
                return await self._handle_currency(tool_input)
            return {"error": f"Unknown query_type: {query_type}"}

        except Exception as e:
            _LOGGER.exception("Financial data error: %s", e)
            return {"error": f"Financial data lookup failed: {e!s}"}

    async def _handle_stock(self, tool_input: llm.ToolInput) -> dict:
        """Handle a stock or crypto price query."""
        symbol = tool_input.tool_args.get("symbol", "").upper().strip()
        if not symbol:
            return {"error": "Stock ticker symbol is required for stock queries."}

        _LOGGER.info("Stock/crypto quote requested: symbol='%s'", symbol)
        data = await self.async_get_stock_quote(symbol)

        is_crypto = data.get("is_crypto", False)

        response = {
            "source": data.get("source", self.source),
            "query_type": "crypto" if is_crypto else "stock",
            "symbol": data.get("symbol", symbol),
            "name": data.get("name", ""),
            "exchange": data.get("exchange", ""),
            "currency": data.get("currency", ""),
            "current_price": data["current_price"],
            "change": data.get("change"),
            "percent_change": data.get("percent_change"),
            "high": data.get("high"),
            "low": data.get("low"),
        }

        if is_crypto:
            if data.get("market_cap"):
                response["market_cap"] = data["market_cap"]
            response["instruction"] = (
                "Present the cryptocurrency price naturally. Mention the coin name, "
                "current price in USD, and whether it's up or down in the last 24 hours "
                "with the change amount and percentage."
            )
        else:
            response["open"] = data.get("open")
            response["previous_close"] = data.get("previous_close")
            response["instruction"] = (
                "Present the stock price naturally. Mention the company name, "
                "current price with currency, and whether it's up or down today "
                "with the change amount and percentage."
            )

        logo_url = data.get("logo_url")
        if logo_url:
            response["featured_image"] = logo_url

        return response

    async def _handle_currency(self, tool_input: llm.ToolInput) -> dict:
        """Handle a currency conversion query."""
        from_cur = tool_input.tool_args.get("from_currency", "").upper().strip()
        to_cur = tool_input.tool_args.get("to_currency", "").upper().strip()
        amount = tool_input.tool_args.get("amount", 1.0)

        if not from_cur or not to_cur:
            return {
                "error": "Both from_currency and to_currency are required for currency queries."
            }

        _LOGGER.info(
            "Currency conversion requested: %s %s → %s", amount, from_cur, to_cur
        )
        rate = await self.async_get_currency_rate(from_cur, to_cur)
        converted = round(amount * rate, 2)

        return {
            "source": self.source,
            "query_type": "currency",
            "from_currency": from_cur,
            "to_currency": to_cur,
            "rate": round(rate, 6),
            "amount": amount,
            "converted_amount": converted,
            "instruction": (
                "Present the currency conversion naturally. "
                "State the converted amount and the exchange rate."
            ),
        }
