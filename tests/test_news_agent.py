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


def test_news_agent_summary(monkeypatch):
    """Test that NewsAgent summarizes classified news articles."""

    mock_articles = [
        {
            "title": "Apple reports strong quarterly results",
            "description": "Apple reported higher revenue and net income.",
            "category": "earnings",
        }
    ]

    mock_response = MagicMock()
    mock_response.content = [
        MagicMock(
            type="text",
            text="Apple reported strong quarterly financial performance.",
        )
    ]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    monkeypatch.setattr(
        "agents.news_agent.anthropic.Anthropic",
        lambda api_key=None: mock_client,
    )

    agent = NewsAgent()
    result = agent.summarize(mock_articles)

    assert result == (
        "Apple reported strong quarterly financial performance."
    )

    
def test_router_dispatches_to_news_agent(monkeypatch):
    """Test that the router dispatches a news request to NewsAgent."""

    from workflows import routing

    mock_articles = [
        {
            "title": "Apple announces new product",
            "description": "Apple announced a new product.",
            "category": "product",
        }
    ]

    monkeypatch.setattr(
        routing,
        "classify_route",
        lambda content, client: "news",
    )

    monkeypatch.setattr(
        NewsAgent,
        "fetch_and_classify",
        lambda self, ticker: mock_articles,
    )

    monkeypatch.setattr(
        NewsAgent,
        "summarize",
        lambda self, articles: "Apple announced a new product.",
    )

    result = routing.route_to_specialist(
        "What is the latest Apple news?",
        ticker="AAPL",
    )

    assert result["route"] == "news"
    assert result["ticker"] == "AAPL"
    assert result["result"]["articles"] == mock_articles
    assert result["result"]["summary"] == "Apple announced a new product."