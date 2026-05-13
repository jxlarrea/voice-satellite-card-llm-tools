"""Sports scores tool using ESPN unofficial scoreboard API."""

import logging

import voluptuous as vol
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .base_tool import BaseTool
from .const import CONF_SPORTS_LEAGUES, SPORTS_LEAGUES
from .http_helpers import fetch_json

_LOGGER = logging.getLogger(__name__)

ESPN_BASE = "https://site.api.espn.com/apis/site/v2/sports"


class SportsScoresTool(BaseTool):
    """Get today's sports scores from the ESPN scoreboard API."""

    source = "espn"
    name = "get_sports_scores"

    def __init__(self, config: dict, hass: HomeAssistant) -> None:
        super().__init__(config, hass)
        configured = config.get(CONF_SPORTS_LEAGUES, list(SPORTS_LEAGUES.keys()))
        if isinstance(configured, str):
            configured = [lid.strip() for lid in configured.split(",") if lid.strip()]
        valid = [lid for lid in configured if lid in SPORTS_LEAGUES] or list(
            SPORTS_LEAGUES.keys()
        )
        self._valid_leagues = valid

        league_names = [SPORTS_LEAGUES[lid][0] for lid in valid]
        self.description = (
            "Get today's sports scores and match results. "
            f"Available leagues: {', '.join(league_names)}."
        )
        self.parameters = vol.Schema(
            {
                vol.Required(
                    "league_id",
                    description=f"League to query. One of: {', '.join(valid)}.",
                ): vol.In(valid),
            }
        )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        league_id = tool_input.tool_args["league_id"]

        if league_id not in SPORTS_LEAGUES:
            return {"error": f"Unknown league: {league_id}"}

        league_name, espn_path = SPORTS_LEAGUES[league_id]
        url = f"{ESPN_BASE}/{espn_path}/scoreboard"

        try:
            data = await fetch_json(hass, url)
        except Exception as e:
            _LOGGER.error("ESPN API failed for %s: %s", league_id, e)
            return {"error": f"Failed to retrieve scores for {league_name}: {e!s}"}

        events = data.get("events", [])
        if not events:
            return {
                "source": "espn",
                "league": league_name,
                "league_id": league_id,
                "message": f"No matches scheduled today for {league_name}.",
                "matches": [],
            }

        matches = []
        for event in events:
            competitions = event.get("competitions", [])
            if not competitions:
                continue
            comp = competitions[0]
            competitors = comp.get("competitors", [])
            if len(competitors) < 2:
                continue

            home = next(
                (c for c in competitors if c.get("homeAway") == "home"), competitors[0]
            )
            away = next(
                (c for c in competitors if c.get("homeAway") == "away"), competitors[1]
            )

            status_type = event.get("status", {}).get("type", {})

            matches.append(
                {
                    "home_team": home.get("team", {}).get("displayName", ""),
                    "away_team": away.get("team", {}).get("displayName", ""),
                    "home_score": home.get("score", ""),
                    "away_score": away.get("score", ""),
                    "status": status_type.get("description", ""),
                    "is_final": status_type.get("completed", False),
                    "date": event.get("date", ""),
                    "venue": comp.get("venue", {}).get("fullName", ""),
                }
            )

        return {
            "source": "espn",
            "league": league_name,
            "league_id": league_id,
            "num_matches": len(matches),
            "matches": matches,
            "instruction": (
                "Read out the scores naturally. "
                "For completed matches say 'X beat Y N-M' or 'X and Y drew N-N'. "
                "For live matches mention the current score and that it's in progress. "
                "For upcoming matches mention the teams and kick-off time."
            ),
        }
