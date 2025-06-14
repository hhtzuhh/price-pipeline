from confluent_kafka import Consumer, KafkaException
import json
import os

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")

cfg = {
    "bootstrap.servers": BOOTSTRAP,
    "group.id": "test-consumer-1234",  # use a fresh one
    "auto.offset.reset": "earliest",
    "enable.auto.commit": True,
}

def print_assignment(consumer, partitions):
    print("📦 Assigned partitions:", partitions)

c = Consumer(cfg)
c.subscribe(["price-events"], on_assign=print_assignment)

print("🔥 Consumer started... waiting for messages")

try:
    while True:
        msg = c.poll(1.0)
        if msg is None:
            continue
        if msg.error():
            print("Kafka error:", msg.error())
            continue

        val = msg.value()
        try:
            print("✅ Received raw:", val)
            data = json.loads(val.decode("utf-8"))
            print("✅ Decoded JSON:", data)
        except Exception as e:
            print("❌ Failed to decode:", e)

except KeyboardInterrupt:
    print("👋 Stopping consumer...")
finally:
    c.close()
