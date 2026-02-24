"""Constants for the Voice Satellite Card LLM Tools integration."""

DOMAIN = "voice_satellite_llm_tools"
ADDON_NAME = "Voice Satellite Card LLM Tools"

# Tool type selection
CONF_TOOL_TYPE = "tool_type"
TOOL_TYPE_IMAGE_SEARCH = "image_search"
TOOL_TYPE_VIDEO_SEARCH = "video_search"
TOOL_TYPE_WEB_SEARCH = "web_search"
TOOL_TYPE_WIKIPEDIA = "wikipedia"

CONF_TOOL_TYPES = {
    TOOL_TYPE_IMAGE_SEARCH: "Image Search",
    TOOL_TYPE_VIDEO_SEARCH: "Video Search",
    TOOL_TYPE_WEB_SEARCH: "Web Search",
    TOOL_TYPE_WIKIPEDIA: "Wikipedia",
}

# LLM API identifiers
IMAGE_SEARCH_API_NAME = "Voice Satellite Card: Image Search"
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
VIDEO_SEARCH_API_NAME = "Voice Satellite Card: Video Search"
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
WEB_SEARCH_API_NAME = "Voice Satellite Card: Web Search"
WEB_SEARCH_API_ID = "voice_satellite_llm_tools_web_search"

WEB_SEARCH_SERVICES_PROMPT = (
    "You may use the Web Search tool to search the internet for information. "
    "When the user asks a question that requires current information, facts, or general knowledge "
    "that you are not sure about, use the search_web tool."
)

# Wikipedia Search LLM API identifiers
WIKIPEDIA_API_NAME = "Voice Satellite Card: Wikipedia"
WIKIPEDIA_API_ID = "voice_satellite_llm_tools_wikipedia"

WIKIPEDIA_SERVICES_PROMPT = (
    "You may use the Wikipedia Search tool to look up encyclopedic information. "
    "When the user asks about a topic, person, place, event, or concept that Wikipedia would cover, "
    "use the search_wikipedia tool."
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
