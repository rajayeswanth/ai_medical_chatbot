from langchain_community.chat_models import ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
import os
import json
from dotenv import load_dotenv

load_dotenv()

# LLM for refining the query
llm = ChatOpenAI(model_name="gpt-4", openai_api_key=os.environ["OPENAI_API_KEY"], max_tokens=500)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-mpnet-base-v2")
vectorstore = Chroma(persist_directory="./chroma_db", embedding_function=embedding_model)

REFINE_PROMPT = """
Original User Query:
{user_query}

Based on this, rewrite and optimize the query for best retrieval results.
-Include related key words and phrases from the user query in the optimized query.
-If you find any grammar or spelling errors, correct them in the optimized query.
Return JSON:
{{"optimized_query": "<your optimized version>"}}
"""

def refine_query(user_query):
    """Refine the user query for better retrieval."""
    resp = llm.predict(REFINE_PROMPT.format(user_query=user_query))
    return json.loads(resp)["optimized_query"]

def retrieve_docs(user_query, k=5):
    """Perform retrieval after refining the user query."""
    optimized_query = refine_query(user_query)
    results = vectorstore.similarity_search(optimized_query, k=k)
    return results

# Usage:
# results = retrieve_docs("What are the statistics for global health in 2023?")
