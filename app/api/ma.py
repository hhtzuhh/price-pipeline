# app/api/ma.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from app.db.session import get_session
from app.db.models import MovingAverage

router = APIRouter(prefix="/prices", tags=["ma"])

@router.get("/ma")
async def get_ma(
    symbol: str = Query(..., examples=["AAPL"]),
    window: int = Query(5, ge=2),
    db = Depends(get_session),
):
    
    result = await db.execute(
        select(MovingAverage)
        .where(MovingAverage.symbol == symbol.upper(),
            MovingAverage.window == window)
        .order_by(MovingAverage.calc_time.desc())
        .limit(1)
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(404, "Moving average not available yet")
    return {
        "symbol": symbol.upper(),
        "window": window,
        "moving_average": row.ma_value,
        "calc_time": row.calc_time.isoformat(),
    }
