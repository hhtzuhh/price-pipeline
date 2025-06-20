import json, os
from confluent_kafka import Producer, KafkaException

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "")
_producer = Producer(
    {"bootstrap.servers": BOOTSTRAP, "enable.idempotence": True}
)

def send_price_event(dto: dict) -> None:
    """
    dto: {"symbol":"AAPL","price":214.8,"timestamp":"...","provider":"yfinance"}
    """
    try:
        _producer.produce(
            "price-events",
            key=dto["symbol"].encode(),
            value=json.dumps(dto).encode(),
        )
        # trigger delivery callbacks (non-blocking flush of librdkafka queue)
        _producer.poll(0)
    except BufferError:
        # local queue full – fall back to blocking flush
        _producer.flush()
        _producer.produce(
            "price-events",
            key=dto["symbol"].encode(),
            value=json.dumps(dto).encode(),
        )
