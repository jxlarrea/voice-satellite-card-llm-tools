# <img width="48" height="48" alt="icon" src="https://github.com/user-attachments/assets/c852d278-a2e8-491a-9fe9-49f511ece3de" /> Voice Satellite Card - LLM Tools

Extend your voice assistant's capabilities with **web, Wikipedia, image, video search, weather forecast, and financial data tools** for Home Assistant's LLM integrations. When paired with the [Voice Satellite Card](https://github.com/jxlarrea/voice-satellite-card-integration), results are displayed directly in the card UI.

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-blue.svg?style=for-the-badge)](https://www.hacs.xyz/docs/faq/custom_repositories/)
[![Downloads](https://img.shields.io/github/downloads/jxlarrea/voice-satellite-card-llm-tools/total?style=for-the-badge&label=Downloads&color=red)](https://github.com/jxlarrea/voice-satellite-card-llm-tools/releases)
[![version](https://shields.io/github/v/release/jxlarrea/voice-satellite-card-llm-tools?style=for-the-badge&color=orange)](https://github.com/jxlarrea/voice-satellite-card-llm-tools/releases)
[![Latest Release](https://img.shields.io/badge/dynamic/json?style=for-the-badge&color=41BDF5&logo=home-assistant&label=home%20assistant&cacheSeconds=15600&url=https://analytics.home-assistant.io/custom_integrations.json&query=$.voice_satellite_llm_tools.total)](https://analytics.home-assistant.io/custom_integrations.json)
[![Build](https://img.shields.io/github/actions/workflow/status/jxlarrea/voice-satellite-card-llm-tools/release.yml?style=for-the-badge&label=Build)](https://github.com/jxlarrea/voice-satellite-card-llm-tools/actions/workflows/release.yml)

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-FFDD00?style=for-the-badge&logo=buy-me-a-coffee&logoColor=black)](https://buymeacoffee.com/jxlarrea)

![Screenshot](https://github.com/user-attachments/assets/621ee33f-83db-45ec-83ef-39038008e7dc)

## Table of Contents

- [How It Works](#how-it-works)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Setup](#setup)
- [Provider Setup](#provider-setup)
- [Configuration Options](#configuration-options)
- [Troubleshooting](#troubleshooting)

## How It Works

This integration registers **LLM API tools** with Home Assistant. When a conversation agent (OpenAI, Google Generative AI, Anthropic, Ollama, etc.) receives a request, it can call these tools to fetch results. The [Voice Satellite Card](https://github.com/jxlarrea/voice-satellite-card-integration) renders the results visually.

**Example voice commands:**

- "Search the web for best restaurants in Tokyo"
- "Tell me about Marie Curie"
- "Show me pictures of golden retrievers"
- "Search for videos on how to make sourdough bread"
- "What's the weather like tomorrow?"
- "What's the price of Apple stock?"
- "How much is Bitcoin right now?"
- "Convert 100 USD to EUR"

> **Requires the [Voice Satellite Card](https://github.com/jxlarrea/voice-satellite-card-integration).** Without it, the tools still return data to the conversation agent but there will be no visual display.

## Features

### Web Search

Search the web using [Brave Search API](https://brave.com/search/api/) or a self-hosted [SearXNG](https://docs.searxng.org/) instance. Returns page titles, snippets, and thumbnails. The conversation agent synthesizes results into a concise answer.

### Wikipedia

Look up topics on Wikipedia — no API key required. Returns a single authoritative article with thumbnail. Choose between **Concise** (1-3 sentence summary) or **Detailed** (full introduction section, uses more LLM tokens).

### Image Search

Search for images using [Brave Search API](https://brave.com/search/api/) or [SearXNG](https://docs.searxng.org/). Supports SafeSearch (Brave) and configurable result counts (1-10).

### Video Search

Search YouTube via the [YouTube Data API v3](https://developers.google.com/youtube/v3). Returns titles, thumbnails, channel names, durations, and view counts.

### Weather Forecast

Get weather forecasts using your existing Home Assistant weather entities — no additional API key required. Supports today, tomorrow, specific days of the week, and weekly outlooks. Optionally include hour-by-hour detail, current temperature, and humidity readings from dedicated sensors. Weather condition icons are displayed alongside forecast data.

### Financial Data

Look up stock prices, cryptocurrency prices, and convert currencies using [Finnhub](https://finnhub.io/) (free tier available). Stocks return current price, daily change, high/low, and company logo. Cryptocurrency queries (BTC, ETH, DOGE, and 25+ others) are automatically resolved via [CoinGecko](https://www.coingecko.com/) for accurate pricing. Currency conversion supports all major forex pairs.

### Auto Display / Auto Play

When the user asks for something specific (e.g. "show me the Mona Lisa"), the card automatically displays the first result. For broader searches, results appear as a browsable list.

### Result Caching

Search results (web, image, video, Wikipedia) are cached in memory (default: 1 hour). Repeated queries return instantly without consuming API quota. Weather and financial data are fetched live on every request.

## Prerequisites

1. **[Voice Satellite Card](https://github.com/jxlarrea/voice-satellite-card-integration)** installed and configured
2. A **conversation agent** with LLM tool support (OpenAI, Google Generative AI, Anthropic, Ollama, etc.)
3. **API credentials** for your chosen providers (Wikipedia and Weather require none)

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS (type: Integration)
2. Search for `Voice Satellite Card LLM Tools` and install
3. Restart Home Assistant

### Manual

1. Download the [latest release](https://github.com/jxlarrea/voice-satellite-card-llm-tools/releases/latest)
2. Copy `custom_components/voice_satellite_llm_tools` to your `config/custom_components/` directory
3. Restart Home Assistant

## Setup

Each tool is configured as a separate entry via **Settings > Devices & Services > Add Integration > Voice Satellite Card LLM Tools**. After adding a tool, enable its LLM API in your **Assist Pipeline** settings.

| Tool | Setup Steps |
|------|-------------|
| **Web Search** | Select provider (Brave/SearXNG) → enter credentials → configure max results |
| **Wikipedia** | Choose detail level (Concise/Detailed) |
| **Image Search** | Select provider (Brave/SearXNG) → enter credentials → configure max results |
| **Video Search** | Enter YouTube Data API v3 key → configure max results |
| **Weather Forecast** | Select daily weather entity → optionally add hourly entity, temperature, and humidity sensors |
| **Financial Data** | Select provider (Finnhub) → enter API key |

> Only one entry per tool type is allowed. Use **Configure** to change settings, or remove the entry to disable a tool.

## Provider Setup

### Brave Search

1. Sign up at the [Brave Search API](https://brave.com/search/api/) page (free tier available)
2. Copy your API key — the same key works for both Web Search and Image Search

### SearXNG

1. Set up a [SearXNG](https://docs.searxng.org/) instance with **JSON format** enabled
2. Note the instance URL (e.g., `http://localhost:8080`)
3. Optionally specify engines (e.g., `google,bing` for web or `bing images,google images` for images)

### YouTube Data API v3

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Enable the **YouTube Data API v3** and create an API key

### Wikipedia

No setup required — uses the public Wikipedia API.

### Finnhub

1. Sign up at [Finnhub](https://finnhub.io/) (free tier: 60 calls/min)
2. Copy your API key from the dashboard

### Weather Forecast

No API key required — uses your existing Home Assistant weather entities. You need at least one weather integration configured (e.g., Met.no, OpenWeatherMap, AccuWeather).

## Configuration Options

| Tool | Option | Description |
|------|--------|-------------|
| **Web Search** | Provider | Brave or SearXNG |
| | API Key | Brave only |
| | Server URL | SearXNG only |
| | Engines | SearXNG only — comma-separated list |
| | Max Results | 1-6 (default: 3) |
| **Wikipedia** | Article Detail | Concise (short summary) or Detailed (full intro, more tokens) |
| **Image Search** | Provider | Brave or SearXNG |
| | API Key | Brave only |
| | Server URL | SearXNG only |
| | Engines | SearXNG only — comma-separated list |
| | SafeSearch | Brave only — off, moderate, or strict |
| | Max Results | 1-10 (default: 3) |
| **Video Search** | YouTube API Key | Your API key |
| | Max Results | 1-6 (default: 3) |
| **Weather Forecast** | Daily Forecast Entity | A weather entity that provides daily forecasts (required) |
| | Hourly Forecast Entity | Enables hour-by-hour detail for specific days (optional) |
| | Current Temperature Sensor | Includes current temperature in today's/weekly forecast (optional) |
| | Current Humidity Sensor | Includes current humidity in today's/weekly forecast (optional) |
| **Financial Data** | Provider | Finnhub |
| | Finnhub API Key | Your API key from [finnhub.io](https://finnhub.io/) |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Assistant doesn't search | Ensure you're using a conversation agent with LLM tool support (not the built-in HA agent). Verify the LLM APIs are enabled in your Assist pipeline settings. |
| No results returned | Check API quotas, verify SearXNG is reachable, or try a different query. |
| Results don't display | Ensure the [Voice Satellite Card](https://github.com/jxlarrea/voice-satellite-card-integration) is installed and up to date. |
| Weather returns no forecast | Verify your weather entity supports daily forecasts. Check **Developer Tools > States** to confirm the entity has forecast data. |
| Stock price not found | Ensure you're using the correct ticker symbol (e.g., `AAPL` not `Apple`). For crypto, use the coin symbol (e.g., `BTC`, `ETH`). |
| Crypto shows wrong price | Some crypto symbols overlap with stock tickers. The tool prioritizes crypto for known symbols (BTC, ETH, etc.) and falls back to stocks otherwise. |

## License

MIT License - see [LICENSE](LICENSE) for details.
