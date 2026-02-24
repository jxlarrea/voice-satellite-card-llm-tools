# Voice Satellite Card - LLM Tools

Extend your voice assistant's capabilities with **image and video search tools** for Home Assistant's LLM integrations. When paired with the [Voice Satellite Card](https://github.com/jxlarrea/voice-satellite-card-integration), search results are displayed directly in the card UI — just ask your assistant to find images or videos and see them on screen.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-blue.svg?style=for-the-badge)](https://www.hacs.xyz/docs/faq/custom_repositories/)
[![Downloads](https://img.shields.io/github/downloads/jxlarrea/voice-satellite-card-llm-tools/total?style=for-the-badge&label=Downloads&color=red)](https://github.com/jxlarrea/voice-satellite-card-llm-tools/releases)
[![version](https://shields.io/github/v/release/jxlarrea/voice-satellite-card-llm-tools?style=for-the-badge&color=orange)](https://github.com/jxlarrea/voice-satellite-card-llm-tools/releases)
[![Latest Release](https://img.shields.io/badge/dynamic/json?style=for-the-badge&color=41BDF5&logo=home-assistant&label=home%20assistant&suffix=%20installs&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.voice_satellite_llm_tools.total)](https://analytics.home-assistant.io/custom_integrations.json)
[![Build](https://img.shields.io/github/actions/workflow/status/jxlarrea/voice-satellite-card-llm-tools/release.yml?style=for-the-badge&label=Build)](https://github.com/jxlarrea/voice-satellite-card-llm-tools/actions/workflows/release.yml)

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/jxlarrea)

## How It Works

This integration registers additional **LLM API tools** with Home Assistant. When a conversation agent (OpenAI, Google Generative AI, Anthropic, Ollama, etc.) receives a request to find images or videos, it can call these tools to fetch results from the configured search providers. The Voice Satellite Card then renders the results visually.

**Example voice commands:**

- "Show me pictures of golden retrievers"
- "Find images of the Eiffel Tower at night"
- "Search for videos on how to make sourdough bread"

## Important

> **This integration requires the [Voice Satellite Card](https://github.com/jxlarrea/voice-satellite-card-integration) to be installed.** The card is responsible for rendering image and video search results in the UI. Without it, the LLM tools will still return data to the conversation agent, but there will be no visual display.

## Features

### Image Search

Search the internet for images using one of two supported providers:

| Provider | Description |
|----------|-------------|
| **Brave Image Search** | Uses the [Brave Search API](https://brave.com/search/api/). Requires an API key. Supports configurable SafeSearch levels (off, moderate, strict). |
| **SearXNG** | Uses a self-hosted [SearXNG](https://docs.searxng.org/) instance. No external API key required — just point it at your instance URL. Optionally specify which image engines to use. |

All providers support configurable result counts (1-10 images per search).

### Video Search

Search YouTube for videos with full metadata:

| Provider | Description |
|----------|-------------|
| **YouTube Data API v3** | Uses the [YouTube Data API](https://developers.google.com/youtube/v3). Requires an API key with YouTube Data API v3 enabled. Returns video titles, thumbnails, channel names, durations, and view counts. |

Video search is configured as a separate entry and can be added independently from image search.

### Result Caching

All search results are cached in memory with a configurable TTL (default: 1 hour). Repeated searches for the same query return instantly without consuming API quota.

## Prerequisites

1. **[Voice Satellite Card](https://github.com/jxlarrea/voice-satellite-card-integration)** installed and configured.
2. A **conversation agent** that supports LLM tool use (OpenAI, Google Generative AI, Anthropic, Ollama, etc.). The built-in Home Assistant conversation agent does not support tool calling.
3. **API credentials** for your chosen search provider(s) — see the [Provider Setup](#provider-setup) section below.

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS (type: Integration)
2. Search for `Voice Satellite Card LLM Tools` and install
3. Restart Home Assistant

### Manual

1. Download the [latest release](https://github.com/jxlarrea/voice-satellite-card-llm-tools/releases/latest)
2. Copy the `custom_components/voice_satellite_llm_tools` folder to your `config/custom_components/` directory
3. Restart Home Assistant

## Setup

Each tool (Image Search, Video Search) is configured as a separate entry, so you can add and remove them independently.

### Adding Image Search

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **Voice Satellite Card LLM Tools**
3. Select **Image Search** as the tool type
4. Choose your image search provider (Brave or SearXNG)
5. Enter your provider credentials and configure the maximum number of results
6. Go to your **Assist Pipeline** settings and enable the **Voice Satellite Card: Image Search** LLM API for your conversation agent

### Adding Video Search

1. Go to **Settings > Devices & Services > Add Integration**
2. Search for **Voice Satellite Card LLM Tools**
3. Select **Video Search** as the tool type
4. Enter your YouTube Data API v3 key and configure the maximum number of results
5. Go to your **Assist Pipeline** settings and enable the **Voice Satellite Card: Video Search** LLM API for your conversation agent

> **Note:** Only one Image Search entry and one Video Search entry are allowed at a time. To change providers or settings, go to the entry's options flow (**Settings > Devices & Services > Voice Satellite Card LLM Tools > Configure**). To disable a tool, simply remove its entry.

## Provider Setup

### Brave Image Search

1. Go to the [Brave Search API](https://brave.com/search/api/) page
2. Sign up for an API plan (free tier available)
3. Copy your **API key**

### SearXNG

1. Set up a [SearXNG](https://docs.searxng.org/) instance (self-hosted or use an existing one)
2. Ensure the instance has **JSON format** enabled in its settings
3. Note the instance URL (e.g., `http://localhost:8080`)
4. Optionally, specify which image search engines to use (e.g., `bing images,google images`)

### YouTube Data API v3

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a project (or select an existing one)
3. Enable the **YouTube Data API v3**
4. Create an API key under **APIs & Services > Credentials**

## Configuration Options

### Image Search

| Option | Description |
|--------|-------------|
| **Image Search Provider** | Brave or SearXNG |
| **API Key** | Brave only — your Brave Search API key |
| **Server URL** | SearXNG only — your instance URL |
| **Engines** | SearXNG only — comma-separated list of image engines |
| **SafeSearch** | Brave only — off, moderate, or strict |
| **Maximum Number of Results** | 1-10 images per search (default: 3) |

### Video Search

| Option | Description |
|--------|-------------|
| **YouTube API Key** | Your YouTube Data API v3 key |
| **Maximum Number of Results** | 1-6 videos per search (default: 3) |

## Troubleshooting

### The assistant doesn't search for images/videos

1. **Check your conversation agent:** The built-in Home Assistant conversation agent does not support LLM tool calling. Use a third-party agent like OpenAI, Google Generative AI, Anthropic, or Ollama.
2. **Enable the LLM APIs:** Go to your Assist pipeline settings and make sure the **Voice Satellite Card: Image Search** and/or **Voice Satellite Card: Video Search** APIs are enabled for your conversation agent.
3. **Verify API credentials:** Double-check that your API keys are correct and have the required APIs enabled.

### Search returns no results

1. **Check API quotas:** Brave Search and YouTube APIs have daily quota limits. Check your provider's dashboard for quota usage.
2. **Check SearXNG instance:** If using SearXNG, ensure the instance is running and reachable from Home Assistant.
3. **Try a different query:** Some queries may not return results depending on the provider and search terms.

### Results don't display in the card

Make sure the [Voice Satellite Card](https://github.com/jxlarrea/voice-satellite-card-integration) is installed and up to date. The card is responsible for rendering search results visually.

## License

ISC License - see [LICENSE](LICENSE) for details.
