import yfinance as yf
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel, Field
from app.providers.schema import PriceDTO
from app.providers.base import PriceProvider

_executor = ThreadPoolExecutor(max_workers=3)   # one is fine for demo


class YahooProvider(PriceProvider):
    name = "yfinance"

    def _blocking_fetch(self,symbol: str) -> PriceDTO:
        tkr = yf.Ticker(symbol)
        # Use .fast_info when available (newer yfinance); fallback to .info
        try:
            price = tkr.fast_info["lastPrice"]
        except Exception:
            price = tkr.info["regularMarketPrice"]
        return PriceDTO(symbol=symbol.upper(), price=float(price), provider=self.name)


    async def fetch(self, symbol: str) -> PriceDTO:
        """Run the blocking fetch in a thread so FastAPI stays async-friendly."""
        from asyncio import get_running_loop
        loop = get_running_loop()
        return await loop.run_in_executor(_executor, self._blocking_fetch, symbol)
