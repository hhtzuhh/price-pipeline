from fastapi import APIRouter, HTTPException, Query, Depends
from app.db.session import get_session
from app.db import models
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.core.ma import calculate_and_upsert_ma
from app.kafka.producer import send_price_event
from app.providers.base import PriceProvider
from app.providers.deps import provider_dep
router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("/latest")
async def latest(
    symbol: str = Query(...),
    provider: "PriceProvider" = Depends(provider_dep),
    db: AsyncSession = Depends(get_session),
):
    # print(f"provider: {provider}")
    dto = await provider.fetch(symbol)

    # 🔸 save raw row
    new_row = models.RawPrice(
        symbol=dto.symbol,
        price=dto.price,
        timestamp=dto.timestamp,
        provider=provider.name,
    )
    db.add(new_row)
    await db.commit()
    send_price_event(dto.model_dump(mode="json"))

    return dto.model_dump()         # same JSON as before


