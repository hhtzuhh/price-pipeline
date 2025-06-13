import yfinance as yf
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, Field

_executor = ThreadPoolExecutor(max_workers=3)   # one is fine for demo


class PriceDTO(BaseModel):
    symbol: str
    price: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str = "yfinance"


def _blocking_fetch(symbol: str) -> PriceDTO:
    tkr = yf.Ticker(symbol)
    # Use .fast_info when available (newer yfinance); fallback to .info
    try:
        price = tkr.fast_info["lastPrice"]
    except Exception:
        price = tkr.info["regularMarketPrice"]
    return PriceDTO(symbol=symbol.upper(), price=float(price))


async def fetch(symbol: str) -> PriceDTO:
    """Run the blocking fetch in a thread so FastAPI stays async-friendly."""
    from asyncio import get_running_loop
    loop = get_running_loop()
    return await loop.run_in_executor(_executor, _blocking_fetch, symbol)
