"""Yahoo Finance data fetching utilities."""

import math


def _number(value):
    """Convert a provider value to a finite float, or report it missing."""
    try:
        result = float(value)
    except (TypeError, ValueError):
        return None
    return result if math.isfinite(result) else None


def get_stock_data(ticker: str, period: str = "3mo") -> dict:
    """
    Fetch price history and key market stats for a ticker.

    Returns a dict with:
      - history: list of {date, open, high, low, close, volume}
      - current_price, prev_close, change_pct
      - week_52_high, week_52_low
      - ma_50, ma_200
      - market_cap, avg_volume
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("A stock ticker is required")
    import yfinance as yf

    ticker = ticker.strip().upper()
    t = yf.Ticker(ticker)
    hist = t.history(period=period)

    if hist.empty:
        raise ValueError(f"No price data found for ticker: {ticker}")

    hist = hist.dropna(subset=["Close"])
    if hist.empty:
        raise ValueError(f"No valid closing prices found for ticker: {ticker}")
    closes = hist["Close"]
    ma_50 = float(closes.rolling(50).mean().iloc[-1]) if len(closes) >= 50 else None
    ma_200 = float(closes.rolling(200).mean().iloc[-1]) if len(closes) >= 200 else None

    try:
        info = t.info or {}
    except Exception:
        info = {}

    history_records = [
        {
            "date": str(date.date()),
            "open": _number(row["Open"]),
            "high": _number(row["High"]),
            "low": _number(row["Low"]),
            "close": round(float(row["Close"]), 4),
            "volume": int(row["Volume"])
            if _number(row["Volume"]) is not None else None,
        }
        for date, row in hist.iterrows()
    ]

    current = float(closes.iloc[-1])
    prev = float(closes.iloc[-2]) if len(closes) > 1 else current
    change_pct = round((current - prev) / prev * 100, 2) if prev else None

    return {
        "ticker": ticker.upper(),
        "period": period,
        "current_price": round(current, 4),
        "prev_close": round(prev, 4),
        "change_pct": change_pct,
        "week_52_high": _number(info.get("fiftyTwoWeekHigh")),
        "week_52_low": _number(info.get("fiftyTwoWeekLow")),
        "ma_50": round(ma_50, 4) if ma_50 is not None else None,
        "ma_200": round(ma_200, 4) if ma_200 is not None else None,
        "market_cap": _number(info.get("marketCap")),
        "avg_volume": _number(info.get("averageVolume")),
        "history": history_records,
    }


def get_financials(ticker: str) -> dict:
    """
    Fetch key financial statement data for a ticker.

    Returns a dict with income statement, balance sheet,
    and valuation metrics from the latest available period.
    """
    if not isinstance(ticker, str) or not ticker.strip():
        raise ValueError("A stock ticker is required")
    import yfinance as yf

    ticker = ticker.strip().upper()
    t = yf.Ticker(ticker)
    info = t.info

    income = t.income_stmt
    balance = t.balance_sheet

    def latest(df, row_name):
        try:
            return float(df.loc[row_name].iloc[0]) if row_name in df.index else None
        except Exception:
            return None

    return {
        "ticker": ticker.upper(),
        "market_cap": info.get("marketCap"),
        "pe_ratio": info.get("trailingPE"),
        "forward_pe": info.get("forwardPE"),
        "eps": info.get("trailingEps"),
        "revenue": latest(income, "Total Revenue"),
        "gross_profit": latest(income, "Gross Profit"),
        "operating_income": latest(income, "Operating Income"),
        "net_income": latest(income, "Net Income"),
        "total_assets": latest(balance, "Total Assets"),
        "total_debt": latest(balance, "Total Debt"),
        "cash": latest(balance, "Cash And Cash Equivalents"),
        "dividend_yield": info.get("dividendYield"),
        "sector": info.get("sector"),
        "industry": info.get("industry"),
        "summary": info.get("longBusinessSummary"),
    }
