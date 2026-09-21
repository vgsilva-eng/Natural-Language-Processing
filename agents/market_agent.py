"""Market price and technical data specialist agent."""

from __future__ import annotations

from tools.yfinance_tool import get_stock_data


class MarketAgent:
    """Summarize observed price, volume, and moving-average signals."""

    def __init__(self, model: str = "claude-sonnet-5"):
        self.model = model

    def analyze(self, ticker: str, period: str = "3mo") -> dict:
        """Return a reproducible market analysis for the routing workflow."""
        data = get_stock_data(ticker, period=period)
        history = data["history"]
        price = data["current_price"]
        first_price = history[0]["close"]
        period_return = (
            round((price / first_price - 1) * 100, 2)
            if first_price > 0 and len(history) > 1 else None
        )

        ma_50 = data["ma_50"]
        ma_200 = data["ma_200"]
        if ma_50 is None:
            trend = "insufficient history for 50-day average"
        elif price > ma_50:
            trend = "above 50-day average"
        elif price < ma_50:
            trend = "below 50-day average"
        else:
            trend = "at 50-day average"

        crossover = None
        if ma_50 is not None and ma_200 is not None:
            if ma_50 > ma_200:
                crossover = "50-day above 200-day"
            elif ma_50 < ma_200:
                crossover = "50-day below 200-day"
            else:
                crossover = "50-day equal to 200-day"

        volumes = [row["volume"] for row in history if row["volume"] is not None]
        recent = volumes[-20:]
        recent_avg_volume = round(sum(recent) / len(recent)) if recent else None
        latest_volume = history[-1]["volume"]
        volume_ratio = (
            round(latest_volume / recent_avg_volume, 2)
            if latest_volume is not None and recent_avg_volume else None
        )

        signals = [f"Price is {trend}."]
        if period_return is not None:
            signals.append(f"Return over available period: {period_return:+.2f}%.")
        if crossover:
            signals.append(f"Moving averages: {crossover}.")
        if volume_ratio is not None:
            signals.append(
                f"Latest volume is {volume_ratio:.2f} times the "
                "recent 20-session average."
            )

        return {
            "ticker": data["ticker"],
            "period": period,
            "as_of": history[-1]["date"],
            "current_price": price,
            "change_pct": data["change_pct"],
            "period_return_pct": period_return,
            "trend": trend,
            "ma_50": ma_50,
            "ma_200": ma_200,
            "crossover": crossover,
            "latest_volume": latest_volume,
            "recent_avg_volume": recent_avg_volume,
            "volume_ratio": volume_ratio,
            "week_52_high": data["week_52_high"],
            "week_52_low": data["week_52_low"],
            "market_cap": data["market_cap"],
            "signals": signals,
            "summary": " ".join(signals),
            "data_source": "Yahoo Finance via yfinance",
            "history": history,
        }
