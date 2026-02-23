"""Config flow for Voice Satellite Card LLM Tools."""

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
    CONF_BRAVE_API_KEY,
    CONF_BRAVE_IMAGE_NUM_RESULTS,
    CONF_BRAVE_SAFESEARCH,
    CONF_IMAGE_SEARCH_PROVIDER,
    CONF_IMAGE_SEARCH_PROVIDER_BRAVE,
    CONF_IMAGE_SEARCH_PROVIDER_SEARXNG,
    CONF_IMAGE_SEARCH_PROVIDERS,
    CONF_SEARXNG_ENGINES,
    CONF_SEARXNG_IMAGE_NUM_RESULTS,
    CONF_SEARXNG_URL,
    CONF_TOOL_TYPE,
    CONF_TOOL_TYPES,
    CONF_YOUTUBE_API_KEY,
    CONF_YOUTUBE_NUM_RESULTS,
    DOMAIN,
    IMAGE_SEARCH_DEFAULTS,
    TOOL_TYPE_IMAGE_SEARCH,
    TOOL_TYPE_VIDEO_SEARCH,
    VIDEO_SEARCH_DEFAULTS,
)

_LOGGER = logging.getLogger(__name__)

# Step identifiers
STEP_USER = "user"
STEP_IMAGE_PROVIDER = "image_provider"
STEP_BRAVE = "brave"
STEP_SEARXNG = "searxng"
STEP_YOUTUBE = "youtube"

SAFESEARCH_OPTIONS = {
    "off": "Off",
    "moderate": "Moderate",
    "strict": "Strict",
}


def _options_to_selections(opts: dict) -> list[SelectOptionDict]:
    """Convert a dict to a list of SelectOptionDict."""
    return [SelectOptionDict(value=key, label=val) for key, val in opts.items()]


def _num_results_selector(unit: str = "images") -> NumberSelector:
    """Create a number selector for result count (1-10)."""
    return NumberSelector(
        NumberSelectorConfig(
            min=1,
            max=10,
            step=1,
            mode=NumberSelectorMode.SLIDER,
            unit_of_measurement=unit,
        )
    )


def get_tool_type_schema() -> vol.Schema:
    """Schema for tool type selection step."""
    return vol.Schema(
        {
            vol.Required(CONF_TOOL_TYPE): SelectSelector(
                SelectSelectorConfig(
                    mode=SelectSelectorMode.DROPDOWN,
                    options=_options_to_selections(CONF_TOOL_TYPES),
                )
            ),
        }
    )


def get_image_provider_schema() -> vol.Schema:
    """Schema for image search provider selection step."""
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


def get_brave_schema(defaults: dict | None = None) -> vol.Schema:
    """Schema for Brave Image Search configuration."""
    d = defaults or IMAGE_SEARCH_DEFAULTS
    return vol.Schema(
        {
            vol.Required(
                CONF_BRAVE_API_KEY,
                default=d.get(CONF_BRAVE_API_KEY, ""),
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
            vol.Required(
                CONF_BRAVE_IMAGE_NUM_RESULTS,
                default=d.get(CONF_BRAVE_IMAGE_NUM_RESULTS, 3),
            ): _num_results_selector(),
            vol.Required(
                CONF_BRAVE_SAFESEARCH,
                default=d.get(CONF_BRAVE_SAFESEARCH, "moderate"),
            ): SelectSelector(
                SelectSelectorConfig(
                    mode=SelectSelectorMode.DROPDOWN,
                    options=_options_to_selections(SAFESEARCH_OPTIONS),
                )
            ),
        }
    )


def get_searxng_schema(defaults: dict | None = None) -> vol.Schema:
    """Schema for SearXNG configuration."""
    d = defaults or IMAGE_SEARCH_DEFAULTS
    return vol.Schema(
        {
            vol.Required(
                CONF_SEARXNG_URL,
                default=d.get(CONF_SEARXNG_URL, ""),
            ): str,
            vol.Required(
                CONF_SEARXNG_IMAGE_NUM_RESULTS,
                default=d.get(CONF_SEARXNG_IMAGE_NUM_RESULTS, 3),
            ): _num_results_selector(),
            vol.Optional(
                CONF_SEARXNG_ENGINES,
                default=d.get(CONF_SEARXNG_ENGINES, ""),
            ): str,
        }
    )


def get_youtube_schema(defaults: dict | None = None) -> vol.Schema:
    """Schema for YouTube Data API v3 configuration."""
    d = defaults or VIDEO_SEARCH_DEFAULTS
    return vol.Schema(
        {
            vol.Required(
                CONF_YOUTUBE_API_KEY,
                default=d.get(CONF_YOUTUBE_API_KEY, ""),
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
            vol.Required(
                CONF_YOUTUBE_NUM_RESULTS,
                default=d.get(CONF_YOUTUBE_NUM_RESULTS, 3),
            ): _num_results_selector(unit="videos"),
        }
    )


# Map provider to (step_id, schema_func)
PROVIDER_STEP_MAP = {
    CONF_IMAGE_SEARCH_PROVIDER_BRAVE: (STEP_BRAVE, get_brave_schema),
    CONF_IMAGE_SEARCH_PROVIDER_SEARXNG: (STEP_SEARXNG, get_searxng_schema),
}


class VoiceSatelliteLlmToolsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Voice Satellite Card LLM Tools."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self.config_data: dict[str, Any] = {}

    def _existing_entry_for_tool_type(self, tool_type: str) -> bool:
        """Check if an entry already exists for the given tool type."""
        for entry in self._async_current_entries():
            if entry.data.get(CONF_TOOL_TYPE) == tool_type:
                return True
        return False

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 1: Select tool type (Image Search or Video Search)."""
        if user_input is None:
            return self.async_show_form(
                step_id=STEP_USER,
                data_schema=get_tool_type_schema(),
            )

        tool_type = user_input.get(CONF_TOOL_TYPE)
        self.config_data[CONF_TOOL_TYPE] = tool_type

        if tool_type == TOOL_TYPE_IMAGE_SEARCH:
            if self._existing_entry_for_tool_type(TOOL_TYPE_IMAGE_SEARCH):
                return self.async_abort(reason="image_search_already_configured")
            return self.async_show_form(
                step_id=STEP_IMAGE_PROVIDER,
                data_schema=get_image_provider_schema(),
            )

        if tool_type == TOOL_TYPE_VIDEO_SEARCH:
            if self._existing_entry_for_tool_type(TOOL_TYPE_VIDEO_SEARCH):
                return self.async_abort(reason="video_search_already_configured")
            return self.async_show_form(
                step_id=STEP_YOUTUBE,
                data_schema=get_youtube_schema(),
            )

        return self.async_abort(reason="unknown_tool_type")

    async def async_step_image_provider(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Step 2 (image): Select image search provider."""
        if user_input is None:
            return self.async_show_form(
                step_id=STEP_IMAGE_PROVIDER,
                data_schema=get_image_provider_schema(),
            )

        self.config_data.update(user_input)
        provider = user_input.get(CONF_IMAGE_SEARCH_PROVIDER)

        if provider in PROVIDER_STEP_MAP:
            step_id, schema_func = PROVIDER_STEP_MAP[provider]
            return self.async_show_form(
                step_id=step_id,
                data_schema=schema_func(),
            )

        return self.async_abort(reason="unknown_provider")

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
        provider = self.config_data.get(CONF_IMAGE_SEARCH_PROVIDER, "")
        title = f"Image Search - {provider}"
        await self.async_set_unique_id(f"{DOMAIN}_image_search")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=title, data=self.config_data)

    async def async_step_brave(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Configure Brave Image Search settings."""
        return await self._handle_provider_step(STEP_BRAVE, user_input)

    async def async_step_searxng(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Configure SearXNG settings."""
        return await self._handle_provider_step(STEP_SEARXNG, user_input)

    async def async_step_youtube(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Configure YouTube Video Search settings."""
        if user_input is None:
            return self.async_show_form(
                step_id=STEP_YOUTUBE,
                data_schema=get_youtube_schema(),
            )

        self.config_data.update(user_input)
        await self.async_set_unique_id(f"{DOMAIN}_video_search")
        self._abort_if_unique_id_configured()
        return self.async_create_entry(
            title="Video Search - YouTube", data=self.config_data
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Get the options flow handler."""
        return VoiceSatelliteLlmToolsOptionsFlow(config_entry)


class VoiceSatelliteLlmToolsOptionsFlow(config_entries.OptionsFlow):
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
        """Route to the appropriate options step based on tool type."""
        tool_type = self.config_data.get(CONF_TOOL_TYPE)

        if tool_type == TOOL_TYPE_IMAGE_SEARCH:
            return await self.async_step_image_provider(user_input)

        if tool_type == TOOL_TYPE_VIDEO_SEARCH:
            return await self.async_step_youtube(user_input)

        return self.async_abort(reason="unknown_tool_type")

    async def async_step_image_provider(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Options: show image provider selection with current values."""
        if user_input is None:
            schema = get_image_provider_schema()
            schema = self.add_suggested_values_to_schema(schema, self.config_data)
            return self.async_show_form(
                step_id=STEP_IMAGE_PROVIDER, data_schema=schema
            )

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
        provider = self.config_data.get(CONF_IMAGE_SEARCH_PROVIDER, "")
        title = f"Image Search - {provider}"
        self.hass.config_entries.async_update_entry(
            self.config_entry, title=title
        )
        return self.async_create_entry(data=self.config_data)

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

    async def async_step_youtube(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Options: YouTube Video Search settings."""
        if user_input is None:
            schema = get_youtube_schema()
            schema = self.add_suggested_values_to_schema(schema, self.config_data)
            return self.async_show_form(step_id=STEP_YOUTUBE, data_schema=schema)

        self.config_data.update(user_input)
        return self.async_create_entry(data=self.config_data)
