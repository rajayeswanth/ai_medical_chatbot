# import os
# from langchain_community.chat_models import ChatOpenAI
# from dotenv import load_dotenv

# load_dotenv()

# llm = ChatOpenAI(model_name="gpt-4.1-nano", openai_api_key=os.environ["OPENAI_API_KEY"], max_tokens=500)

# FINAL_ANSWER_PROMPT = """
# You are an expert medical assistant. 

# Context:
# {context}

# User Query:
# {user_query}

# Instructions:
# - Use only the context.
# - Answer clearly, concisely, and helpfully.
# - Do not invent information.s
# - Answer naturally, concisely, and helpfully.
# - dont hallucinate information, only give relevant information.
# - if you dont have information, dont say "The provided context does not include specific information about child cancer"., instead get the information from the retrieved docs.
#    related information and tell the user this is related information.
# - for any non meical user queries like social media, math, restaurants, games, etc, if it doesnt have any medical keywords, just say "I don't have enough information to help with that."
# Final Answer:
# """

# def get_final_answer(user_query, retrieved_docs, recent_chat, long_term_summaries, entities):
#     """Get the final answer from LLM using retrieved documents + context."""
#     combined_docs = '\n'.join([doc.page_content for doc in retrieved_docs])
#     context = f"""
#     Recent Chat: {recent_chat}
#     Long‑Term Summaries: {long_term_summaries}
#     Entities: {entities}
#     Retrieved Info:
#     {combined_docs}
#     """
#     return llm.predict(FINAL_ANSWER_PROMPT.format(context=context, user_query=user_query))

# # Usage:
# # final_answer = get_final_answer(user_query, results, recent_chat, long_term_summaries, entities)


import torch
import os
from dotenv import load_dotenv
# from test_finetune import model, tokenizer  # Fine-tuned Mistral
from langchain_community.chat_models import ChatOpenAI  # Old Model

load_dotenv()

# Old Model Init
llm = ChatOpenAI(model_name="gpt-4.1-nano",
                openai_api_key=os.environ["OPENAI_API_KEY"],
                max_tokens=500)

FINAL_ANSWER_PROMPT = """
You are an expert medical assistant.

Context:
{context}

User Query:
{user_query}

Instructions:
- Use only the context.
- Answer clearly, concisely, and helpfully.
- Do not invent information.
- Do not say "The provided context does not include specific information..."
- If context doesn’t have exact information, relate it if possible and say this is related information.
- For any NON‑MEDICAL questions (math, restaurants, games, etc.), just reply:
  "I don't have enough information to help with that."
Final Answer:
"""

def fine_tuned_answer(prompt, max_new_tokens=500):
    """Use fine-tuned Mistral for generation."""
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
    with torch.no_grad():
        output = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )
    return tokenizer.decode(output[0], skip_special_tokens=True)

def get_final_answer(user_query, retrieved_docs, recent_chat, long_term_summaries, entities, use_fine_tuned=False):
    """Get final answer using either the old ChatOpenAI or the new fine-tuned Mistral."""
    combined_docs = '\n'.join([doc.page_content for doc in retrieved_docs])
    context = f"""
    Recent Chat: {recent_chat}
    Long‑Term Summaries: {long_term_summaries}
    Entities: {entities}
    Retrieved Info:
    {combined_docs}
    """
    prompt = FINAL_ANSWER_PROMPT.format(context=context, user_query=user_query)

    if use_fine_tuned:
        return fine_tuned_answer(prompt)
    else:
        return llm.predict(prompt)