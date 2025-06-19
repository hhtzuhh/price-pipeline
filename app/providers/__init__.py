# app/providers/__init__.py
from .yahoo import YahooProvider
from .alpha_vantage import AlphaVantageProvider          # add as you go
from .base import PriceProvider
_PROVIDER_REGISTRY: dict[str, "PriceProvider"] = {
    p.name: p() for p in (YahooProvider, AlphaVantageProvider)
}

def get_provider(name: str) -> "PriceProvider":
    try:
        return _PROVIDER_REGISTRY[name]
    except KeyError:
        raise ValueError(f"Unknown provider: {name!r}")
