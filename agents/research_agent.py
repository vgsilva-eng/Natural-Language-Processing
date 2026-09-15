"""
Autonomous Investment Research Agent — main orchestrator.

Responsibilities:
  - Plan research steps for a given stock symbol
  - Delegate to specialist agents via the router
  - Self-reflect on output quality
  - Maintain cross-run memory
"""

from __future__ import annotations

from tools.memory_tool import AgentMemory


class ResearchAgent:
    """Orchestrates the end-to-end investment research workflow."""

    def __init__(self, model: str = "claude-opus-5"):
        self.model = model
        self.memory = AgentMemory()

    def plan(self, ticker: str) -> list[str]:
        """Return ordered research steps for the given ticker."""
        raise NotImplementedError

    def run(self, ticker: str) -> dict:
        """Execute the full research pipeline and return a structured report."""
        raise NotImplementedError

    def reflect(self, report: dict) -> str:
        """Self-assess quality of the generated report; return critique."""
        raise NotImplementedError
