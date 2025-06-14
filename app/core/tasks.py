from app.providers.yahoo import fetch as fetch_yahoo
from app.db.session import AsyncSessionLocal
from app.db import models
from app.kafka.producer import send_price_event

async def poll_prices(symbols: list[str], provider: str):
    dtos=[]
    async with AsyncSessionLocal() as db:
        for sym in symbols:
            dto = await fetch_yahoo(sym)
            dto.provider = provider
            dtos.append(dto)
            db.add(models.RawPrice(
                symbol=dto.symbol,
                price=dto.price,
                timestamp=dto.timestamp,
                provider=provider,
            ))
        await db.commit()
        # 🔸 outside the DB session so we open a fresh one inside helper
    for dto in dtos:
        payload = dto.model_dump(mode="json")
        payload["window"] = 5  # include window info if needed
        send_price_event(payload)# send to Kafka

