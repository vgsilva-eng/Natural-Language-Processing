"""News ingestion and sentiment analysis specialist agent."""

from __future__ import annotations


class NewsAgent:
    """Fetches, classifies, and summarizes financial news for a ticker."""

    def __init__(self, model: str = "claude-sonnet-5"):
        self.model = model

    def fetch_and_classify(self, ticker: str, lookback_days: int = 7) -> list[dict]:
        """Fetch recent news and classify each article (earnings/macro/sentiment)."""
        raise NotImplementedError

    def summarize(self, articles: list[dict]) -> str:
        """Summarize key themes across classified articles."""
        raise NotImplementedError
