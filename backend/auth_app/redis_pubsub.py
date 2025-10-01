# backend/auth_app/redis_pubsub.py
import os
import redis
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
REDIS_DECODE = os.getenv("REDIS_DECODE", "True").lower() in ("1", "true", "yes")

# Create Redis client
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    db=REDIS_DB,
    decode_responses=REDIS_DECODE
)


def publish_event(channel: str, event: str, payload: dict) -> None:
    """
    Publish an event to a Redis channel.
    """
    message = {
        "event": event,
        "data": payload,
    }
    try:
        result = redis_client.publish(channel, json.dumps(message))
        print(f"📤 Redis published → channel={channel}, event={event}, delivered_to={result}, payload={payload}")
    except Exception as e:
        print(f"[redis_pubsub.publish_event] failed to publish to {channel}: {e}")
        
        
        
        
if __name__ == "__main__":
    # Quick connectivity check
    try:
        redis_client.ping()
        print("✅ Redis connected")
    except Exception as e:
        print("❌ Redis connection failed:", e)

