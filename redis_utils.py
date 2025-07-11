# import redis
# import json
# import os

# redis_client = redis.Redis(
#     host=os.getenv("REDIS_HOST", "localhost"),
#     port=int(os.getenv("REDIS_PORT", 6379)),
#     db=0,
#     decode_responses=True
# )

# def save_thread(session_id: str, title: str, timestamp: float):
#     # Only save to Redis if title is not default/placeholder
#     if not title or title.strip().lower() == "untitled chat":
#         return

#     key = f"thread:{session_id}"
#     data = {
#         "title": title,
#         "timestamp": timestamp
#     }
#     redis_client.hset(key, mapping=data)
#     redis_client.zadd("thread_index", {session_id: timestamp})

# def get_all_threads():
#     # Returns session IDs sorted by time (latest first)
#     session_ids = redis_client.zrevrange("thread_index", 0, -1)
#     threads = []
#     for sid in session_ids:
#         data = redis_client.hgetall(f"thread:{sid}")
#         if data:
#             threads.append({
#                 "session_id": sid,
#                 "title": data.get("title") or "Untitled",
#                 "timestamp": float(data.get("timestamp", 0))
#             })
#     return threads


import redis
import json
import os
from datetime import datetime

# Redis connection
redis_client = redis.Redis(
    host=os.getenv("REDIS_HOST", "localhost"),
    port=int(os.getenv("REDIS_PORT", 6379)),
    db=0,
    decode_responses=True
)

# Save thread metadata (title + timestamp)
def save_thread(session_id: str, title: str, timestamp: float):
    if not title or title.strip().lower() == "untitled chat":
        return

    redis_client.hset(f"thread:{session_id}", mapping={
        "title": title,
        "timestamp": timestamp
    })

    redis_client.zadd("thread_index", {session_id: timestamp})

# Save full chat turn (user + assistant)
def save_chat_turn(session_id: str, user_query: str, gpt_response: str):
    key = f"chat:{session_id}"
    timestamp = datetime.utcnow().timestamp()

    # Store user and assistant turns as separate JSON entries
    redis_client.rpush(key, json.dumps({
        "role": "user",
        "content": user_query,
        "timestamp": timestamp
    }))
    redis_client.rpush(key, json.dumps({
        "role": "assistant",
        "content": gpt_response,
        "timestamp": timestamp
    }))

# Retrieve all chat messages for a session
def get_full_conversation(session_id: str):
    key = f"chat:{session_id}"
    raw = redis_client.lrange(key, 0, -1)
    return [json.loads(m) for m in raw]

# Retrieve all threads for sidebar display (title + timestamp)
def get_all_threads():
    session_ids = redis_client.zrevrange("thread_index", 0, -1)
    threads = []

    for sid in session_ids:
        data = redis_client.hgetall(f"thread:{sid}")
        if data:
            threads.append({
                "session_id": sid,
                "title": data.get("title", "Untitled"),
                "timestamp": float(data.get("timestamp", 0))
            })

    return threads

# Optional: Get last N messages for LLM context
def get_recent_context(session_id: str, limit: int = 10):
    key = f"chat:{session_id}"
    raw = redis_client.lrange(key, -limit, -1)
    return [json.loads(m) for m in raw]
