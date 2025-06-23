# import os
# import json
# from dotenv import load_dotenv
# from langchain_community.chat_models import ChatOpenAI

# load_dotenv()

# llm = ChatOpenAI(model_name="gpt-4.1-nano",
#                 openai_api_key=os.environ["OPENAI_API_KEY"],
#                 max_tokens=500)

# PROMPT_TEMPLATE = """
# You are an intelligent planner for a medical assistant.

# CONTEXT:
# Short‑term Chat: {recent_chat}
# Long‑term Summaries: {long_term_summaries}
# Entities: {entities}

# User Query: {user_query}

# DECISION RULES:
# - DIRECTLY ANSWER if the user's query clearly relates to information present in the context (Short‑term Chat, Long‑term Summaries, Entities).
# - IF NOT, or if it's a general knowledge or medical information request NOT covered by context, return an action to RETRIEVE DOCS.
# - Always assume retrieval if context is irrelevant or too sparse.

# Return JSON:
# {{"action": "direct_answer"}} 
# or 
# {{"action": "retrieve_docs", "query": "<optimized query>"}}
# """

# def plan(user_query, recent_chat, long_term_summaries, entities) -> dict:
#     """Make a decision using user context."""
#     prompt = PROMPT_TEMPLATE.format(
#         recent_chat=recent_chat,
#         long_term_summaries=long_term_summaries,
#         entities=entities,
#         user_query=user_query,
#     )
#     resp = llm.predict(prompt)

#     # ✅ Safely Parse Response
#     try:
#         return json.loads(resp)
#     except json.JSONDecodeError:
#         return {"action": "retrieve_docs", "query": user_query}

# # Usage:
# # decision = plan(user_query, recent_chat, long_term_summaries, entities)

import os
import json
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI

load_dotenv()

llm = ChatOpenAI(model_name="gpt-4.1-nano",
                openai_api_key=os.environ["OPENAI_API_KEY"],
                max_tokens=500)

PROMPT_TEMPLATE = """
You are an intelligent planner for a medical assistant.

CONTEXT:
Short‑term Chat: {recent_chat}
Long‑term Summaries: {long_term_summaries}
Entities: {entities}

User Query: {user_query}

DECISION RULES:
- If the user query is related to medical or health topics, RETURN:
    {{"action": "retrieve_docs", "query": "<optimized medical query>"}}
- If the user query is NOT related to medical or health topics (general questions like math, restaurants, greetings), RETURN:
    {{"action": "direct_answer"}}
- Never respond with "I don't have information".
- Never use retrieval for general or unrelated questions.

Return JSON only:
{{"action": "direct_answer"}} OR {{"action": "retrieve_docs", "query": "<optimized medical query>"}}
"""

def plan(user_query, recent_chat, long_term_summaries, entities) -> dict:
    """Make a decision using user context."""
    prompt = PROMPT_TEMPLATE.format(
        recent_chat=recent_chat,
        long_term_summaries=long_term_summaries,
        entities=entities,
        user_query=user_query,
    )
    resp = llm.predict(prompt)

    # ✅ Safely Parse Response
    try:
        return json.loads(resp)
    except json.JSONDecodeError:
        return {"action": "retrieve_docs", "query": user_query}
