"""Earnings and financial statements specialist agent."""

from __future__ import annotations


class EarningsAgent:
    """Analyzes earnings reports and financial statement data."""

    def __init__(self, model: str = "claude-sonnet-5"):
        self.model = model

    def analyze(self, ticker: str) -> dict:
        """Pull latest earnings data and return a structured analysis."""
        raise NotImplementedError
