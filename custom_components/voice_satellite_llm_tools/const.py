"""Constants for the Voice Satellite Card LLM Tools integration."""

DOMAIN = "voice_satellite_llm_tools"
ADDON_NAME = "Voice Satellite Card LLM Tools"

# Tool type selection
CONF_TOOL_TYPE = "tool_type"
TOOL_TYPE_IMAGE_SEARCH = "image_search"
TOOL_TYPE_VIDEO_SEARCH = "video_search"

CONF_TOOL_TYPES = {
    "Image Search": TOOL_TYPE_IMAGE_SEARCH,
    "Video Search": TOOL_TYPE_VIDEO_SEARCH,
}

# LLM API identifiers
IMAGE_SEARCH_API_NAME = "Image Search Services"
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
VIDEO_SEARCH_API_NAME = "Video Search Services"
VIDEO_SEARCH_API_ID = "voice_satellite_llm_tools_video_search"

VIDEO_SEARCH_SERVICES_PROMPT = (
    "You may use the Video Search Services tools to find videos on YouTube. "
    "When the user asks you to find, search for, or show videos, use the search_videos tool. "
    "Set auto_play to true when the user wants to watch a specific video immediately "
    "(e.g. 'play the latest MrBeast video', 'show me that rickroll video'). "
    "Set auto_play to false when they want to browse or explore results "
    "(e.g. 'find me videos about cooking', 'search for guitar tutorials')."
)

# Provider selection
CONF_IMAGE_SEARCH_PROVIDER = "image_search_provider"
CONF_IMAGE_SEARCH_PROVIDER_GOOGLE = "Google"
CONF_IMAGE_SEARCH_PROVIDER_BRAVE = "Brave"
CONF_IMAGE_SEARCH_PROVIDER_SEARXNG = "SearXNG"

CONF_IMAGE_SEARCH_PROVIDERS = {
    "Google": CONF_IMAGE_SEARCH_PROVIDER_GOOGLE,
    "Brave": CONF_IMAGE_SEARCH_PROVIDER_BRAVE,
    "SearXNG": CONF_IMAGE_SEARCH_PROVIDER_SEARXNG,
}

# Google Custom Search config keys
CONF_GOOGLE_CSE_API_KEY = "google_cse_api_key"
CONF_GOOGLE_CSE_CX = "google_cse_cx"
CONF_GOOGLE_CSE_NUM_RESULTS = "google_cse_num_results"

# Brave Image Search config keys
CONF_BRAVE_API_KEY = "brave_api_key"
CONF_BRAVE_IMAGE_NUM_RESULTS = "brave_image_num_results"
CONF_BRAVE_SAFESEARCH = "brave_safesearch"

# SearXNG config keys
CONF_SEARXNG_URL = "searxng_server_url"
CONF_SEARXNG_IMAGE_NUM_RESULTS = "searxng_image_num_results"
CONF_SEARXNG_ENGINES = "searxng_engines"

# YouTube Data API v3 config keys
CONF_YOUTUBE_API_KEY = "youtube_api_key"
CONF_YOUTUBE_NUM_RESULTS = "youtube_num_results"

# Cache config
CONF_CACHE_TTL = "cache_ttl"
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds

# Image search defaults
IMAGE_SEARCH_DEFAULTS = {
    CONF_GOOGLE_CSE_API_KEY: "",
    CONF_GOOGLE_CSE_CX: "",
    CONF_GOOGLE_CSE_NUM_RESULTS: 3,
    CONF_BRAVE_API_KEY: "",
    CONF_BRAVE_IMAGE_NUM_RESULTS: 3,
    CONF_BRAVE_SAFESEARCH: "moderate",
    CONF_SEARXNG_URL: "",
    CONF_SEARXNG_IMAGE_NUM_RESULTS: 3,
    CONF_SEARXNG_ENGINES: "",
}

# Video search defaults
VIDEO_SEARCH_DEFAULTS = {
    CONF_YOUTUBE_API_KEY: "",
    CONF_YOUTUBE_NUM_RESULTS: 3,
}
