"""Regression tests for the prompt-chaining workflow."""

from workflows import prompt_chaining
from types import SimpleNamespace

from tools.anthropic_tool import response_text


def test_response_text_skips_thinking_blocks():
    response = SimpleNamespace(content=[
        SimpleNamespace(type="thinking", thinking="internal reasoning"),
        SimpleNamespace(type="text", text="usable answer"),
    ])

    assert response_text(response) == "usable answer"


def test_prompt_chain_returns_complete_contract_when_news_is_empty(monkeypatch):
    """The final notebook must remain runnable when a provider has no news."""
    monkeypatch.setattr(prompt_chaining, "fetch_news", lambda *args, **kwargs: [])

    result = prompt_chaining.run_prompt_chain("TEST")

    assert result["ticker"] == "TEST"
    assert result["articles_ingested"] == 0
    assert result["articles_after_dedup"] == 0
    assert result["classified"] == []
    assert result["key_facts"] == []
    assert result["summary"] == "No recent news articles were found."
