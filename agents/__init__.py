__all__ = ["ResearchAgent", "NewsAgent", "EarningsAgent", "MarketAgent"]


def __getattr__(name):
    """Load specialists only when needed, without requiring every API SDK."""
    if name not in __all__:
        raise AttributeError(name)
    from importlib import import_module

    module_names = {
        "ResearchAgent": "research_agent",
        "NewsAgent": "news_agent",
        "EarningsAgent": "earnings_agent",
        "MarketAgent": "market_agent",
    }
    return getattr(import_module(f".{module_names[name]}", __name__), name)
