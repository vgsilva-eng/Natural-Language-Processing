"""Deterministic checks for the market specialist and its data adapter."""

import sys
import tempfile
import types
import unittest
import importlib
from unittest.mock import patch

import pandas as pd

from agents.market_agent import MarketAgent
from tools.yfinance_tool import get_stock_data
from tools.market_visualization import save_price_chart


def sample_data(count=60):
    history = [
        {"date": f"2026-01-{i + 1:02d}", "close": 100 + i,
         "volume": 1000, "open": 100 + i, "high": 101 + i,
         "low": 99 + i}
        for i in range(count)
    ]
    return {
        "ticker": "TEST", "period": "3mo", "history": history,
        "current_price": history[-1]["close"], "change_pct": 1.0,
        "ma_50": 134.5 if count >= 50 else None,
        "ma_200": None, "week_52_high": None,
        "week_52_low": None, "market_cap": None,
    }


class MarketAgentTests(unittest.TestCase):
    @patch("agents.market_agent.get_stock_data")
    def test_market_analysis_has_routing_contract_and_signals(self, fetch):
        fetch.return_value = sample_data()
        result = MarketAgent().analyze("test")

        fetch.assert_called_once_with("test", period="3mo")
        self.assertEqual(result["ticker"], "TEST")
        self.assertEqual(result["trend"], "above 50-day average")
        self.assertEqual(result["volume_ratio"], 1.0)
        self.assertIsNone(result["crossover"])
        self.assertIn("above 50-day average", result["summary"])

    @patch("agents.market_agent.get_stock_data")
    def test_short_history_does_not_invent_moving_averages(self, fetch):
        fetch.return_value = sample_data(2)
        result = MarketAgent().analyze("TEST")
        self.assertIsNone(result["ma_50"])
        self.assertIn("insufficient history", result["trend"])

    @patch("agents.market_agent.get_stock_data")
    def test_provider_error_is_visible(self, fetch):
        fetch.side_effect = ValueError("No price data found")
        with self.assertRaisesRegex(ValueError, "No price data"):
            MarketAgent().analyze("BAD")

    @patch("agents.market_agent.get_stock_data")
    def test_price_chart_is_valid_svg(self, fetch):
        fetch.return_value = sample_data(2)
        result = MarketAgent().analyze("TEST")
        with tempfile.TemporaryDirectory() as folder:
            path = save_price_chart(result, f"{folder}/market.svg")
            content = path.read_text(encoding="utf-8")
        self.assertIn("<svg", content)
        self.assertIn("TEST closing price", content)

    @patch("agents.market_agent.get_stock_data")
    def test_router_dispatches_to_market_agent(self, fetch):
        """Exercise router to specialist without calling an external LLM."""
        fetch.return_value = sample_data(2)
        fake_anthropic = types.SimpleNamespace(Anthropic=lambda **kwargs: object())
        fake_dotenv = types.SimpleNamespace(load_dotenv=lambda: None)
        with patch.dict(sys.modules, {"anthropic": fake_anthropic,
                                      "dotenv": fake_dotenv}):
            routing = importlib.import_module("workflows.routing")
            with patch.object(routing, "classify_route", return_value="market"):
                response = routing.route_to_specialist(
                    "What happened to TEST's price?", ticker="TEST"
                )
        self.assertEqual(response["route"], "market")
        self.assertEqual(response["result"]["ticker"], "TEST")
        self.assertIn("summary", response["result"])


class YahooFinanceToolTests(unittest.TestCase):
    def test_missing_metadata_and_sparse_rows(self):
        dates = pd.date_range("2026-01-01", periods=3)
        frame = pd.DataFrame(
            {"Open": [10.0, 11.0, 12.0],
             "High": [11.0, 12.0, 13.0],
             "Low": [9.0, 10.0, 11.0],
             "Close": [10.0, float("nan"), 12.0],
             "Volume": [100, 200, float("nan")]},
            index=dates,
        )

        class FakeTicker:
            def history(self, period):
                self.period = period
                return frame

            @property
            def info(self):
                raise RuntimeError("metadata unavailable")

        fake_yf = types.SimpleNamespace(Ticker=lambda ticker: FakeTicker())
        with patch.dict(sys.modules, {"yfinance": fake_yf}):
            result = get_stock_data(" test ")

        self.assertEqual(result["ticker"], "TEST")
        self.assertEqual(len(result["history"]), 2)
        self.assertIsNone(result["history"][-1]["volume"])
        self.assertIsNone(result["market_cap"])
        self.assertEqual(result["change_pct"], 20.0)

    def test_blank_ticker_rejected(self):
        with self.assertRaisesRegex(ValueError, "ticker is required"):
            get_stock_data("  ")


if __name__ == "__main__":
    unittest.main()
