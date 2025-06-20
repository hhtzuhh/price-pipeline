from app.db.session import AsyncSessionLocal
from app.db import models
from app.kafka.producer import send_price_event
from app.providers import PriceProvider
async def poll_prices(symbols: list[str], provider: PriceProvider):
    dtos=[]
    async with AsyncSessionLocal() as db:
        for sym in symbols:
            dto = await provider.fetch(sym)
            dtos.append(dto)
            db.add(models.RawPrice(
                symbol=dto.symbol,
                price=dto.price,
                timestamp=dto.timestamp,
                provider=dto.provider,
            ))
        await db.commit()
        # 🔸 outside the DB session so we open a fresh one inside helper
    for dto in dtos:
        payload = dto.model_dump(mode="json")
        payload["window"] = 5  # include window info if needed
        send_price_event(payload)# send to Kafka

