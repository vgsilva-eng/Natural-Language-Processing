"""Focused tests for ResearchAgent orchestration decisions."""

from agents.research_agent import ResearchAgent


def test_select_specialists_follows_research_plan():
    steps = [
        "Review recent price and volume trends",
        "Assess earnings, revenue, and financial health",
    ]

    assert ResearchAgent._select_specialists(steps) == ["market", "earnings"]


def test_select_specialists_uses_all_when_plan_is_ambiguous():
    assert ResearchAgent._select_specialists(["Research the company"]) == [
        "market",
        "earnings",
        "news",
    ]
