"""Constants for the Voice Satellite LLM Tools integration."""

DOMAIN = "voice_satellite_llm_tools"
ADDON_NAME = "Voice Satellite LLM Tools"
WEATHER_ICONS_PATH = f"/api/{DOMAIN}/weather_icons"

# Tool type selection
CONF_TOOL_TYPE = "tool_type"
TOOL_TYPE_IMAGE_SEARCH = "image_search"
TOOL_TYPE_VIDEO_SEARCH = "video_search"
TOOL_TYPE_WEB_SEARCH = "web_search"
TOOL_TYPE_WIKIPEDIA = "wikipedia"
TOOL_TYPE_WEATHER = "weather"
TOOL_TYPE_FINANCIAL = "financial_data"

TOOL_TYPE_NEWS = "news"
TOOL_TYPE_CALENDAR = "calendar"
TOOL_TYPE_TODO = "todo"
TOOL_TYPE_SPORTS = "sports"

CONF_TOOL_TYPES = {
    TOOL_TYPE_IMAGE_SEARCH: "Image Search",
    TOOL_TYPE_VIDEO_SEARCH: "Video Search",
    TOOL_TYPE_WEB_SEARCH: "Web Search",
    TOOL_TYPE_WIKIPEDIA: "Wikipedia",
    TOOL_TYPE_WEATHER: "Weather Forecast",
    TOOL_TYPE_FINANCIAL: "Financial Data",
    TOOL_TYPE_NEWS: "News Headlines",
    TOOL_TYPE_CALENDAR: "Calendar Events",
    TOOL_TYPE_TODO: "To-do Lists",
    TOOL_TYPE_SPORTS: "Sports Scores",
}

# LLM API identifiers
IMAGE_SEARCH_API_NAME = "Voice Satellite: Image Search"
IMAGE_SEARCH_API_ID = "voice_satellite_llm_tools_image_search"

IMAGE_SEARCH_SERVICES_PROMPT = (
    "You may use the Image Search Services tools to find images on the internet. "
    "When the user asks you to find, search for, or show images, use the search_images tool. "
    "Set auto_display to true when the user wants to see a specific image immediately "
    "(e.g. 'show me the Mona Lisa', 'what does a pangolin look like'). "
    "Set auto_display to false when they want to browse multiple results "
    "(e.g. 'find me pictures of cats', 'search for sunset photos')."
)

# Video Search LLM API identifiers
VIDEO_SEARCH_API_NAME = "Voice Satellite: Video Search"
VIDEO_SEARCH_API_ID = "voice_satellite_llm_tools_video_search"

VIDEO_SEARCH_SERVICES_PROMPT = (
    "You may use the Video Search Services tools to find videos on YouTube. "
    "When the user asks you to find, search for, or show videos, use the search_videos tool. "
    "Set auto_play to true when the user wants to watch a specific video immediately "
    "(e.g. 'play the latest MrBeast video', 'show me that rickroll video'). "
    "Set auto_play to false when they want to browse or explore results "
    "(e.g. 'find me videos about cooking', 'search for guitar tutorials')."
)

# Web Search LLM API identifiers
WEB_SEARCH_API_NAME = "Voice Satellite: Web Search"
WEB_SEARCH_API_ID = "voice_satellite_llm_tools_web_search"

WEB_SEARCH_SERVICES_PROMPT = (
    "You may use the Web Search tool to search the internet for information. "
    "When the user asks a question that requires current information, facts, or general knowledge "
    "that you are not sure about, use the search_web tool."
)

# Wikipedia Search LLM API identifiers
WIKIPEDIA_API_NAME = "Voice Satellite: Wikipedia"
WIKIPEDIA_API_ID = "voice_satellite_llm_tools_wikipedia"

WIKIPEDIA_SERVICES_PROMPT = (
    "You may use the Wikipedia Search tool to look up encyclopedic information. "
    "When the user asks about a topic, person, place, event, or concept that Wikipedia would cover, "
    "use the search_wikipedia tool."
)

# Weather Forecast LLM API identifiers
WEATHER_API_NAME = "Voice Satellite: Weather Forecast"
WEATHER_API_ID = "voice_satellite_llm_tools_weather"

WEATHER_SERVICES_PROMPT = (
    "You may use the Weather Forecast tool to get weather information. "
    "When the user asks about the weather, temperature, or forecast for today, "
    "tomorrow, a specific day of the week, or the upcoming week, use the "
    "get_weather_forecast tool with the appropriate range parameter."
)

# Provider selection
CONF_IMAGE_SEARCH_PROVIDER = "image_search_provider"
CONF_IMAGE_SEARCH_PROVIDER_BRAVE = "Brave"
CONF_IMAGE_SEARCH_PROVIDER_SEARXNG = "SearXNG"

CONF_IMAGE_SEARCH_PROVIDERS = {
    "Brave": CONF_IMAGE_SEARCH_PROVIDER_BRAVE,
    "SearXNG": CONF_IMAGE_SEARCH_PROVIDER_SEARXNG,
}

# Brave Image Search config keys
CONF_BRAVE_API_KEY = "brave_api_key"
CONF_BRAVE_IMAGE_NUM_RESULTS = "brave_image_num_results"
CONF_BRAVE_SAFESEARCH = "brave_safesearch"

# SearXNG config keys
CONF_SEARXNG_URL = "searxng_server_url"
CONF_SEARXNG_IMAGE_NUM_RESULTS = "searxng_image_num_results"
CONF_SEARXNG_ENGINES = "searxng_engines"

# Web Search provider selection
CONF_WEB_SEARCH_PROVIDER = "web_search_provider"
CONF_WEB_SEARCH_PROVIDER_BRAVE = "Brave"
CONF_WEB_SEARCH_PROVIDER_SEARXNG = "SearXNG"

CONF_WEB_SEARCH_PROVIDERS = {
    "Brave": CONF_WEB_SEARCH_PROVIDER_BRAVE,
    "SearXNG": CONF_WEB_SEARCH_PROVIDER_SEARXNG,
}

# Brave Web Search config keys
CONF_BRAVE_WEB_NUM_RESULTS = "brave_web_num_results"

# SearXNG Web Search config keys
CONF_SEARXNG_WEB_NUM_RESULTS = "searxng_web_num_results"
CONF_SEARXNG_WEB_ENGINES = "searxng_web_engines"

# Wikipedia config keys
CONF_WIKIPEDIA_DETAIL = "wikipedia_detail"
WIKIPEDIA_DETAIL_CONCISE = "concise"
WIKIPEDIA_DETAIL_DETAILED = "detailed"

CONF_WIKIPEDIA_DETAIL_OPTIONS = {
    WIKIPEDIA_DETAIL_CONCISE: "Concise",
    WIKIPEDIA_DETAIL_DETAILED: "Detailed",
}

# Financial Data LLM API identifiers
FINANCIAL_API_NAME = "Voice Satellite: Financial Data"
FINANCIAL_API_ID = "voice_satellite_llm_tools_financial"

FINANCIAL_SERVICES_PROMPT = (
    "You may use the Financial Data tool to look up stock prices, cryptocurrency prices, "
    "and convert currencies. "
    "When the user asks about a stock price, cryptocurrency price, market data, "
    "or how a stock or crypto is doing, use the get_financial_data tool with "
    "query_type 'stock' and the ticker symbol (e.g. AAPL, TSLA, BTC, ETH). "
    "When the user asks to convert currencies or about exchange rates, "
    "use the get_financial_data tool with query_type 'currency'."
)

# Financial Data provider selection
CONF_FINANCIAL_PROVIDER = "financial_provider"
CONF_FINANCIAL_PROVIDER_FINNHUB = "Finnhub"

CONF_FINANCIAL_PROVIDERS = {
    "Finnhub": CONF_FINANCIAL_PROVIDER_FINNHUB,
}

# Finnhub config keys
CONF_FINNHUB_API_KEY = "finnhub_api_key"

# Financial Data defaults
FINANCIAL_DEFAULTS = {
    CONF_FINNHUB_API_KEY: "",
}

# Weather Forecast config keys
CONF_DAILY_WEATHER_ENTITY = "daily_weather_entity"
CONF_HOURLY_WEATHER_ENTITY = "hourly_weather_entity"
CONF_WEATHER_TEMPERATURE_SENSOR = "weather_temperature_sensor"
CONF_WEATHER_HUMIDITY_SENSOR = "weather_humidity_sensor"

# YouTube Data API v3 config keys
CONF_YOUTUBE_API_KEY = "youtube_api_key"
CONF_YOUTUBE_NUM_RESULTS = "youtube_num_results"

# Cache config
CONF_CACHE_TTL = "cache_ttl"
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds

# Image search defaults
IMAGE_SEARCH_DEFAULTS = {
    CONF_BRAVE_API_KEY: "",
    CONF_BRAVE_IMAGE_NUM_RESULTS: 3,
    CONF_BRAVE_SAFESEARCH: "moderate",
    CONF_SEARXNG_URL: "",
    CONF_SEARXNG_IMAGE_NUM_RESULTS: 3,
    CONF_SEARXNG_ENGINES: "",
}

# Web search defaults
WEB_SEARCH_DEFAULTS = {
    CONF_BRAVE_API_KEY: "",
    CONF_BRAVE_WEB_NUM_RESULTS: 3,
    CONF_SEARXNG_URL: "",
    CONF_SEARXNG_WEB_NUM_RESULTS: 3,
    CONF_SEARXNG_WEB_ENGINES: "",
}

# Wikipedia defaults
WIKIPEDIA_DEFAULTS = {
    CONF_WIKIPEDIA_DETAIL: WIKIPEDIA_DETAIL_CONCISE,
}

# Video search defaults
VIDEO_SEARCH_DEFAULTS = {
    CONF_YOUTUBE_API_KEY: "",
    CONF_YOUTUBE_NUM_RESULTS: 3,
}

# News Headlines LLM API identifiers
NEWS_API_NAME = "Voice Satellite: News Headlines"
NEWS_API_ID = "voice_satellite_llm_tools_news"

NEWS_SERVICES_PROMPT = (
    "You may use the News Headlines tool to get current news. "
    "When the user asks about news, current events, or what's happening in the world, "
    "use the get_news_headlines tool. "
    "You can optionally filter by topic (query) or category."
)

CONF_NEWSAPI_KEY = "newsapi_key"
CONF_NEWS_NUM_RESULTS = "news_num_results"
CONF_NEWS_COUNTRY = "news_country"

NEWS_DEFAULTS = {
    CONF_NEWSAPI_KEY: "",
    CONF_NEWS_NUM_RESULTS: 5,
    CONF_NEWS_COUNTRY: "us",
}

# Calendar Events LLM API identifiers
CALENDAR_API_NAME = "Voice Satellite: Calendar Events"
CALENDAR_API_ID = "voice_satellite_llm_tools_calendar"

CALENDAR_SERVICES_PROMPT = (
    "You may use the Calendar Events tool to get events from Home Assistant calendars. "
    "When the user asks what's on their calendar, schedule, or agenda, "
    "use the get_calendar_events tool with the appropriate range."
)

CONF_CALENDAR_ENTITIES = "calendar_entities"

# To-do Lists LLM API identifiers
TODO_API_NAME = "Voice Satellite: To-do Lists"
TODO_API_ID = "voice_satellite_llm_tools_todo"

TODO_SERVICES_PROMPT = (
    "You may use the To-do Lists tool to read items from Home Assistant to-do or shopping lists. "
    "When the user asks what's on their shopping list, to-do list, or wants to check their tasks, "
    "use the get_todo_items tool."
)

CONF_TODO_ENTITIES = "todo_entities"

# Sports Scores LLM API identifiers
SPORTS_API_NAME = "Voice Satellite: Sports Scores"
SPORTS_API_ID = "voice_satellite_llm_tools_sports"

SPORTS_SERVICES_PROMPT = (
    "You may use the Sports Scores tool to get today's sports results and scores. "
    "When the user asks about match scores, results, or who won a game, "
    "use the get_sports_scores tool with the appropriate league_id."
)

CONF_SPORTS_LEAGUES = "sports_leagues"

# Maps league_id -> (display_name, ESPN API path)
SPORTS_LEAGUES: dict[str, tuple[str, str]] = {
    "premier_league": ("Premier League", "soccer/eng.1"),
    "la_liga": ("La Liga", "soccer/esp.1"),
    "serie_a": ("Serie A", "soccer/ita.1"),
    "bundesliga": ("Bundesliga", "soccer/ger.1"),
    "ligue_1": ("Ligue 1", "soccer/fra.1"),
    "champions_league": ("UEFA Champions League", "soccer/uefa.champions"),
    "mls": ("MLS", "soccer/usa.1"),
    "nba": ("NBA", "basketball/nba"),
    "nfl": ("NFL", "football/nfl"),
    "mlb": ("MLB", "baseball/mlb"),
    "nhl": ("NHL", "hockey/nhl"),
}

SPORTS_DEFAULTS = {
    CONF_SPORTS_LEAGUES: list(SPORTS_LEAGUES.keys()),
}
