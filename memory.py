import os
import psycopg2
import json
from datetime import datetime
from dotenv import load_dotenv
from langchain_community.chat_models import ChatOpenAI
import re

load_dotenv()


class MemoryStore:
    def __init__(self, max_turns_for_summary=5, max_long_term_records=10):
        """Initialize database connections and settings."""
        self.conn_params = {
            "dbname": os.getenv("POSTGRES_DB"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "host": os.getenv("POSTGRES_HOST"),
            "port": os.getenv("POSTGRES_PORT"),
        }
        self.max_turns_for_summary = max_turns_for_summary
        self.max_long_term_records = max_long_term_records
        self.llm = ChatOpenAI(model_name="gpt-4.1-nano", openai_api_key=os.environ["OPENAI_API_KEY"])

    # USERS
    def create_user(self, user_id, name, email):
        """Create a new user if not exists."""
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO users (user_id, name, email) 
            VALUES (%s, %s, %s) ON CONFLICT (user_id) DO NOTHING
        """, (user_id, name, email))
        conn.commit()
        cursor.close()
        conn.close()

    # SESSION MEMORIES
    def save_memory(self, user_id, session_id, conversation_text, entity_store, conversation_count):
        """Save or update user memory for a specific session."""
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_memories (user_id, session_id, last_seen, conversation_count, last_conversation, entity_store) 
            VALUES (%s, %s, %s, %s, %s, %s) 
            ON CONFLICT (user_id, session_id) DO UPDATE SET 
                last_seen = EXCLUDED.last_seen,
                conversation_count = EXCLUDED.conversation_count,
                last_conversation = EXCLUDED.last_conversation,
                entity_store = EXCLUDED.entity_store
        """, (
            user_id,
            session_id,
            datetime.utcnow(),
            conversation_count,
            conversation_text[:500],
            json.dumps(entity_store),
        ))
        conn.commit()
        cursor.close()
        conn.close()

        # Trigger long-term summary if threshold met
        if conversation_count >= self.max_turns_for_summary:
            self._process_for_long_term(user_id, conversation_text, entity_store)

    def load_memory(self, user_id, session_id):
        """Load existing user memory for a specific session."""
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT conversation_count, last_conversation, entity_store
            FROM user_memories 
            WHERE user_id = %s AND session_id = %s
        """, (user_id, session_id))
        result = cursor.fetchone()
        conn.close()
        if result:
            conversation_count, last_conversation, entity_store = result
            return {
                "conversation_count": conversation_count,
                "last_conversation": last_conversation,
                "entity_store": entity_store,
            }
        return None

    # LONG-TERM SUMMARIES
    def _process_for_long_term(self, user_id, conversation_text, entity_store):
        """Use LLM to extract long‑term context and entities."""
        long_term_summaries = self.load_long_term_summaries(user_id)
        combined_summary = " ".join(long_term_summaries) if long_term_summaries else ""

        prompt = f"""
        You are an expert in extracting long‑term context.
        User's existing summary:
        {combined_summary}
        New conversation:
        {conversation_text}
        New entities:
        {entity_store}
        Task:
        1. Summarize and merge into a longer summary.
        2. Keep it concise and focused.
        3. Extract important entities as JSON.
        Output JSON:
        {{"summary": "<new consolidated summary>", "entities": {{"key": "value"}}}}
        """
        resp = self.llm.predict(prompt)

        result = None
        # Try direct load
        try:
            result = json.loads(resp)
        except json.JSONDecodeError:
            # Try extracting JSON block
            match = re.search(r'\{.*\}', resp, re.DOTALL)
            if match:
                candidate = match.group(0)

                # Try fix common trailing commas
                candidate = re.sub(r',(\s*[}\]])', r'\1', candidate)

                try:
                    result = json.loads(candidate)
                except json.JSONDecodeError:
                    # Final fallback
                    result = {"summary": combined_summary, "entities": entity_store}
            else:
                result = {"summary": combined_summary, "entities": entity_store}

        # Save consolidated summary
        self.save_long_term_summary(user_id, result.get("summary", combined_summary))

        # Save updated entities
        for entity_name, entity_data in result.get("entities", {}).items():
            self.save_entity(user_id, entity_name, entity_data)

    def save_long_term_summary(self, user_id, summary_text):
        """Save a long-term conversation summary for the user."""
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_summaries (user_id, created_at, summary)
            VALUES (%s, %s, %s)
        """, (user_id, datetime.utcnow(), summary_text))
        conn.commit()
        cursor.close()
        conn.close()
        self._prune_long_term_summaries(user_id)

    def load_long_term_summaries(self, user_id, limit=5):
        """Load the latest long-term summaries for the user."""
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT summary FROM user_summaries
            WHERE user_id = %s
            ORDER BY created_at DESC
            LIMIT %s
        """, (user_id, limit))
        results = [row[0] for row in cursor.fetchall()]
        conn.close()
        return results

    def _prune_long_term_summaries(self, user_id):
        """Keep long-term summaries within limit by removing oldest ones."""
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM user_summaries
            WHERE user_id = %s
            ORDER BY created_at ASC
        """, (user_id,))
        ids = [row[0] for row in cursor.fetchall()]
        if len(ids) > self.max_long_term_records:
            ids_to_remove = ids[:-self.max_long_term_records]
            for id_ in ids_to_remove:
                cursor.execute("DELETE FROM user_summaries WHERE id = %s", (id_,))
            conn.commit()
        cursor.close()
        conn.close()

    # ENTITY STORAGE
    def save_entity(self, user_id, entity_name, entity_data):
        """Save or update an entity for the user."""
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO user_entities (user_id, entity_name, entity_data, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id, entity_name) DO UPDATE SET
                entity_data = EXCLUDED.entity_data,
                updated_at = EXCLUDED.updated_at
        """, (user_id, entity_name, json.dumps(entity_data), datetime.utcnow()))
        conn.commit()
        cursor.close()
        conn.close()

    def load_entities(self, user_id):
        """Load all entities for a specific user."""
        conn = psycopg2.connect(**self.conn_params)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT entity_name, entity_data 
            FROM user_entities
            WHERE user_id = %s
        """, (user_id,))
        results = {name: data for (name, data) in cursor.fetchall()}
        conn.close()
        return results
