"""
Workflow 2: Routing
An LLM classifier reads a piece of content and directs it to the right
specialist handler (earnings, news, or market analysis).
"""

from __future__ import annotations

import os
import json

import anthropic
from dotenv import load_dotenv
from tools.anthropic_tool import response_text

load_dotenv()


VALID_ROUTES = ["earnings", "news", "market"]


def classify_route(content: str, client: anthropic.Anthropic) -> str:
    """Ask the LLM which specialist should handle this content."""
    prompt = (
        "You are a router for a financial research system. "
        "Read the content below and decide which specialist should handle it.\n\n"
        "Choose exactly one:\n"
        "  - earnings : revenue, profit, EPS, guidance, financial statements\n"
        "  - news     : headlines, press, analyst ratings, general sentiment\n"
        "  - market   : price action, volume, technical trends, valuation\n\n"
        f"Content:\n{content}\n\n"
        "Return ONLY the single word route (earnings, news, or market)."
    )
    resp = client.messages.create(
        model="claude-sonnet-5",
        max_tokens=16,
        thinking={"type": "disabled"},
        messages=[{"role": "user", "content": prompt}],
    )
    route = response_text(resp).lower()
    return route if route in VALID_ROUTES else "news"


def route_to_specialist(content: str, ticker: str | None = None) -> dict:
    """
    Route content to the correct specialist agent and return its analysis.

    Returns:
      {route, ticker, result}
    """
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    print(f"[Router] Classifying content...")
    route = classify_route(content, client)
    print(f"[Router] Routed to: {route}")

    # Lazy imports avoid circular dependency with agents package.
    from agents.earnings_agent import EarningsAgent
    from agents.market_agent import MarketAgent
    from agents.news_agent import NewsAgent

    specialists = {
        "earnings": EarningsAgent,
        "news": NewsAgent,
        "market": MarketAgent,
    }

    agent = specialists[route]()

    if route == "earnings":
        result = agent.analyze(ticker) if ticker else {"error": "ticker required for earnings"}
    elif route == "market":
        result = agent.analyze(ticker) if ticker else {"error": "ticker required for market"}
    else:  # news
        if ticker:
            articles = agent.fetch_and_classify(ticker)
            result = {"summary": agent.summarize(articles), "articles": articles}
        else:
            result = {"error": "ticker required for news"}

    return {"route": route, "ticker": ticker, "result": result}
