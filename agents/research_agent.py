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
from tools.anthropic_tool import response_text
from agents.earnings_agent import EarningsAgent
from agents.market_agent import MarketAgent
from agents.news_agent import NewsAgent

load_dotenv()


class ResearchAgent:
    """Orchestrates the end-to-end investment research workflow."""

    def __init__(self, model: str = "claude-opus-5"):
        self.model = model
        self.client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.memory = AgentMemory()

    @staticmethod
    def _response_text(response) -> str:
        """Return text blocks from a response that may also contain thinking blocks."""
        return response_text(response)
    
    # 1. PLAN
    def plan(self, ticker: str) -> list[str]:
        """Ask the LLM to break down research into ordered steps."""
        past = self.memory.load().get(ticker, {})
        memory_context = f"\nPast notes on {ticker}: {json.dumps(past)}" if past else ""

        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            thinking={"type": "disabled"},
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

        raw = self._response_text(response)

        start, end = raw.find("["), raw.rfind("]") + 1
        if start != -1 and end != -1:
            raw = raw[start:end]
        try:
            steps = json.loads(raw)
        except json.JSONDecodeError:
            steps = [line.strip("-\" ").strip() for line in raw.splitlines() if line.strip()]
        return steps

    # 2. RUN
    def run(self, ticker: str) -> dict:
        """Execute the full research pipeline and return a structured report."""
        print(f"[ResearchAgent] Planning research for {ticker}...")
        steps = self.plan(ticker)
        print(f"[ResearchAgent] Steps: {steps}")
        selected = self._select_specialists(steps)
        print(f"[ResearchAgent] Selected specialists: {selected}")

        market = {}
        if "market" in selected:
            print(f"[ResearchAgent] Running MarketAgent...")
            market = MarketAgent().analyze(ticker)

        financials = {}
        if "earnings" in selected:
            print(f"[ResearchAgent] Running EarningsAgent...")
            financials = EarningsAgent().analyze(ticker)

        news = []
        news_summary = "News analysis was not selected by the research plan."
        if "news" in selected:
            print(f"[ResearchAgent] Running NewsAgent...")
            news_agent = NewsAgent()
            news = news_agent.fetch_and_classify(ticker)
            news_summary = news_agent.summarize(news)
        headlines = [a["title"] for a in news[:10] if a.get("title")]

        print(f"[ResearchAgent] Synthesizing report...")
        report_text = self._synthesize(
            ticker, steps, market, financials, headlines, news_summary
        )

        report = {
            "ticker": ticker,
            "steps": steps,
            "selected_specialists": selected,
            "market_snapshot": {
                "price": market.get("current_price"),
                "change_pct": market.get("change_pct"),
                "week_52_high": market.get("week_52_high"),
                "week_52_low": market.get("week_52_low"),
            },
            "financials_snapshot": {
                "revenue": financials.get("revenue"),
                "net_income": financials.get("net_income"),
                "pe_ratio": financials.get("pe_ratio"),
                "sector": financials.get("sector"),
            },
            "top_headlines": headlines,
            "specialist_outputs": {
                "market": market,
                "earnings": financials,
                "news": {"articles": news, "summary": news_summary},
            },
            "analysis": report_text,
        }

        print(f"[ResearchAgent] Reflecting and refining report...")
        reflection = self.reflect(report)
        report["initial_analysis"] = report_text
        report["reflection"] = reflection
        report["analysis"] = self._refine(report_text, reflection)

        self.memory.save(
            ticker,
            {"last_price": market.get("current_price"), "summary": report["analysis"][:300]},
        )
        return report

    @staticmethod
    def _select_specialists(steps: list[str]) -> list[str]:
        """Select specialists whose subject matter appears in the research plan."""
        plan = " ".join(str(step) for step in steps).lower()
        keywords = {
            "market": ("market", "price", "technical", "volume", "valuation"),
            "earnings": ("earnings", "financial", "revenue", "profit", "fundamental"),
            "news": ("news", "headline", "sentiment", "event", "development"),
        }
        selected = [
            specialist
            for specialist, terms in keywords.items()
            if any(term in plan for term in terms)
        ]
        return selected or list(keywords)

    def _synthesize(
        self, ticker, steps, market, financials, headlines, news_summary
    ) -> str:
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
            f"NewsAgent summary:\n{news_summary}\n\n"
            f"Write a 3-paragraph investment research summary covering: "
            f"(1) market position and price action, (2) financial health, (3) news sentiment and outlook."
        )
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            thinking={"type": "disabled"},
            messages=[{"role": "user", "content": prompt}],
        )
        return self._response_text(response)

    def _refine(self, analysis: str, reflection: str) -> str:
        """Revise an analysis by applying the agent's own reflection feedback."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=1024,
            thinking={"type": "disabled"},
            messages=[{
                "role": "user",
                "content": (
                    "Revise the investment analysis using every applicable point in the "
                    f"self-critique. Preserve factual details.\n\nAnalysis:\n{analysis}"
                    f"\n\nSelf-critique:\n{reflection}\n\nReturn only the revised analysis."
                ),
            }],
        )
        return self._response_text(response)

    # 3. REFLECT
    def reflect(self, report: dict) -> str:
        """Self-assess the quality of the generated report."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=512,
            thinking={"type": "disabled"},
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
        return self._response_text(response)
