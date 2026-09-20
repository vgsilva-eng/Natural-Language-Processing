__all__ = ["get_stock_data", "get_financials", "fetch_news", "AgentMemory"]


def __getattr__(name):
    """Load the requested tool without importing unrelated API clients."""
    if name not in __all__:
        raise AttributeError(name)
    from importlib import import_module

    module_names = {
        "get_stock_data": "yfinance_tool",
        "get_financials": "yfinance_tool",
        "fetch_news": "news_tool",
        "AgentMemory": "memory_tool",
    }
    return getattr(import_module(f".{module_names[name]}", __name__), name)
