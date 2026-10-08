"""Earnings and financial statements specialist agent."""

from __future__ import annotations

from tools.yfinance_tool import get_financials


class EarningsAgent:
    """Analyzes earnings reports and financial statement data."""

    def __init__(self, model: str = "claude-sonnet-5"):
        self.model = model

    def analyze(self, ticker: str) -> dict:
        """Pull latest earnings data and return a structured analysis."""
        financials = get_financials(ticker)

        revenue = financials.get("revenue")
        net_income = financials.get("net_income")

        net_margin = None
        if revenue and net_income is not None:
            net_margin = (net_income / revenue) * 100

        signals = []

        if net_income is not None:
            if net_income > 0:
                signals.append("The company reported positive net income.")
            elif net_income < 0:
                signals.append("The company reported a net loss.")

        if net_margin is not None:
            signals.append(
                f"Net profit margin is approximately {net_margin:.2f}%."
            )

        return {
            "ticker": financials.get("ticker"),
            "sector": financials.get("sector"),
            "industry": financials.get("industry"),
            "revenue": revenue,
            "gross_profit": financials.get("gross_profit"),
            "operating_income": financials.get("operating_income"),
            "net_income": net_income,
            "eps": financials.get("eps"),
            "pe_ratio": financials.get("pe_ratio"),
            "forward_pe": financials.get("forward_pe"),
            "market_cap": financials.get("market_cap"),
            "total_assets": financials.get("total_assets"),
            "total_debt": financials.get("total_debt"),
            "cash": financials.get("cash"),
            "dividend_yield": financials.get("dividend_yield"),
            "net_margin_pct": (
                round(net_margin, 2) if net_margin is not None else None
            ),
            "signals": signals,
            "summary": financials.get("summary"),
            "data_source": "Yahoo Finance",
        }