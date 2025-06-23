import gradio as gr
import os
import psycopg2
from dotenv import load_dotenv
from memory import MemoryStore
from short_term import ShortTermContext
from app import handle_query

# ==========================
# Init
# ==========================
load_dotenv()
memory_store = MemoryStore()
short_term = ShortTermContext()


# ==========================
# Helpers
# ==========================
def get_all_user_ids():
    """Return a list of user ids from the database."""
    conn = psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
        host=os.getenv("POSTGRES_HOST"),
        port=os.getenv("POSTGRES_PORT"),
    )
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM users;")
    ids = [row[0] for row in cursor.fetchall()]
    conn.close()
    return ids


def add_user(user_id, name, email):
    """Add a new user and return status + updated user list."""
    memory_store.create_user(user_id, name, email)
    status = f"✅ User {user_id} added."
    return status, {"choices": get_all_user_ids()}


def chat(user_id, session_id, user_message, history):
    """Send a message and get a reply."""
    reply = handle_query(user_id, session_id, user_message)
    history.append((user_message, reply))
    return history


# ==========================
# Build Gradio Demo
# ==========================
with gr.Blocks() as demo:
    gr.Markdown("## ⚕️ AI Health Chatbot Demo\nConnect, Chat, Maintain Context over Time!")

    # User Registration
    with gr.Row():
        user_id_in = gr.Textbox(label="User ID")
        user_name_in = gr.Textbox(label="Name")
        user_email_in = gr.Textbox(label="Email")
        add_user_btn = gr.Button(value="Add User")
        add_user_status = gr.Textbox(label="Add User Status", interactive=False)

    # User Selection & Session
    user_dropdown = gr.Dropdown(label="Select User", choices=get_all_user_ids(), interactive=True)
    session_id_in = gr.Textbox(value="default_session", label="Session ID")

    # Chat Area
    chat_box = gr.Chatbot()
    msg_box = gr.Textbox(label="Your Message")
    send_btn = gr.Button(value="Send")

    # ==========================
    # Actions
    # ==========================
    add_user_btn.click(
        add_user,
        inputs=[user_id_in, user_name_in, user_email_in],
        outputs=[add_user_status, user_dropdown]
    )
    send_btn.click(chat, [user_dropdown, session_id_in, msg_box, chat_box], chat_box)

demo.launch()
