"""
main.py

This is the entry point for the FastAPI backend that powers a LangChain-based
chatbot for proactive network maintenance and DOCSIS-related queries.

Core Features:
- Receives user input via `/chat` endpoint
- Uses a RAG (Retrieval-Augmented Generation) pipeline with history-aware context
- Generates summarized metadata from chat history
- Stores all chat logs and summaries in PostgreSQL
- Dynamically generates conversation titles based on technical queries
- Saves titles in both PostgreSQL and Redis for UI/UX improvements

Dependencies:
- FastAPI
- LangChain
- Redis
- PostgreSQL
- Pydantic
"""
from fastapi import FastAPI
from pydantic_models import QueryInput, QueryResponse
from langchain_utils import get_rag_chain
from db_utils import (
    insert_application_logs,
    get_chat_history,
    save_conversation_title,
    get_conversation_title  
)
from redis_utils import save_thread
from title_utils import generate_title
from title_utils import get_last_technical_question
from langchain_utils import get_last_n_turns, get_summarization_chain

import uuid
import logging
from dotenv import load_dotenv
import re
import time

load_dotenv()
logging.basicConfig(filename='app.log', level=logging.INFO)

app = FastAPI()

@app.post("/chat", response_model=QueryResponse)
def chat(query_input: QueryInput):
    """
    Chat endpoint that receives a user query, retrieves context,
    runs a RAG chain for response generation, and stores results.

    Args:
        query_input (QueryInput): Pydantic model containing question, session_id, and model.

    Returns:
        QueryResponse: Pydantic model with generated answer, session_id, and model.
    """

    print(" /chat endpoint hit")

    session_id = query_input.session_id or str(uuid.uuid4())
    logging.info(f"[CHAT] Session ID: {session_id}, User Query: {query_input.question}, Model: {query_input.model.value}")

    chat_history = get_chat_history(session_id)
    rag_chain,llm = get_rag_chain(model=query_input.model.value)            

    result = rag_chain.invoke({
        "input": query_input.question,
        "chat_history": chat_history
    })

    answer = result['answer']
    answer = re.sub(r"<think>.*?</think>", "", answer, flags=re.DOTALL).strip().strip('"')

    #clean_summary = sliding_summary.content.strip().replace("<think>", "").replace("</think>", "").strip()


#     current_turn = {
#     "user_query": query_input.question,
#     "bot_response": answer
# }
#     updated_history = chat_history + [current_turn]

    last_five_turns = get_last_n_turns(chat_history, n=10)
    
    # print("Turns for summary input:\n", get_last_n_turns(updated_history, n=5))

    summary_chain = get_summarization_chain(llm)

    sliding_summary = summary_chain.invoke({"chat_history": last_five_turns})
    clean_summary = sliding_summary.replace("<think>", "").replace("</think>", "").strip()

    metadata = {
        "sliding_summary": clean_summary,

    }

    insert_application_logs(session_id, query_input.question, answer, query_input.model.value,metadata=metadata)
    logging.info(f"[CHAT] AI Response: {answer}")


    existing_title = get_conversation_title(session_id)

    if not existing_title or existing_title.strip().lower() in ["untitled chat", "new chat"]:
        try:
            updated_history = chat_history + [{"question": query_input.question, "answer": answer}]
            technical_question = get_last_technical_question(updated_history)

            if technical_question:  
                title = generate_title(updated_history)

                if title.strip().lower() not in ["untitled chat", "new chat"]:
                    save_conversation_title(session_id, title)
                    save_thread(session_id, title, time.time())
                    logging.info(f"[CHAT] Title generated and saved: {title}")
                else:
                    logging.warning(f"[CHAT] Title was fallback ('{title}'), skipping DB/Redis save for session {session_id}")
            else:
                logging.info(f"[CHAT] Skipping title generation for session {session_id} — no valid technical question yet.")

        except Exception as e:
            fallback_title = "New Chat"
            logging.warning(f"[CHAT] Title generation failed. Using fallback: {fallback_title}. Error: {e}")
            save_conversation_title(session_id, fallback_title)


    return QueryResponse(answer=answer, session_id=session_id, model=query_input.model)
