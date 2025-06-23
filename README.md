# AI Health Chatbot

A smart medical assistant that remembers your conversations and provides accurate health information from reliable sources.

## What This Does

This chatbot helps you with health questions by:
- Remembering your past conversations
- Searching through medical documents to find relevant information
- Giving you personalized answers based on your history
- Keeping track of important details about your health

## How It Works

The chatbot follows a simple but smart process when you ask a question:

### Step 1: Gather Your History
First, it looks up your conversation history:
- Recent messages from your current chat session
- Long-term summaries of your past conversations
- Important details it has learned about you (like your medical conditions, preferences, etc.)

### Step 2: Decide What to Do
The chatbot then decides whether to:
- Answer directly using what it already knows about you
- Search through medical documents to find specific information

### Step 3: Find Information (if needed)
If it needs to search for information, it:
- Looks through a database of health documents
- Finds the most relevant information for your question
- Combines this with your personal history

### Step 4: Give You an Answer
Finally, it creates a personalized answer that:
- Uses the information it found
- References your past conversations
- Speaks naturally and clearly

### Step 5: Remember Everything
After answering, it saves your question and its response so it can remember this conversation for the future.

## What Makes This Special

**Memory System**: Unlike most chatbots that forget everything after each conversation, this one remembers:
- Your recent messages (stored in Redis for fast access)
- Long-term summaries of your conversations (stored in PostgreSQL)
- Important details about you (like your medical history, preferences, etc.)

**Smart Planning**: The chatbot doesn't just search for everything. It's smart enough to:
- Answer general questions directly without searching
- Only search medical documents when you ask health-related questions
- Use your personal history to give better answers

**Document Search**: When you ask health questions, it searches through:
- Medical guidelines and documents
- Health statistics and research
- Best practices and recommendations

## Technical Architecture

The system is built with several components that work together:

**Main Application** (`app.py`): The brain that coordinates everything

**Context Builder** (`context_builder.py`): Gathers your conversation history and personal information

**Planner** (`planner.py`): Decides whether to answer directly or search for information

**Retrieval System** (`retrieval.py`): Searches through medical documents to find relevant information

**Answer Generator** (`answer.py`): Creates the final response using either GPT-4 or a custom-trained model

**Memory Management**:
- `short_term.py`: Handles recent conversations (stored in Redis)
- `memory.py`: Manages long-term memory and user data (stored in PostgreSQL)

**Web Interface** (`app_gradio.py`): Provides a user-friendly chat interface

## Setup Requirements

To run this chatbot, you'll need:

**Databases**:
- PostgreSQL (for long-term memory and user data)
- Redis (for recent conversation storage)
- ChromaDB (for searching through medical documents)

**API Keys**:
- OpenAI API key (for the main language model)

**Python Dependencies**: All listed in `requirements.txt`

## How to Use

1. Set up your databases and environment variables
2. Run the database setup script to create tables
3. Start the web interface
4. Create a user account
5. Start chatting!

The chatbot will remember your conversations and get better at helping you over time as it learns more about your health needs and preferences.

## Key Features

- **Personalized Responses**: Uses your conversation history to give better answers
- **Medical Document Search**: Finds relevant health information from reliable sources
- **Memory Across Sessions**: Remembers important details about you
- **Smart Decision Making**: Knows when to search and when to answer directly
- **User-Friendly Interface**: Easy-to-use web chat interface

This chatbot is designed to be a helpful medical assistant that gets to know you and provides accurate, personalized health information. 