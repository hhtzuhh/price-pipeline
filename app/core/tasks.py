from app.providers.yahoo import fetch as fetch_yahoo
from app.db.session import AsyncSessionLocal
from app.db import models

async def poll_prices(symbols: list[str], provider: str):
    async with AsyncSessionLocal() as db:
        for sym in symbols:
            dto = await fetch_yahoo(sym)
            db.add(models.RawPrice(
                symbol=dto.symbol,
                price=dto.price,
                timestamp=dto.timestamp,
                provider=provider,
            ))
        await db.commit()
    
