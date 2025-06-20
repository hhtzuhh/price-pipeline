import asyncio, json, statistics, signal, os
from contextlib import asynccontextmanager
from confluent_kafka import Consumer
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.db import models

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

cfg = {
    "bootstrap.servers": BOOTSTRAP,
    "group.id": "ma-consumer-debug-1",
    "auto.offset.reset": "earliest",
    "enable.auto.commit": False,         # explicit commit after DB success
}

@asynccontextmanager
async def session_scope():
    async with AsyncSessionLocal() as session:
        yield session
        await session.commit()

async def handle(symbol: str):
    async with session_scope() as db:
        rows = (await db.execute(
            select(models.RawPrice.price)
            .where(models.RawPrice.symbol == symbol)
            .order_by(models.RawPrice.timestamp.desc())
            .limit(5)
        )).scalars().all()
        if len(rows) < 5:
            print(f"Not enough data for {symbol}")
            return
        ma = float(statistics.mean(rows))
        await db.merge(models.MovingAverage(
            symbol=symbol,
            window=5,
            ma_value=ma,
        ))

def main():
    c = Consumer(cfg)
    c.subscribe(["price-events"])

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    running = True
    signal.signal(signal.SIGINT, lambda *_: c.close())

    while running:
        msg = c.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Kafka err:", msg.error())
        
        try:
            data = json.loads(msg.value())
            print("Received:", data)
            loop.run_until_complete(handle(data["symbol"]))
            c.commit(msg)
        except Exception as e:
            print("Failed to handle message:", e)
    # mark as processed

if __name__ == "__main__":
    main()
