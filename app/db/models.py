from sqlalchemy import Column, String, Numeric, DateTime, Integer, JSON
from sqlalchemy.sql import func
from uuid import uuid4
from .session import Base

class RawPrice(Base):
    __tablename__ = "raw_prices"
    id        = Column(String, primary_key=True, default=lambda: str(uuid4()))
    symbol    = Column(String, index=True)
    price     = Column(Numeric)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    provider  = Column(String)
    payload   = Column(JSON)

class PollJob(Base):
    __tablename__ = "poll_jobs"
    id        = Column(String, primary_key=True, default=lambda: str(uuid4()))
    symbols   = Column(JSON)        # ["AAPL","MSFT"]
    interval  = Column(Integer)     # seconds
    provider  = Column(String)
