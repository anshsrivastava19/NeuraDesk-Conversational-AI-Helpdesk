from langchain_community.chat_models import ChatOllama
from langchain.schema import HumanMessage
from langchain.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import os 
load_dotenv()
import re

title_llm = ChatOpenAI(
        model="qwen3",
        base_url=os.environ["BASE_URL"],
        api_key="not-needed",  #  required even if unused
        default_headers={"Authorization": os.environ["LLAMA_AUTHORIZATION"]},

        temperature=0.3,
        top_p=0.9,
        max_tokens=7,
        streaming=False
    )
#chatollama instance not properly created 

# def generate_title(chat_history: list) -> str:
#     """
#     Generate a short 4–5 word title for a chat using the first two exchanges.
#     """
#     if not chat_history:
#         return "New Chat"

#     # Limit to the first 2 exchanges for relevance
#     history_excerpt = "\n".join(
#         [f"User: {h['question']}\nAssistant: {h['answer']}" for h in chat_history[:2]]
#     )

#     prompt = f"""/no_think /no think Create a short, clear title (max 5 words) for this conversation:\n\n{history_excerpt}\n\nTitle:"""

#     try:
#         response = title_llm.invoke([HumanMessage(content=prompt)]).content
        
#         clean_title = re.sub(r"<think>\s*.*?\s*</think>", "", response, flags=re.DOTALL).strip().strip('"')

#         return clean_title
#     except Exception as e:
#         print("Title generation failed:", e)
#         return "New Chat"



# def get_last_technical_question(chat_history: list) -> str:
#     """
#     Returns the last user question that seems technical in nature.
#     Skips greetings and intros.
#     """
#     for turn in reversed(chat_history):
#         q = turn.get("question", "").strip().lower()
#         if re.search(r"\b(hi|hello|hey|good morning|my name is|i am|how are you|just checking)\b", q):
#             continue
#         return turn.get("question", "").strip()  # Return original casing
#     return ""



# def filter_small_talk(chat_history: list) -> list:
#     filtered = []
#     for turn in chat_history:
#         q = turn.get("question", "").lower()

#         if re.search(r"\b(hi|hello|hey|how are you|good morning|good evening)\b", q):
#             continue
#         if re.search(r"\b(my name is|i am|i’m|this is|just getting started|i’m new)\b", q):
#             continue

#         filtered.append(turn)

#     return filtered if filtered else chat_history



# def generate_title(chat_history: list) -> str:
#     """
#     Generate a 4–5 words title using an LLM that ignores greetings/small talk.
#     """

#     if not chat_history:
#         return "New Chat"

#     technical_question = get_last_technical_question(chat_history)

    
#     # Use first 2 full turns (even if they include greetings)
#     # excerpt = "\n".join([
#     #     f"User: {turn['question']}"                  #\nAssistant: {turn['answer']}
#     #     for turn in chat_history[:2]
#     # ])

#     # excerpt = "\n".join([
#     # f"User: {turn['question']}"
#     # for turn in filter_small_talk(chat_history)[:2]
#     # ])

#     prompt = f"""
# /no_think
# You are a helpful assistant summarizing technical conversations.

# Only generate a short, clear title (max 6 words) that describes the main **technical issue** or **question** asked by the user.

# I Ignore greetings, names, introductions, small talk, or general help requests.
# Only use what the **user actually asked** that is technical in nature.

# Question:
# {technical_question}

# Title:
# """.strip()

#     try:
#         response = title_llm.invoke([HumanMessage(content=prompt)]).content

#         # Clean title output
#         clean_title = re.sub(r"<think>\s*.*?\s*</think>", "", response, flags=re.DOTALL).strip().strip('"')

#         # if not clean_title or len(clean_title.split()) > 6:
#         #     return "Technical Query"

#         return clean_title

#     except Exception as e:
#         print("[Title Generation Error]", e)
#         return "New Chat"

def get_last_technical_question(chat_history: list) -> str:
    for turn in reversed(chat_history):
        question = turn.get("question", "").strip()
        q_lower = question.lower()
        if re.search(r"\b(hi|hello|hey|good morning|good evening|how are you|my name is|i am|this is)\b", q_lower):
            continue
        return question
    return ""

def generate_title(chat_history: list) -> str:
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
