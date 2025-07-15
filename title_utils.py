"""
title_utils.py

This module provides utility functions to generate concise, meaningful titles
for chatbot sessions based on the most recent technical user query.

Key Features:
- Filters out greetings and small talk from chat history.
- Uses an LLM (Qwen3) to generate short, context-aware titles.
- Ensures the title reflects the core technical question.

Dependencies:
- LangChain
- LangChain OpenAI
- Regular expressions
- Environment variables (.env)
"""
from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os 
import re

load_dotenv()

title_llm = ChatOpenAI(
        model="qwen3",
        base_url=os.environ["BASE_URL"],
        api_key="not-needed",  #  required even if unused
        default_headers={"Authorization": os.environ["LLAMA_AUTHORIZATION"]},

        temperature=0.3,
        top_p=0.6,
        max_tokens=7,
        streaming=False
    )
#chatollama instance not properly created 

def get_last_technical_question(chat_history: list) -> str:

    """
    Extracts the last meaningful (non-greeting) technical question from chat history.

    Args:
        chat_history (list): A list of dictionaries, each containing a 'question' field.

    Returns:
        str: The last technical question found, or an empty string if none exists.
    """
    for turn in reversed(chat_history):
        question = turn.get("question", "").strip()
        q_lower = question.lower()
        if re.search(r"\b(hi|hello|hey|good morning|good evening|how are you|my name is|i am|this is)\b", q_lower):
            continue
        return question
    return ""

def generate_title(chat_history: list) -> str:
    """
    Generates a concise title summarizing the user's last technical question in the chat.
    The title excludes any greetings or casual conversation and is designed to be
    a maximum of 5 words.

    Args:
        chat_history (list): A list of chat turns, each with 'question' and 'answer' fields.

    Returns:
        str: A short descriptive title, or "New Chat" if no technical question is found.

    """
    if not chat_history:
        return "New Chat"

    technical_question = get_last_technical_question(chat_history)

    print("TECHNICAL QUESTION:", repr(technical_question))  # debug

    if not technical_question:
        return "New Chat"

    prompt = f"""
/no_think
Create a short, clear title (max 5 words) that summarizes the user's **technical question** below.
Ignore greetings, names, and small talk.

Question:
{technical_question}

Title:
""".strip()

    print("FINAL PROMPT:\n", prompt)  

    try:
        response = title_llm.invoke([HumanMessage(content=prompt)])


        print("RAW RESPONSE:", repr(response.content)) 

        clean_title = re.sub(r"<think>\s*.*?\s*</think>", "", response.content, flags=re.DOTALL).strip().strip('"')

        return clean_title or "New Chat"

    except Exception as e:
        print("[Title Generation Error]", e)
        return "New Chat"


test_chat = [
    {"question": "Hello", "answer": "Hi! How can I help you today?"},
    {"question": "What is Full Band Capture?", "answer": "FBC is a DOCSIS feature..."}
]

generate_title(test_chat)
