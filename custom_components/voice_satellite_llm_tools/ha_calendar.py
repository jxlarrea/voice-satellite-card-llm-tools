"""Home Assistant Calendar tool."""

import logging
from datetime import timedelta

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm
from homeassistant.util import dt as dt_util

from .base_tool import BaseTool
from .const import CONF_CALENDAR_ENTITIES

_LOGGER = logging.getLogger(__name__)

RANGE_OPTIONS = ["today", "tomorrow", "this_week", "next_7_days"]


class HACalendarTool(BaseTool):
    """Get events from Home Assistant calendar entities."""

    source = "home_assistant"
    name = "get_calendar_events"

    def __init__(self, config: dict, hass: HomeAssistant) -> None:
        super().__init__(config, hass)
        entities = config.get(CONF_CALENDAR_ENTITIES, [])
        if isinstance(entities, str):
            entities = [e.strip() for e in entities.split(",") if e.strip()]
        self._entity_ids: list[str] = list(entities)

        calendar_list = ", ".join(self._entity_ids) if self._entity_ids else "all available"
        self.description = (
            "Get events from your Home Assistant calendars. "
            f"Available calendars: {calendar_list}. "
            "Use 'today', 'tomorrow', 'this_week', or 'next_7_days' as the range."
        )
        self.parameters = vol.Schema(
            {
                vol.Required(
                    "range",
                    description=(
                        "Time range: 'today', 'tomorrow', 'this_week', or 'next_7_days'."
                    ),
                ): vol.In(RANGE_OPTIONS),
                vol.Optional(
                    "calendar_entity",
                    description=(
                        "Specific calendar entity ID to query. "
                        "Omit to query all configured calendars."
                    ),
                ): str,
            }
        )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        range_key = tool_input.tool_args["range"]
        calendar_filter = tool_input.tool_args.get("calendar_entity")

        now = dt_util.now()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if range_key == "today":
            start = today_start
            end = today_start + timedelta(days=1)
        elif range_key == "tomorrow":
            start = today_start + timedelta(days=1)
            end = today_start + timedelta(days=2)
        else:
            start = today_start
            end = today_start + timedelta(days=7)

        entity_ids = list(self._entity_ids)
        if calendar_filter:
            if calendar_filter in entity_ids or not entity_ids:
                entity_ids = [calendar_filter]

        if not entity_ids:
            return {
                "error": (
                    "No calendar entities configured. "
                    "Add calendar entities in the integration settings."
                )
            }

        try:
            result = await hass.services.async_call(
                "calendar",
                "get_events",
                {
                    "start_date_time": start.isoformat(),
                    "end_date_time": end.isoformat(),
                },
                target={"entity_id": entity_ids},
                return_response=True,
                blocking=True,
            )
        except Exception as e:
            _LOGGER.error("Calendar service call failed: %s", e)
            return {"error": f"Failed to retrieve calendar events: {e!s}"}

        all_events = []
        for entity_id, entity_data in (result or {}).items():
            for event in entity_data.get("events", []):
                all_events.append(
                    {
                        "calendar": entity_id,
                        "summary": event.get("summary", ""),
                        "start": event.get("start", ""),
                        "end": event.get("end", ""),
                        "description": event.get("description", ""),
                        "location": event.get("location", ""),
                        "all_day": event.get("all_day", False),
                    }
                )

        all_events.sort(key=lambda e: str(e.get("start", "")))

        return {
            "source": "home_assistant",
            "range": range_key,
            "num_events": len(all_events),
            "events": all_events,
            "instruction": (
                "Summarize the calendar events naturally. "
                "Mention the time and title for each event. "
                "If there are no events, say the schedule is clear for that period."
            ),
        }
