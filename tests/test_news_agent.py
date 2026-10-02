"""Tests for the NewsAgent."""

from unittest.mock import MagicMock

from agents.news_agent import NewsAgent


def test_news_agent_fetch_and_classify(monkeypatch):
    """Test that NewsAgent fetches and classifies news articles."""

    mock_articles = [
        {
            "title": "Apple reports quarterly earnings",
            "source": "Test Source",
            "published_at": "2026-09-30T12:00:00Z",
            "url": "https://example.com/article",
            "description": "Apple reported its latest quarterly results.",
        }
    ]

    monkeypatch.setattr(
        "agents.news_agent.fetch_news",
        lambda ticker, lookback_days=7: mock_articles,
    )

    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(type="text", text="earnings")
    ]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    monkeypatch.setattr(
        "agents.news_agent.anthropic.Anthropic",
        lambda api_key=None: mock_client,
    )

    agent = NewsAgent()
    result = agent.fetch_and_classify("AAPL")

    assert len(result) == 1
    assert result[0]["title"] == "Apple reports quarterly earnings"
    assert result[0]["category"] == "earnings"


def test_news_agent_no_articles(monkeypatch):
    """Test that NewsAgent handles an empty news result."""

    monkeypatch.setattr(
        "agents.news_agent.fetch_news",
        lambda ticker, lookback_days=7: [],
    )

    agent = NewsAgent()
    result = agent.fetch_and_classify("AAPL")

    assert result == []


def test_news_agent_summary_empty():
    """Test the response when there are no articles."""

    agent = NewsAgent()
    result = agent.summarize([])

    assert result == "No recent news articles were found."