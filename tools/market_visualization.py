"""Small dependency-free chart for the final research notebook."""

from html import escape
from pathlib import Path


def save_price_chart(market_result: dict, destination: str | Path) -> Path:
    """Write an SVG closing-price chart from MarketAgent.analyze output."""
    history = market_result["history"]
    if not history:
        raise ValueError("At least one price observation is required")

    prices = [float(row["close"]) for row in history]
    low, high = min(prices), max(prices)
    span = high - low or 1.0
    left, top, width, height = 65, 45, 660, 270
    points = [
        f"{left + i * width / max(len(prices) - 1, 1):.1f},"
        f"{top + (high - price) * height / span:.1f}"
        for i, price in enumerate(prices)
    ]
    ticker = escape(str(market_result["ticker"]))
    first_date = escape(str(history[0]["date"]))
    last_date = escape(str(history[-1]["date"]))
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="390"
  viewBox="0 0 800 390" role="img" aria-label="{ticker} closing prices">
  <rect width="800" height="390" fill="white"/>
  <text x="65" y="27" font-family="sans-serif" font-size="20">{ticker} closing price</text>
  <path d="M65 45 V315 H725" fill="none" stroke="#777"/>
  <polyline points="{' '.join(points)}" fill="none" stroke="#1769aa"
    stroke-width="2.5" stroke-linejoin="round"/>
  <g fill="#333" font-family="sans-serif" font-size="13">
    <text x="8" y="49">${high:,.2f}</text>
    <text x="8" y="319">${low:,.2f}</text>
    <text x="65" y="342">{first_date}</text>
    <text x="645" y="342">{last_date}</text>
    <text x="65" y="373">Source: Yahoo Finance via yfinance</text>
  </g>
</svg>"""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(svg, encoding="utf-8")
    return destination
