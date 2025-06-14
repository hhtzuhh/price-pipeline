from app.providers.yahoo import fetch as fetch_yahoo
from app.db.session import AsyncSessionLocal
from app.db import models
from app.core.ma import calculate_and_upsert_ma 

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
        # 🔸 outside the DB session so we open a fresh one inside helper
    for sym in symbols:
        await calculate_and_upsert_ma(sym, window=5)
    
