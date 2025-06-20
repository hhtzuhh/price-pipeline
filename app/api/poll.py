from fastapi import APIRouter, BackgroundTasks, status, Depends
from pydantic import BaseModel, Field
from uuid import uuid4
from app.core.scheduler import scheduler
from app.core.tasks import poll_prices
from app.db.session import get_session
from app.db import models
from app.providers import get_provider, PriceProvider
router = APIRouter(prefix="/prices", tags=["poll"])

class PollRequest(BaseModel):
    symbols: list[str] = Field(..., min_items=1)
    interval: int = Field(..., gt=0)          # seconds
    provider: str = "default"

@router.post("/poll", status_code=status.HTTP_202_ACCEPTED)
async def create_poll_job(req: PollRequest, db = Depends(get_session)):
    job_id = f"poll_{uuid4().hex[:8]}"

    # 1️⃣  persist cfg
    db.add(models.PollJob(
        id=job_id,
        symbols=req.symbols,
        interval=req.interval,
        provider=req.provider,
    ))
    await db.commit()
    
    provider: PriceProvider = get_provider(req.provider)


    # 2️⃣  schedule task
    scheduler.add_job(
        poll_prices,
        "interval",
        id=job_id,
        seconds=req.interval, # run this job every `interval` seconds
        args=[req.symbols, provider],
        coalesce=True, max_instances=1, replace_existing=True,
    )

    return {
        "job_id": job_id,
        "status": "accepted",
        "config": req.model_dump(exclude_none=True),
    }
