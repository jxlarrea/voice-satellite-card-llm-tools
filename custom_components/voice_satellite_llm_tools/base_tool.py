"""Base tool class for Voice Satellite Card LLM Tools."""

from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm


class BaseTool(llm.Tool):
    """Base class for all tools in this integration."""

    def __init__(self, config: dict, hass: HomeAssistant) -> None:
        """Initialize the tool with config and hass."""
        super().__init__()
        self.config = config
        self.hass = hass
