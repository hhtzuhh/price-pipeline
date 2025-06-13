from fastapi import APIRouter, HTTPException, Query
from app.providers.yahoo import fetch as fetch_yahoo

router = APIRouter(prefix="/prices", tags=["prices"])

@router.get("/latest")
async def latest(
    symbol: str = Query(..., min_length=1, examples=["AAPL"])
):
    try:
        dto = await fetch_yahoo(symbol)
    except Exception as exc:
        # yfinance throws on invalid tickers, network fails, etc.
        raise HTTPException(status_code=502, detail=str(exc))

    # Return exactly the shape required in the assignment
    return {
        "symbol": dto.symbol,
        "price": dto.price,
        "timestamp": dto.timestamp.isoformat(),
        "provider": dto.provider,
    }

