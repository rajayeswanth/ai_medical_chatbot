import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

class ShortTermContext:
    """Keeps recent chat context in Redis."""
    def __init__(self, host="localhost", port=6379, db=0, max_turns=10):
        self.client = redis.StrictRedis(host=host, port=port, db=db)
        self.max_turns = max_turns

    def add_message(self, session_id, role, message):
        """Add a message to the recent context."""
        key = f"chat:{session_id}"
        self.client.rpush(key, json.dumps({"role": role, "message": message}))
        self.client.ltrim(key, -self.max_turns, -1)

    def get_messages(self, session_id):
        """Get the recent messages for the session."""
        key = f"chat:{session_id}"
        messages = self.client.lrange(key, 0, -1)
        return [json.loads(msg) for msg in messages]

# Usage:
# short_term = ShortTermContext()
# short_term.add_message("sess123", "user", "Hello, how are you?")
# recent = short_term.get_messages("sess123")
# print(recent)
