from memory import MemoryStore
from short_term import ShortTermContext
import time

# Init
memory_store = MemoryStore()
short_term = ShortTermContext()

# Test Parameters
user_id = "user_test"
user_name = "Test User"
user_email = "testuser@example.com"
session_id = "sess_test"

# ✅ STEP 1: Create User
memory_store.create_user(user_id, user_name, user_email)

# ✅ STEP 2: Simulate 5 Chat Messages
for i in range(5):
    user_message = f"User message {i + 1} about billing issue."
    assistant_message = f"Assistant reply {i + 1}"
    short_term.add_message(session_id, "user", user_message)
    short_term.add_message(session_id, "assistant", assistant_message)

    # Save Session Memory
    combined_convo = f"User: {user_message}\nAssistant: {assistant_message}"
    entity_store = {"billing_issue": "account 12345"}
    memory_store.save_memory(user_id, session_id, combined_convo, entity_store, conversation_count=i + 1)

    print(f"✅ Saved conversation {i + 1}")

# ✅ STEP 3: Check Long‑term Summaries
long_term_summaries = memory_store.load_long_term_summaries(user_id)
entities = memory_store.load_entities(user_id)

print("\n📄 Long‑term Summaries:", long_term_summaries)
print("\n🗄️ Entities:", entities)

# ✅ STEP 4: Short‑term Context Check
recent_chat = short_term.get_messages(session_id)
print("\n💬 Recent Chat Messages:", recent_chat)
