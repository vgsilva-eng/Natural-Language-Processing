"""Tests for the EarningsAgent."""

from agents.earnings_agent import EarningsAgent


def test_earnings_agent_analysis(monkeypatch):
    """Test that EarningsAgent correctly analyzes financial data."""

    mock_financials = {
        "ticker": "AAPL",
        "sector": "Technology",
        "industry": "Consumer Electronics",
        "revenue": 1000.0,
        "gross_profit": 500.0,
        "operating_income": 300.0,
        "net_income": 200.0,
        "eps": 5.0,
        "pe_ratio": 25.0,
        "forward_pe": 22.0,
        "market_cap": 3000000.0,
        "total_assets": 2000.0,
        "total_debt": 500.0,
        "cash": 400.0,
        "dividend_yield": 0.5,
        "summary": "Test company summary.",
    }

    monkeypatch.setattr(
        "agents.earnings_agent.get_financials",
        lambda ticker: mock_financials,
    )

    agent = EarningsAgent()
    result = agent.analyze("AAPL")

    assert result["ticker"] == "AAPL"
    assert result["revenue"] == 1000.0
    assert result["net_income"] == 200.0
    assert result["net_margin_pct"] == 20.0
    assert result["data_source"] == "Yahoo Finance"
    assert "positive net income" in result["signals"][0].lower()


def test_earnings_agent_missing_values(monkeypatch):
    """Test that EarningsAgent handles missing financial values."""

    mock_financials = {
        "ticker": "TEST",
        "sector": None,
        "industry": None,
        "revenue": None,
        "gross_profit": None,
        "operating_income": None,
        "net_income": None,
        "eps": None,
        "pe_ratio": None,
        "forward_pe": None,
        "market_cap": None,
        "total_assets": None,
        "total_debt": None,
        "cash": None,
        "dividend_yield": None,
        "summary": None,
    }

    monkeypatch.setattr(
        "agents.earnings_agent.get_financials",
        lambda ticker: mock_financials,
    )

    agent = EarningsAgent()
    result = agent.analyze("TEST")

    assert result["ticker"] == "TEST"
    assert result["net_margin_pct"] is None
    assert result["signals"] == []


def test_router_dispatches_to_earnings_agent(monkeypatch):
    """Test that the router dispatches an earnings request to EarningsAgent."""

    from workflows import routing

    mock_result = {
        "ticker": "AAPL",
        "revenue": 1000.0,
        "net_income": 200.0,
        "net_margin_pct": 20.0,
        "signals": ["The company reported positive net income."],
    }

    monkeypatch.setattr(
        routing,
        "classify_route",
        lambda content, client: "earnings",
    )

    monkeypatch.setattr(
        EarningsAgent,
        "analyze",
        lambda self, ticker: mock_result,
    )

    result = routing.route_to_specialist(
        "How are Apple's earnings?",
        ticker="AAPL",
    )

    assert result["route"] == "earnings"
    assert result["ticker"] == "AAPL"
    assert result["result"] == mock_result