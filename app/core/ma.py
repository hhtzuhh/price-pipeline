# app/core/ma.py
from sqlalchemy import select, func
from app.db.models import RawPrice, MovingAverage
from app.db.session import AsyncSessionLocal

async def calculate_and_upsert_ma(symbol: str, window: int = 5):
    """
    Fetch the last <window> prices for <symbol>, compute the average,
    upsert into moving_averages.
    """
    async with AsyncSessionLocal() as db:
        # 1. grab last N prices
        stmt = (
            select(RawPrice.price)
            .where(RawPrice.symbol == symbol)
            .order_by(RawPrice.timestamp.desc())
            .limit(window)
        )
        rows = (await db.execute(stmt)).scalars().all()
        if len(rows) < window:      # not enough data yet → skip
            return

        ma_val = float(sum(rows) / window)

        # 2. upsert (one row per symbol+window)
        await db.merge(
            MovingAverage(
                symbol=symbol,
                window=window,
                ma_value=ma_val,
            )
        )
        await db.commit()
