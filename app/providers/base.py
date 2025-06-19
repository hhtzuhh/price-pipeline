# app/providers/base.py
from typing import Protocol
from app.providers.schema import PriceDTO

class PriceProvider(Protocol):
    name: str
    async def fetch(self, symbol: str) -> PriceDTO: ...
