from pydantic import BaseModel, Field
from datetime import datetime, timezone

class PriceDTO(BaseModel):
    symbol: str
    price: float
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    provider: str = "default"
