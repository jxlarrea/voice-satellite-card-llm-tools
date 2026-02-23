"""Config flow for LLM Extensions."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectOptionDict,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import (
    ADDON_NAME,
    CONF_BRAVE_API_KEY,
    CONF_BRAVE_IMAGE_NUM_RESULTS,
    CONF_BRAVE_SAFESEARCH,
    CONF_GOOGLE_CSE_API_KEY,
    CONF_GOOGLE_CSE_CX,
    CONF_GOOGLE_CSE_NUM_RESULTS,
    CONF_IMAGE_SEARCH_PROVIDER,
    CONF_IMAGE_SEARCH_PROVIDER_BRAVE,
    CONF_IMAGE_SEARCH_PROVIDER_GOOGLE,
    CONF_IMAGE_SEARCH_PROVIDER_SEARXNG,
    CONF_IMAGE_SEARCH_PROVIDERS,
    CONF_SEARXNG_ENGINES,
    CONF_SEARXNG_IMAGE_NUM_RESULTS,
    CONF_SEARXNG_URL,
    DOMAIN,
    SERVICE_DEFAULTS,
)

_LOGGER = logging.getLogger(__name__)

# Step identifiers
STEP_USER = "user"
STEP_GOOGLE = "google"
STEP_BRAVE = "brave"
STEP_SEARXNG = "searxng"

SAFESEARCH_OPTIONS = {
    "off": "Off",
    "moderate": "Moderate",
    "strict": "Strict",
}


def _options_to_selections(opts: dict) -> list[SelectOptionDict]:
    """Convert a dict to a list of SelectOptionDict."""
    return [SelectOptionDict(value=key, label=val) for key, val in opts.items()]


def _num_results_selector() -> NumberSelector:
    """Create a number selector for result count (1-10)."""
    return NumberSelector(
        NumberSelectorConfig(
            min=1,
            max=10,
            step=1,
            mode=NumberSelectorMode.SLIDER,
            unit_of_measurement="images",
        )
    )


def get_user_schema() -> vol.Schema:
    """Schema for provider selection step."""
    return vol.Schema(
        {
            vol.Required(CONF_IMAGE_SEARCH_PROVIDER): SelectSelector(
                SelectSelectorConfig(
                    mode=SelectSelectorMode.DROPDOWN,
                    options=_options_to_selections(CONF_IMAGE_SEARCH_PROVIDERS),
                )
            ),
        }
    )


def get_google_schema() -> vol.Schema:
    """Schema for Google Custom Search configuration."""
    return vol.Schema(
        {
            vol.Required(
                CONF_GOOGLE_CSE_API_KEY,
                default=SERVICE_DEFAULTS[CONF_GOOGLE_CSE_API_KEY],
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
            vol.Required(
                CONF_GOOGLE_CSE_CX,
                default=SERVICE_DEFAULTS[CONF_GOOGLE_CSE_CX],
            ): str,
            vol.Required(
                CONF_GOOGLE_CSE_NUM_RESULTS,
                default=SERVICE_DEFAULTS[CONF_GOOGLE_CSE_NUM_RESULTS],
            ): _num_results_selector(),
        }
    )


def get_brave_schema() -> vol.Schema:
    """Schema for Brave Image Search configuration."""
    return vol.Schema(
        {
            vol.Required(
                CONF_BRAVE_API_KEY,
                default=SERVICE_DEFAULTS[CONF_BRAVE_API_KEY],
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
            vol.Required(
                CONF_BRAVE_IMAGE_NUM_RESULTS,
                default=SERVICE_DEFAULTS[CONF_BRAVE_IMAGE_NUM_RESULTS],
            ): _num_results_selector(),
            vol.Required(
                CONF_BRAVE_SAFESEARCH,
                default=SERVICE_DEFAULTS[CONF_BRAVE_SAFESEARCH],
            ): SelectSelector(
                SelectSelectorConfig(
                    mode=SelectSelectorMode.DROPDOWN,
                    options=_options_to_selections(SAFESEARCH_OPTIONS),
                )
            ),
        }
    )


def get_searxng_schema() -> vol.Schema:
    """Schema for SearXNG configuration."""
    return vol.Schema(
        {
            vol.Required(
                CONF_SEARXNG_URL,
                default=SERVICE_DEFAULTS[CONF_SEARXNG_URL],
            ): str,
            vol.Required(
                CONF_SEARXNG_IMAGE_NUM_RESULTS,
                default=SERVICE_DEFAULTS[CONF_SEARXNG_IMAGE_NUM_RESULTS],
            ): _num_results_selector(),
            vol.Optional(
                CONF_SEARXNG_ENGINES,
                default=SERVICE_DEFAULTS[CONF_SEARXNG_ENGINES],
            ): str,
        }
    )


# Map provider to (step_id, schema_func)
PROVIDER_STEP_MAP = {
    CONF_IMAGE_SEARCH_PROVIDER_GOOGLE: (STEP_GOOGLE, get_google_schema),
    CONF_IMAGE_SEARCH_PROVIDER_BRAVE: (STEP_BRAVE, get_brave_schema),
    CONF_IMAGE_SEARCH_PROVIDER_SEARXNG: (STEP_SEARXNG, get_searxng_schema),
}


class HaLlmExtensionsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for LLM Extensions."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.config_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 1: Select provider."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is None:
            return self.async_show_form(
                step_id=STEP_USER,
                data_schema=get_user_schema(),
            )

        self.config_data.update(user_input)
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        provider = user_input.get(CONF_IMAGE_SEARCH_PROVIDER)
        if provider in PROVIDER_STEP_MAP:
            step_id, schema_func = PROVIDER_STEP_MAP[provider]
            return self.async_show_form(
                step_id=step_id,
                data_schema=schema_func(),
            )

        return self.async_create_entry(title=ADDON_NAME, data=self.config_data)

    async def _handle_provider_step(
        self, step_id: str, user_input: dict[str, Any] | None
    ) -> config_entries.ConfigFlowResult:
        """Generic handler for provider config steps."""
        if user_input is None:
            _, schema_func = PROVIDER_STEP_MAP[
                self.config_data[CONF_IMAGE_SEARCH_PROVIDER]
            ]
            return self.async_show_form(
                step_id=step_id,
                data_schema=schema_func(),
            )

        self.config_data.update(user_input)
        return self.async_create_entry(title=ADDON_NAME, data=self.config_data)

    async def async_step_google(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 2: Google Custom Search settings."""
        return await self._handle_provider_step(STEP_GOOGLE, user_input)

    async def async_step_brave(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 2: Brave Image Search settings."""
        return await self._handle_provider_step(STEP_BRAVE, user_input)

    async def async_step_searxng(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 2: SearXNG settings."""
        return await self._handle_provider_step(STEP_SEARXNG, user_input)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow handler."""
        return HaLlmExtensionsOptionsFlow(config_entry)


class HaLlmExtensionsOptionsFlow(config_entries.OptionsFlow):
    """Options flow for reconfiguration."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize the options flow."""
        self.config_data: dict[str, Any] = {
            **config_entry.data,
            **(config_entry.options or {}),
        }

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Options: show provider selection with current values."""
        if user_input is None:
            schema = get_user_schema()
            schema = self.add_suggested_values_to_schema(schema, self.config_data)
            return self.async_show_form(step_id="init", data_schema=schema)

        self.config_data.update(user_input)

        provider = user_input.get(CONF_IMAGE_SEARCH_PROVIDER)
        if provider in PROVIDER_STEP_MAP:
            step_id, schema_func = PROVIDER_STEP_MAP[provider]
            schema = schema_func()
            schema = self.add_suggested_values_to_schema(schema, self.config_data)
            return self.async_show_form(step_id=step_id, data_schema=schema)

        return self.async_create_entry(data=self.config_data)

    async def _handle_provider_step(
        self, step_id: str, user_input: dict[str, Any] | None
    ) -> config_entries.ConfigFlowResult:
        """Generic handler for provider options steps."""
        if user_input is None:
            provider = self.config_data.get(CONF_IMAGE_SEARCH_PROVIDER)
            _, schema_func = PROVIDER_STEP_MAP[provider]
            schema = schema_func()
            schema = self.add_suggested_values_to_schema(schema, self.config_data)
            return self.async_show_form(step_id=step_id, data_schema=schema)

        self.config_data.update(user_input)
        return self.async_create_entry(data=self.config_data)

    async def async_step_google(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Options: Google Custom Search settings."""
        return await self._handle_provider_step(STEP_GOOGLE, user_input)

    async def async_step_brave(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Options: Brave Image Search settings."""
        return await self._handle_provider_step(STEP_BRAVE, user_input)

    async def async_step_searxng(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Options: SearXNG settings."""
        return await self._handle_provider_step(STEP_SEARXNG, user_input)
