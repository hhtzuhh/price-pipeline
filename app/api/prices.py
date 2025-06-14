from fastapi import APIRouter, HTTPException, Query, Depends
from app.providers.yahoo import fetch as fetch_yahoo
from app.db.session import get_session
from app.db import models
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder
from app.core.ma import calculate_and_upsert_ma
from app.kafka.producer import send_price_event

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("/latest")
async def latest(
    symbol: str = Query(...),
    provider: str | None = Query(None),
    db: AsyncSession = Depends(get_session),
):
    provider = provider or "yfinance"
    # … check DB cache if you like …

    dto = await fetch_yahoo(symbol)

    # 🔸 save raw row
    new_row = models.RawPrice(
        symbol=dto.symbol,
        price=dto.price,
        timestamp=dto.timestamp,
        provider=provider,
        # payload=jsonable_encoder(dto),
    )
    db.add(new_row)
    await db.commit()
    send_price_event(dto.model_dump(mode="json"))

    return dto.model_dump()         # same JSON as before


