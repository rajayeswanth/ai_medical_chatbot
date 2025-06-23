from context_builder import build_context
from planner import plan
from retrieval import retrieve_docs
from answer import get_final_answer
from memory import MemoryStore
from short_term import ShortTermContext

memory_store = MemoryStore()
short_term = ShortTermContext()


def handle_query(user_id, session_id, user_query):
    """Final orchestration for user query."""
    # 1️⃣ Build Context
    context = build_context(user_id, session_id, user_query)

    # 2️⃣ Plan
    decision = plan(
        user_query,
        recent_chat=context["recent_chat"],
        long_term_summaries=context["long_term_summaries"],
        entities=context["entities"],
    )

    print("\n[DEBUG] Planner Output:", decision)

    # 3️⃣ Answer
    if decision["action"] == "direct_answer":
        reply = get_final_answer(
            user_query,
            retrieved_docs=[], 
            recent_chat=context["recent_chat"],
            long_term_summaries=context["long_term_summaries"],
            entities=context["entities"],
        )
    else:
        results = retrieve_docs(decision["query"])
        reply = get_final_answer(
            user_query,
            retrieved_docs=results,
            recent_chat=context["recent_chat"],
            long_term_summaries=context["long_term_summaries"],
            entities=context["entities"],
        )

    # 4️⃣ Save Short‑term Context
    short_term.add_message(session_id, "user", user_query)
    short_term.add_message(session_id, "assistant", reply)

    return reply

# Usage:
# reply = handle_query("user123", "sess456", "What's the status of my billing issue?")
# print(reply)
