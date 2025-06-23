from memory import MemoryStore
from short_term import ShortTermContext

memory_store = MemoryStore()
short_term = ShortTermContext()

user_ids = ["user_test_1", "user_test_2"]
session_ids = ["sess_1", "sess_2"]

# ✅ TEST 1: Multiple Users
for user_id, session_id in zip(user_ids, session_ids):
    memory_store.create_user(user_id, f"Test User {user_id[-1]}", f"{user_id}@example.com")

    # ✅ TEST 2: High Number of Messages (100 per user)
    for i in range(100):  # You can adjust between 50–100
        user_message = f"User {user_id[-1]} message {i + 1}"
        assistant_message = f"Assistant reply for user {user_id[-1]}, message {i + 1}"

        short_term.add_message(session_id, "user", user_message)
        short_term.add_message(session_id, "assistant", assistant_message)

        combined_convo = f"User: {user_message}\nAssistant: {assistant_message}"
        entity_store = {"context": f"interaction_{i + 1}"}
        memory_store.save_memory(user_id, session_id, combined_convo, entity_store, conversation_count=i + 1)

    # ✅ Final Check
    recent_chat = short_term.get_messages(session_id)
    long_term_summaries = memory_store.load_long_term_summaries(user_id)
    entities = memory_store.load_entities(user_id)

    print(f"\n👤 {user_id}:")
    print(f"💬 Recent Messages: {len(recent_chat)} (expecting max ~10 due to limit!) ")
    print(f"📃 Long‑term Summaries: {long_term_summaries}")
    print(f"🗄️ Entities: {entities}")

# ✅ Done
