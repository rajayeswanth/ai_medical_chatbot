from memory import MemoryStore
from short_term import ShortTermContext

memory_store = MemoryStore()
short_term = ShortTermContext()

def build_context(user_id, session_id, user_query):
    """Construct final context for the LLM."""
    recent_chat = short_term.get_messages(session_id)              # ✅ Short‑term
    long_term_summaries = memory_store.load_long_term_summaries(user_id)  # ✅ Long‑term
    entities = memory_store.load_entities(user_id)                      # ✅ Entities

    return {
        "user_query": user_query,
        "recent_chat": recent_chat,
        "long_term_summaries": long_term_summaries,
        "entities": entities,
    }

# Usage:
# context = build_context("user123", "sess456", "What's the status of my billing issue?")
# print(context)
