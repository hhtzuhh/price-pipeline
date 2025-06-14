from fastapi import FastAPI
from app.api.prices import router as prices_router
from app.api.poll import router as poll_router


app = FastAPI(title="Market-Data Service (Y-Finance only v0)")
app.include_router(prices_router)
app.include_router(poll_router)

@app.get("/health")
def health():
    return {"status": "ok"}
