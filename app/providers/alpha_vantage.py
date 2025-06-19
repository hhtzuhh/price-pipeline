import httpx  
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
from app.providers.schema import PriceDTO
from app.providers.base import PriceProvider
import os # To get API key from environment variables
from dotenv import load_dotenv

_executor = ThreadPoolExecutor(max_workers=3)   # one is fine for demo

load_dotenv() 

class AlphaVantageProvider(PriceProvider):
    name = "alpha_vantage"
    _base_url = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str = None):
        super().__init__()
        # It's good practice to get API keys from environment variables
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Alpha Vantage API key not provided. "
                "Set ALPHA_VANTAGE_API_KEY environment variable or pass it during initialization."
            )

    def _blocking_fetch(self, symbol: str) -> PriceDTO:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": self.api_key
        }
        try:
            # Use httpx.Client for synchronous call within the thread
            with httpx.Client() as client:
                response = client.get(self._base_url, params=params)
                response.raise_for_status()  # Raise an exception for HTTP errors
                data = response.json()

            # Alpha Vantage API returns data under "Global Quote"
            global_quote = data.get("Global Quote", {})
            
            # The key for the latest price is typically "05. price"
            price_str = global_quote.get("05. price")
            if not price_str:
                raise ValueError(f"Could not retrieve price for {symbol}. API response: {data}")
            
            price = float(price_str)
            return PriceDTO(symbol=symbol.upper(), price=price, provider=self.name)
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"HTTP error fetching from Alpha Vantage for {symbol}: {e.response.status_code} - {e.response.text}") from e
        except Exception as e:
            raise RuntimeError(f"Error fetching from Alpha Vantage for {symbol}: {e}") from e

    async def fetch(self, symbol: str) -> PriceDTO:
        """Run the blocking fetch in a thread so FastAPI stays async-friendly."""
        from asyncio import get_running_loop
        loop = get_running_loop()
        return await loop.run_in_executor(_executor, self._blocking_fetch, symbol)