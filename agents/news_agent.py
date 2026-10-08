"""News ingestion and sentiment analysis specialist agent."""

from __future__ import annotations

import os

import anthropic
from dotenv import load_dotenv

from tools.news_tool import fetch_news


class NewsAgent:
    """Fetches, classifies, and summarizes financial news for a ticker."""

    def __init__(self, model: str = "claude-sonnet-5"):
        self.model = model

    def fetch_and_classify(
        self, ticker: str, lookback_days: int = 7
    ) -> list[dict]:
        """Fetch recent news and classify each article by financial topic."""
        load_dotenv()

        articles = fetch_news(ticker, lookback_days=lookback_days)

        if not articles:
            return []

        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        classified_articles = []

        for article in articles:
            title = article.get("title") or ""
            description = article.get("description") or ""

            prompt = f"""
Classify this financial news article into exactly one category:
earnings, macro, sentiment, product, or other.

Title: {title}
Description: {description}

Return only the category name.
"""

            response = client.messages.create(
                model=self.model,
                max_tokens=20,
                messages=[
                    {"role": "user", "content": prompt}
                ],
            )

            category = response.content[0].text.strip().lower()

            if category not in {
                "earnings",
                "macro",
                "sentiment",
                "product",
                "other",
            }:
                category = "other"

            classified_article = article.copy()
            classified_article["category"] = category
            classified_articles.append(classified_article)

        return classified_articles

    def summarize(self, articles: list[dict]) -> str:
        """Summarize key themes across classified articles."""
        if not articles:
            return "No recent news articles were found."

        load_dotenv()

        client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )

        article_text = "\n".join(
            f"- [{article.get('category', 'other')}] "
            f"{article.get('title', '')}: "
            f"{article.get('description') or ''}"
            for article in articles
        )

        prompt = f"""
Summarize the key financial news themes from the articles below.

Focus on:
- major developments
- earnings or company performance
- market sentiment
- potential risks or opportunities

Use only the information provided in the articles.
Keep the summary concise and factual.
Limit the summary to 4-6 bullet points total.
Prioritize the most relevant financial information and avoid unnecessary detail.

Articles:
{article_text}
"""

        response = client.messages.create(
            model=self.model,
            max_tokens=1000,
            messages=[
                {"role": "user", "content": prompt}
            ],
        )

        text_parts = [
            block.text
            for block in response.content
            if getattr(block, "type", None) == "text"
        ]

        return "\n".join(text_parts).strip()