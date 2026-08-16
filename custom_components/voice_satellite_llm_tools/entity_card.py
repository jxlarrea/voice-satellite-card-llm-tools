"""Entity Card tool - draws Home Assistant entities on the satellite screen.

Returns a Lovelace card config under the `card` key, which Voice Satellite
mounts in its media panel.  Assistants without a screen ignore the key and
still get the entity states as text, so the spoken answer is unaffected.

The card is picked from the entities themselves rather than by the model:
cameras become picture cards, a history request becomes a graph, one
entity becomes a tile, several become an entities list.  The model only
says what to show and, optionally, whether it wants history.
"""

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .base_tool import BaseTool
from .const import (
    CONF_ENTITY_CARD_HISTORY_HOURS,
    CONF_ENTITY_CARD_MAX_ENTITIES,
    DEFAULT_ENTITY_CARD_HISTORY_HOURS,
    DEFAULT_ENTITY_CARD_MAX_ENTITIES,
)

_LOGGER = logging.getLogger(__name__)

DISPLAY_AUTO = "auto"
DISPLAY_HISTORY = "history"
DISPLAY_OPTIONS = [DISPLAY_AUTO, DISPLAY_HISTORY]


def _is_exposed(hass: HomeAssistant, entity_id: str) -> bool:
    """Whether the entity is exposed to the conversation agent.

    The model should only be able to draw what the user already shared
    with it, so a hallucinated (but real) entity id can't be put on
    screen.  If the exposure helper is unavailable we allow the entity:
    failing closed here would break the tool entirely on a setup where
    the helper moved, and the card only ever displays state.
    """
    try:
        from homeassistant.components.homeassistant.exposed_entities import (
            async_should_expose,
        )
    except ImportError:  # pragma: no cover - depends on HA internals
        _LOGGER.debug("Exposure helper unavailable, skipping exposure check")
        return True
    return async_should_expose(hass, "conversation", entity_id)


class EntityCardTool(BaseTool):
    """Show Home Assistant entities as a card on the satellite screen."""

    source = "home_assistant"
    name = "show_entity_card"
    description = (
        "Put Home Assistant entities on the screen of the device the user "
        "is talking to. Use this for 'show me', 'display', 'pull up', "
        "'let me see', and 'what does X look like' requests, including "
        "cameras. Pass the device name and its domain, the same way you "
        "would to HassTurnOn, e.g. name='Front Door Camera', "
        "domain='camera'. An entity ID works as the name too. "
        "This tool only displays: it never turns anything on or off. "
        "Cameras cannot be turned on, so never use a turn-on tool to show "
        "a camera - use this tool instead. "
        "Also answer normally in speech: the card is a visual extra, not a "
        "replacement for your spoken reply."
    )

    # Flat scalars only.  An array parameter is legal JSON schema, but the
    # chat templates local models are served with (Gemma, Qwen, Llama on
    # llama.cpp) render tools as simple signatures and emit array args
    # unreliably, so a list parameter can cost the tool a call it should
    # have won.  Every other tool in this integration is scalar too.
    parameters = vol.Schema(
        {
            vol.Required(
                "name",
                description=(
                    "Name of the thing to show, exactly as it appears in the "
                    "list of devices, e.g. 'Front Door Camera'. An entity ID "
                    "such as 'camera.front_door' is accepted too. To show "
                    "several, separate them with commas."
                ),
            ): str,
            vol.Optional(
                "domain",
                description=(
                    "Domain of the thing to show, e.g. 'camera', 'sensor', "
                    "'light'. Narrows the match when several devices share a "
                    "name."
                ),
            ): str,
            vol.Optional(
                "display",
                description=(
                    "'auto' shows current state (default). 'history' shows a "
                    "graph over time - use it when the user asks about a "
                    "trend, history, or how something changed."
                ),
            ): vol.In(DISPLAY_OPTIONS),
            vol.Optional(
                "title",
                description="Optional heading for the card, e.g. 'Kitchen'.",
            ): str,
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Resolve the entities and build a card config for them."""
        # Accept every shape a model might reach for: the documented
        # comma-separated name string, a list, or the entity_id spelling.
        raw = tool_input.tool_args.get("name")
        for key in ("entity_id", "entity_ids"):
            if raw is None:
                raw = tool_input.tool_args.get(key)
        if isinstance(raw, str):
            requested = raw.split(",")
        elif isinstance(raw, list):
            requested = raw
        else:
            requested = []

        domain = tool_input.tool_args.get("domain")
        # HassTurnOn takes domain as a list, so a model copying that habit
        # will send one here too.
        if isinstance(domain, list):
            domain = domain[0] if domain else None
        domain = (domain or "").strip().lower() or None

        display = tool_input.tool_args.get("display", DISPLAY_AUTO)
        title = (tool_input.tool_args.get("title") or "").strip()

        max_entities = int(
            self.config.get(
                CONF_ENTITY_CARD_MAX_ENTITIES, DEFAULT_ENTITY_CARD_MAX_ENTITIES
            )
        )

        resolved: list[dict] = []
        skipped: list[str] = []

        for term in requested:
            if not isinstance(term, str):
                continue
            term = term.strip()
            if not term:
                continue
            state = self._resolve(hass, term, domain)
            if state is None:
                skipped.append(term)
                continue
            if any(e["entity_id"] == state.entity_id for e in resolved):
                continue
            resolved.append(
                {
                    "entity_id": state.entity_id,
                    "name": state.attributes.get(
                        "friendly_name", state.entity_id
                    ),
                    "state": state.state,
                }
            )

        if not resolved:
            return {
                "error": "No matching entities are available on this system.",
                "not_found": skipped,
            }

        truncated = resolved[max_entities:]
        resolved = resolved[:max_entities]
        entity_ids = [e["entity_id"] for e in resolved]

        result: dict = {
            "entities": resolved,
            "card": self._build_card(entity_ids, display, title),
        }
        if skipped:
            result["not_found"] = skipped
        if truncated:
            result["omitted"] = [e["entity_id"] for e in truncated]

        return result

    def _resolve(self, hass: HomeAssistant, term: str, domain: str | None):
        """Find the exposed entity a model's name or entity ID refers to.

        The assistant is given entities by name, not by entity ID (see the
        static context HA builds for the conversation agent), so a name is
        the argument a model can actually produce.  Matching walks from
        strictest to loosest: exact entity ID, exact friendly name, then a
        substring, so 'doorbell camera' finds 'G4 Doorbell Pro Low
        resolution channel' without a name match beating an ID match.
        """
        lowered = term.lower()
        candidates = []

        for state in hass.states.async_all():
            if domain and state.domain != domain:
                continue
            if not _is_exposed(hass, state.entity_id):
                continue
            if state.entity_id.lower() == lowered:
                return state
            candidates.append(state)

        def names(state) -> list[str]:
            found = [state.attributes.get("friendly_name") or ""]
            aliases = state.attributes.get("aliases")
            if isinstance(aliases, list):
                found.extend(a for a in aliases if isinstance(a, str))
            return [n.lower() for n in found if n]

        for state in candidates:
            if lowered in names(state):
                return state

        # Substring both ways: the model may shorten a long friendly name
        # ('doorbell camera') or pad a short one ('the office light').
        for state in candidates:
            for name in names(state):
                if lowered in name or name in lowered:
                    return state

        return None

    def _build_card(
        self, entity_ids: list[str], display: str, title: str
    ) -> dict:
        """Pick the card that fits these entities."""
        if display == DISPLAY_HISTORY:
            hours = int(
                self.config.get(
                    CONF_ENTITY_CARD_HISTORY_HOURS,
                    DEFAULT_ENTITY_CARD_HISTORY_HOURS,
                )
            )
            card: dict = {
                "type": "history-graph",
                "hours_to_show": hours,
                "entities": entity_ids,
            }
            if title:
                card["title"] = title
            return card

        cameras = [e for e in entity_ids if e.startswith("camera.")]
        if cameras and len(cameras) == len(entity_ids):
            picture_cards = [
                {
                    "type": "picture-entity",
                    "entity": entity_id,
                    "camera_view": "live",
                    # Fit the whole frame rather than cropping to fill:
                    # the panel is a fixed width, and "cover" overflows it
                    # into a scrollbar.
                    "fit_mode": "contain",
                    # No footer: the assistant just said which camera this
                    # is, and the satellite shows one card at a time.
                    "show_state": False,
                    "show_name": False,
                }
                for entity_id in cameras
            ]
            if len(picture_cards) == 1:
                return picture_cards[0]
            return {"type": "grid", "columns": 2, "square": False,
                    "cards": picture_cards}

        if len(entity_ids) == 1:
            return {"type": "tile", "entity": entity_ids[0]}

        card = {"type": "entities", "entities": entity_ids}
        if title:
            card["title"] = title
        return card
