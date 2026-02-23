"""Constants for the LLM Extensions integration."""

DOMAIN = "ha_llm_extensions"
ADDON_NAME = "LLM Extensions"

# LLM API identifiers
IMAGE_SEARCH_API_NAME = "Image Search Services"
IMAGE_SEARCH_API_ID = "ha_llm_extensions_image_search"

IMAGE_SEARCH_SERVICES_PROMPT = (
    "You may use the Image Search Services tools to find images on the internet. "
    "When the user asks you to find, search for, or show images, use the search_images tool."
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

# Cache config
CONF_CACHE_TTL = "cache_ttl"
DEFAULT_CACHE_TTL = 3600  # 1 hour in seconds

# Service defaults
SERVICE_DEFAULTS = {
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
