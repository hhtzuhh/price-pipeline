from fastapi import FastAPI
from app.api.prices import router as prices_router
from app.api.poll import router as poll_router
from app.api.ma import router as ma_router
from dotenv import load_dotenv

load_dotenv() # This loads variables from .env into os.environ


app = FastAPI(title="Market-Data Service (Y-Finance only v0)")
app.include_router(prices_router)
app.include_router(poll_router)
app.include_router(ma_router)
@app.get("/health")
def health():
    return {"status": "ok"}
