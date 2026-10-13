"""Regression tests for the prompt-chaining workflow."""

from workflows import prompt_chaining


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
