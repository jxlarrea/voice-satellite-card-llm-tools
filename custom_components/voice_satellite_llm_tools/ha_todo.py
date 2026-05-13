"""Home Assistant To-do / Shopping List tool."""

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .base_tool import BaseTool
from .const import CONF_TODO_ENTITIES

_LOGGER = logging.getLogger(__name__)

_STATUS_MAP = {
    "incomplete": ["needsAction"],
    "completed": ["completed"],
    "all": ["needsAction", "completed"],
}


class HATodoTool(BaseTool):
    """Get items from Home Assistant to-do or shopping list entities."""

    source = "home_assistant"
    name = "get_todo_items"

    def __init__(self, config: dict, hass: HomeAssistant) -> None:
        super().__init__(config, hass)
        entities = config.get(CONF_TODO_ENTITIES, [])
        if isinstance(entities, str):
            entities = [e.strip() for e in entities.split(",") if e.strip()]
        self._entity_ids: list[str] = list(entities)

        list_names = ", ".join(self._entity_ids) if self._entity_ids else "all configured lists"
        self.description = (
            "Get items from your Home Assistant to-do or shopping lists. "
            f"Available lists: {list_names}. "
            "Can filter by completion status."
        )
        self.parameters = vol.Schema(
            {
                vol.Optional(
                    "list_entity",
                    description=(
                        "Specific to-do list entity ID. "
                        "Omit to query all configured lists."
                    ),
                ): str,
                vol.Optional(
                    "status",
                    description=(
                        "Filter by status: 'incomplete' (default), 'completed', or 'all'."
                    ),
                    default="incomplete",
                ): vol.In(["incomplete", "completed", "all"]),
            }
        )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        status_key = tool_input.tool_args.get("status", "incomplete")
        list_filter = tool_input.tool_args.get("list_entity")

        entity_ids = list(self._entity_ids)
        if list_filter:
            if list_filter in entity_ids or not entity_ids:
                entity_ids = [list_filter]

        if not entity_ids:
            return {"error": "No to-do list entities configured."}

        status_values = _STATUS_MAP.get(status_key, ["needsAction"])

        try:
            result = await hass.services.async_call(
                "todo",
                "get_items",
                {"status": status_values},
                target={"entity_id": entity_ids},
                return_response=True,
                blocking=True,
            )
        except Exception as e:
            _LOGGER.error("Todo service call failed: %s", e)
            return {"error": f"Failed to retrieve to-do items: {e!s}"}

        all_items = []
        for entity_id, entity_data in (result or {}).items():
            for item in entity_data.get("items", []):
                all_items.append(
                    {
                        "list": entity_id,
                        "summary": item.get("summary", ""),
                        "status": item.get("status", ""),
                        "description": item.get("description", ""),
                        "due": item.get("due", ""),
                    }
                )

        return {
            "source": "home_assistant",
            "status_filter": status_key,
            "num_items": len(all_items),
            "items": all_items,
            "instruction": (
                "Read out the list items naturally. "
                "Group by list if multiple lists are present. "
                "If the list is empty, say so clearly."
            ),
        }
