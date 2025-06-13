from fastapi import APIRouter, HTTPException, Query, Depends
from app.providers.yahoo import fetch as fetch_yahoo
from app.db.session import get_session
from app.db import models
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder


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

    return dto.model_dump()         # same JSON as before


