# backend/auth_app/redis_subscriber.py
import redis
import os
import json
from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB, decode_responses=True)

pubsub = r.pubsub()
pubsub.subscribe("auth_events")

print("👂 Listening on Redis channel: auth_events")
for message in pubsub.listen():
    if message["type"] == "message":
        print("📩 Received:", json.loads(message["data"]))
