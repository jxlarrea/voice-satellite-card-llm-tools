"""Weather Forecast tool using Home Assistant weather entities."""

import logging
from datetime import datetime, timedelta

import voluptuous as vol
from homeassistant.components.weather import WeatherEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import llm

from .base_tool import BaseTool
from .const import (
    CONF_DAILY_WEATHER_ENTITY,
    CONF_HOURLY_WEATHER_ENTITY,
    CONF_WEATHER_HUMIDITY_SENSOR,
    CONF_WEATHER_TEMPERATURE_SENSOR,
    WEATHER_ICONS_PATH,
)

_LOGGER = logging.getLogger(__name__)

RANGE_OPTIONS = [
    "week",
    "today",
    "tomorrow",
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

DAY_NAMES = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]

ICON_BASE_URL = WEATHER_ICONS_PATH

# Maps HA weather condition to (day_icon, night_icon)
CONDITION_ICON_MAP = {
    "clear-night": ("clear_night", "clear_night"),
    "cloudy": ("cloudy", "cloudy"),
    "fog": ("haze_fog_dust_smoke", "haze_fog_dust_smoke"),
    "hail": ("mixed_rain_hail_sleet", "mixed_rain_hail_sleet"),
    "lightning": ("isolated_thunderstorms", "isolated_thunderstorms"),
    "lightning-rainy": ("strong_thunderstorms", "strong_thunderstorms"),
    "partlycloudy": ("partly_cloudy_day", "partly_cloudy_night"),
    "pouring": ("heavy_rain", "heavy_rain"),
    "rainy": ("showers_rain", "showers_rain"),
    "snowy": ("heavy_snow", "heavy_snow"),
    "snowy-rainy": ("mixed_rain_snow", "mixed_rain_snow"),
    "sunny": ("clear_day", "clear_day"),
    "windy": ("windy", "windy"),
    "windy-variant": ("windy", "windy"),
    "exceptional": ("tropical_storm_hurricane", "tropical_storm_hurricane"),
}

PRECIPITATION_THRESHOLDS = [
    (0, "no chance"),
    (5, "very unlikely"),
    (15, "unlikely"),
    (30, "possible"),
    (50, "moderate"),
    (70, "likely"),
    (85, "very likely"),
    (95, "extremely likely"),
    (100, "almost guaranteed"),
]


class WeatherForecastTool(BaseTool):
    """Get weather forecast from Home Assistant weather entities."""

    source = "home_assistant"
    name = "get_weather_forecast"
    description = (
        "Get the weather forecast. Use 'week' for the weekly outlook, "
        "'today' or 'tomorrow' for those days, or a day name (monday-sunday) "
        "for a specific upcoming day. If the user says 'tonight', use 'today'."
    )

    parameters = vol.Schema(
        {
            vol.Required(
                "range",
                description=(
                    "The time range: 'week', 'today', 'tomorrow', or a day "
                    "name (monday-sunday)."
                ),
            ): vol.In(RANGE_OPTIONS),
        }
    )

    async def async_call(
        self,
        hass: HomeAssistant,
        tool_input: llm.ToolInput,
        llm_context: llm.LLMContext,
    ) -> dict:
        """Execute the weather forecast tool."""
        range_value = tool_input.tool_args["range"]
        daily_entity = self.config.get(CONF_DAILY_WEATHER_ENTITY, "")
        hourly_entity = self.config.get(CONF_HOURLY_WEATHER_ENTITY, "")
        temp_sensor = self.config.get(CONF_WEATHER_TEMPERATURE_SENSOR, "")
        humidity_sensor = self.config.get(CONF_WEATHER_HUMIDITY_SENSOR, "")

        if not daily_entity:
            return {"error": "No daily weather entity configured."}

        try:
            today = datetime.now().date()
            target_date = self._resolve_target_date(range_value, today)

            use_hourly = (
                range_value != "week"
                and hourly_entity
                and self._entity_supports(
                    hass, hourly_entity, WeatherEntityFeature.FORECAST_HOURLY
                )
            )

            supports_twice_daily = self._entity_supports(
                hass, daily_entity, WeatherEntityFeature.FORECAST_TWICE_DAILY
            )

            if use_hourly:
                raw = await self._fetch_forecast(hass, hourly_entity, "hourly")
                entries = self._filter_by_date(raw, target_date)
                forecast_type = "hourly"
            elif supports_twice_daily and range_value != "week":
                raw = await self._fetch_forecast(
                    hass, daily_entity, "twice_daily"
                )
                entries = self._filter_by_date(raw, target_date)
                forecast_type = "twice_daily"
            else:
                raw = await self._fetch_forecast(hass, daily_entity, "daily")
                if range_value == "week":
                    entries = raw[:7] if raw else []
                else:
                    entries = self._filter_by_date(raw, target_date)
                forecast_type = "daily"

            if not entries:
                return {
                    "source": self.source,
                    "range": range_value,
                    "message": "No forecast data available for the requested range.",
                }

            formatted = self._format_entries(entries, forecast_type)

            first = entries[0]
            condition = first.get("condition", "")
            is_daytime = first.get("is_daytime", True)
            icon_url = self._get_condition_icon_url(condition, is_daytime)

            response = {
                "source": self.source,
                "range": range_value,
                "forecast_type": forecast_type,
                "forecast": formatted,
                "instruction": (
                    "Summarize the weather forecast naturally. Mention temperatures, "
                    "conditions, and precipitation chances. If current humidity is "
                    "provided, mention it as well. Do NOT list raw numbers "
                    "or data verbatim — give a conversational summary."
                ),
            }

            if icon_url:
                response["condition_icon"] = icon_url

            if temp_sensor and range_value in ("today", "week"):
                current = self._get_current_temp(hass, temp_sensor)
                if current is not None:
                    response["current_temperature"] = current

            if humidity_sensor and range_value in ("today", "week"):
                current_humidity = self._get_sensor_value(hass, humidity_sensor)
                if current_humidity is not None:
                    response["current_humidity"] = current_humidity

            return response

        except Exception as e:
            _LOGGER.exception("Weather forecast error: %s", e)
            return {"error": f"Weather forecast failed: {e!s}"}

    @staticmethod
    def _resolve_target_date(range_value: str, today):
        """Resolve the range parameter to a target date."""
        if range_value == "week":
            return None
        if range_value == "today":
            return today
        if range_value == "tomorrow":
            return today + timedelta(days=1)
        if range_value in DAY_NAMES:
            target_weekday = DAY_NAMES.index(range_value)
            days_ahead = (target_weekday - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            return today + timedelta(days=days_ahead)
        return today

    @staticmethod
    def _entity_supports(
        hass: HomeAssistant, entity_id: str, feature: WeatherEntityFeature
    ) -> bool:
        """Check if a weather entity supports a specific feature."""
        state = hass.states.get(entity_id)
        if state is None:
            return False
        return bool(state.attributes.get("supported_features", 0) & feature)

    @staticmethod
    async def _fetch_forecast(
        hass: HomeAssistant, entity_id: str, forecast_type: str
    ) -> list[dict]:
        """Fetch forecast data via the weather.get_forecasts service."""
        result = await hass.services.async_call(
            "weather",
            "get_forecasts",
            {"type": forecast_type, "entity_id": entity_id},
            blocking=True,
            return_response=True,
        )
        return result.get(entity_id, {}).get("forecast", [])

    @staticmethod
    def _filter_by_date(forecast_data: list[dict], target_date) -> list[dict]:
        """Filter forecast entries to those matching the target date."""
        if target_date is None:
            return forecast_data
        filtered = []
        for entry in forecast_data:
            dt_str = entry.get("datetime", "")
            if not dt_str:
                continue
            try:
                if datetime.fromisoformat(dt_str).date() == target_date:
                    filtered.append(entry)
            except (ValueError, TypeError):
                continue
        return filtered

    @staticmethod
    def _get_current_temp(hass: HomeAssistant, entity_id: str) -> str | None:
        """Get current temperature from a sensor entity."""
        return WeatherForecastTool._get_sensor_value(hass, entity_id)

    @staticmethod
    def _get_sensor_value(hass: HomeAssistant, entity_id: str) -> str | None:
        """Get formatted value from a sensor entity."""
        state = hass.states.get(entity_id)
        if state is None or state.state in ("unavailable", "unknown"):
            return None
        unit = state.attributes.get("unit_of_measurement", "")
        try:
            return f"{round(float(state.state))}{unit}"
        except (ValueError, TypeError):
            return None

    @staticmethod
    def _get_condition_icon_url(
        condition: str, is_daytime: bool = True
    ) -> str | None:
        """Get the local icon URL for a weather condition."""
        icons = CONDITION_ICON_MAP.get(condition)
        if not icons:
            return None
        icon_name = icons[0] if is_daytime else icons[1]
        return f"{ICON_BASE_URL}/{icon_name}.svg"

    @staticmethod
    def _describe_precipitation(probability) -> str | None:
        """Convert precipitation probability to natural language."""
        if probability is None:
            return None
        try:
            prob = int(probability)
        except (ValueError, TypeError):
            return None
        for threshold, description in PRECIPITATION_THRESHOLDS:
            if prob <= threshold:
                return description
        return "almost guaranteed"

    def _format_entries(self, entries: list[dict], forecast_type: str) -> list[dict]:
        """Format raw forecast entries for the LLM."""
        formatted = []
        for entry in entries:
            item = {}

            dt_str = entry.get("datetime", "")
            if dt_str:
                try:
                    dt = datetime.fromisoformat(dt_str)
                    if forecast_type == "hourly":
                        item["time"] = dt.strftime("%-I%p").lower()
                    else:
                        item["date"] = dt.strftime("%A")
                except (ValueError, TypeError):
                    item["datetime"] = dt_str

            item["condition"] = entry.get("condition", "")

            temp = entry.get("temperature")
            templow = entry.get("templow")
            if temp is not None:
                if templow is not None:
                    item["temperature"] = f"{round(templow)} - {round(temp)}"
                else:
                    item["temperature"] = str(round(temp))

            if forecast_type == "twice_daily":
                item["is_daytime"] = entry.get("is_daytime")

            precip = entry.get("precipitation_probability")
            desc = self._describe_precipitation(precip)
            if desc:
                item["precipitation"] = desc

            if entry.get("humidity") is not None:
                item["humidity"] = f"{entry['humidity']}%"

            if entry.get("wind_speed") is not None:
                item["wind_speed"] = entry["wind_speed"]

            formatted.append(item)
        return formatted
