"""
Autonomous Investment Research Agent — main orchestrator.

Responsibilities:
  - Plan research steps for a given stock symbol
  - Fetch data via tools and synthesize a report
  - Self-reflect on output quality
  - Persist key findings in memory across runs
"""

from __future__ import annotations

import json
import os

import anthropic
from dotenv import load_dotenv

from tools.memory_tool import AgentMemory
from tools.news_tool import fetch_news
from tools.yfinance_tool import get_financials, get_stock_data

load_dotenv()


class ResearchAgent:
    """Orchestrates the end-to-end investment research workflow."""

    def __init__(self, model: str = "claude-opus-5"):
        self.model = model
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.memory = AgentMemory()

    # ------------------------------------------------------------------
    # 1. PLAN
    # ------------------------------------------------------------------

    def plan(self, ticker: str) -> list[str]:
        """Ask the LLM to break down research into ordered steps."""
        past = self.memory.load().get(ticker, {})
        memory_context = f"\nPast notes on {ticker}: {json.dumps(past)}" if past else ""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are an investment research assistant. "
                        f"List the 5 most important steps to research the stock {ticker}. "
                        f"Return a JSON array of step strings, nothing else.{memory_context}"
                    ),
                }
            ],
        )
        raw = response.content[0].text.strip()
        try:
            steps = json.loads(raw)
        except json.JSONDecodeError:
            steps = [line.strip("- ").strip() for line in raw.splitlines() if line.strip()]
        return steps

    # ------------------------------------------------------------------
    # 2. RUN
    # ------------------------------------------------------------------

    def run(self, ticker: str) -> dict:
        """Execute the full research pipeline and return a structured report."""
        print(f"[ResearchAgent] Planning research for {ticker}...")
        steps = self.plan(ticker)
        print(f"[ResearchAgent] Steps: {steps}")

        print(f"[ResearchAgent] Fetching market data...")
        market = get_stock_data(ticker)
        financials = get_financials(ticker)

        print(f"[ResearchAgent] Fetching news...")
        news = fetch_news(ticker)
        headlines = [a["title"] for a in news[:10] if a.get("title")]

        print(f"[ResearchAgent] Synthesizing report...")
        report_text = self._synthesize(ticker, steps, market, financials, headlines)

        report = {
            "ticker": ticker,
            "steps": steps,
            "market_snapshot": {
                "price": market["current_price"],
                "change_pct": market["change_pct"],
                "week_52_high": market["week_52_high"],
                "week_52_low": market["week_52_low"],
            },
            "financials_snapshot": {
                "revenue": financials["revenue"],
                "net_income": financials["net_income"],
                "pe_ratio": financials["pe_ratio"],
                "sector": financials["sector"],
            },
            "top_headlines": headlines,
            "analysis": report_text,
        }

        self.memory.save(ticker, {"last_price": market["current_price"], "summary": report_text[:300]})
        return report

    def _synthesize(self, ticker, steps, market, financials, headlines) -> str:
        prompt = (
            f"You are an investment research analyst. Write a concise research summary for {ticker}.\n\n"
            f"Research steps followed: {steps}\n\n"
            f"Market data:\n"
            f"  Price: ${market['current_price']} ({market['change_pct']}% today)\n"
            f"  52W range: ${market['week_52_low']} - ${market['week_52_high']}\n"
            f"  Market cap: {financials.get('market_cap')}\n\n"
            f"Financials:\n"
            f"  Revenue: {financials.get('revenue')}\n"
            f"  Net income: {financials.get('net_income')}\n"
            f"  P/E ratio: {financials.get('pe_ratio')}\n"
            f"  Sector: {financials.get('sector')}\n\n"
            f"Recent headlines:\n" + "\n".join(f"  - {h}" for h in headlines) + "\n\n"
            f"Write a 3-paragraph investment research summary covering: "
            f"(1) market position and price action, (2) financial health, (3) news sentiment and outlook."
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.content[0].text.strip()

    # ------------------------------------------------------------------
    # 3. REFLECT
    # ------------------------------------------------------------------

    def reflect(self, report: dict) -> str:
        """Self-assess the quality of the generated report."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            messages=[
                {
                    "role": "user",
                    "content": (
                        f"You are a senior analyst reviewing a research report on {report['ticker']}.\n\n"
                        f"Report analysis:\n{report['analysis']}\n\n"
                        f"Critique this report in 3 bullet points: "
                        f"what is strong, what is missing, and what should be improved."
                    ),
                }
            ],
        )
        return response.content[0].text.strip()
