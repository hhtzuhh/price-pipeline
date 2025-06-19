from fastapi import Depends, Query
from app.providers import get_provider, PriceProvider

async def provider_dep(
    provider: str = Query("yfinance")  # default via query param
) -> PriceProvider:
    return get_provider(provider)