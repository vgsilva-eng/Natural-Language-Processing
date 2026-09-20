"""Financial news fetching via NewsAPI and yfinance news fallback."""

import os
from datetime import datetime, timedelta

import requests


NEWSAPI_URL = "https://newsapi.org/v2/everything"


def fetch_news(ticker: str, lookback_days: int = 7, max_articles: int = 20) -> list[dict]:
    """
    Fetch recent news articles for a ticker.

    Tries NewsAPI first (requires NEWSAPI_KEY in .env).
    Falls back to yfinance news if key is unavailable.

    Returns a list of dicts with keys:
      title, source, published_at, url, description
    """
    api_key = os.getenv("NEWSAPI_KEY")

    if api_key:
        return _fetch_from_newsapi(ticker, lookback_days, max_articles, api_key)
    else:
        return _fetch_from_yfinance(ticker)


def _fetch_from_newsapi(ticker: str, lookback_days: int, max_articles: int, api_key: str) -> list[dict]:
    from_date = (datetime.now() - timedelta(days=lookback_days)).strftime("%Y-%m-%d")

    params = {
        "q": ticker,
        "from": from_date,
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": max_articles,
        "apiKey": api_key,
    }

    response = requests.get(NEWSAPI_URL, params=params, timeout=10)
    response.raise_for_status()
    data = response.json()

    articles = []
    for item in data.get("articles", []):
        articles.append({
            "title": item.get("title"),
            "source": item.get("source", {}).get("name"),
            "published_at": item.get("publishedAt"),
            "url": item.get("url"),
            "description": item.get("description"),
        })

    return articles


def _fetch_from_yfinance(ticker: str) -> list[dict]:
    import yfinance as yf

    t = yf.Ticker(ticker)
    raw = t.news or []

    articles = []
    for item in raw:
        articles.append({
            "title": item.get("title"),
            "source": item.get("publisher"),
            "published_at": datetime.fromtimestamp(item.get("providerPublishTime", 0)).isoformat(),
            "url": item.get("link"),
            "description": None,
        })

    return articles
