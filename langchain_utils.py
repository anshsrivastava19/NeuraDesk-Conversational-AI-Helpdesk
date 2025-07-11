from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate,MessagesPlaceholder
from langchain.chains import create_retrieval_chain,create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from typing import List
from langchain_core.documents import Document
import os 
from chroma_utils import vectorstore
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

retriever=vectorstore.as_retriever(search_kwargs={'k':5})
output_parser=StrOutputParser()

contextualize_q_system_prompt = (
    "You are given the last 3 turns of a conversation, including user messages and assistant responses, "
    "along with the most recent user message. This latest message may reference earlier context. "
    "Your task is to reformulate the latest user message into a clear, standalone question that is "
    "fully self-contained and understandable without prior context. Only rewrite it if necessary to preserve clarity and intent. "
    "If the original message already makes sense on its own, return it unchanged. "
    "If the latest message is a simple greeting (e.g., 'hi', 'hello', 'good morning') or contains no meaningful intent "
    "(e.g., small talk, acknowledgments like 'thanks', or empty filler), return it exactly as is without reformulation. "
    "Do not attempt to answer the question or modify greetings. Your output should only be a rewritten query if needed, "
    "otherwise return the original message."
)

system_prompt = """You are the Openvault Proactive Network Maintenance Assistant, an intelligent chatbot designed to support network administrators and IT professionals. Your primary role is to provide clear and actionable advice on Data Over Cable Service(DOCSIS), proactive network monitoring, troubleshooting and maintenance.You are a helpful assistant. 
Do NOT include <think>...</think> or any inner monologue or commentary.
Respond only with the final user-facing answer.

Key Guidelines:
1. Provide concise and straightforward answers without unnecessary elaboration.  
2. Emphasize early detection of network issues, routine maintenance practices, and optimization techniques.  
3. Offer step-by-step instructions for diagnosing and resolving network problems.  
4. If the user's input is ambiguous, ask clarifying questions. Recommend consulting a network specialist for complex or critical issues.  
5. Always promote best practices in network security and proactive maintenance. Remind users to verify critical actions with appropriate internal protocols.  
6. Maintain a friendly, supportive, and professional tone.

Context:
- Openvault is a proactive network maintenance application that monitors network health, alerts users to potential issues, and recommends preemptive actions to avoid network failures.  
- The intended audience includes network administrators, IT operations teams, and technical support staff.

Special Handling:
- If the user greets you with phrases like "hi", "hello", or "good morning", respond with a friendly greeting and offer help related to network maintenance.
- If the query is clearly outside the cable network domain (e.g., unrelated topics like cooking, banking, etc.), strictly respond with the following message **without any additional text**:  
"I am sorry, I am a friendly and knowledgeable networking assistant made by Nimblethis. I cannot answer queries outside the cable network domain."

Retrieved Context:
{context}


Your task is to assist with network maintenance queries, provide actionable insights, and help users implement preventive measures to keep their networks running smoothly. Responses should be direct, avoiding redundant introductory phrases.
"""

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])


def get_last_n_turns(chat_history: list[dict], n: int = 5) -> str:
    """
    Returns the last `n` chat turns formatted as a string.
    Each turn is a dict with 'user_query' and 'gpt_response'.
    Falls back to empty string if keys are missing.
    """
    last_n = chat_history[-n:]

    # formatted = []

    # for i, turn in enumerate(last_n):
    #     user = turn.get("user_query", f"[Missing user_query in turn {i}]")
    #     assistant = turn.get("gpt_response", f"[Missing gpt_response in turn {i}]")
    #     formatted.append(f"User: {user}\nAssistant: {assistant}")
    # print("\n".join(formatted))
    # return "\n".join(formatted)
    return last_n
    

summary_prompt = PromptTemplate.from_template("""
Summarize the following conversation in 1-2 clear, concise sentences. 
Focus only on the key points discussed. Do not include filler or thoughts.
                                              

{chat_history}
/no_think /nothink

                                              
""")

def get_summarization_chain(llm):
    return summary_prompt | llm | StrOutputParser()


def get_rag_chain(model: str):

    if model != "qwen3":
        llm = ChatOpenAI(
        model_name=model,
        openai_api_key="NA",
        )
    else:
        llm = ChatOpenAI(
        model="qwen3",
        base_url=os.environ["BASE_URL"],
        api_key="not-needed",
        default_headers={"Authorization": os.environ["LLAMA_AUTHORIZATION"]},

        temperature=0.2,     
        top_p=0.6,          
        max_tokens=256,    
        streaming=True  
    )

    history_aware_retriever=create_history_aware_retriever(llm,retriever,contextualize_q_prompt)        
    question_answer_chain=create_stuff_documents_chain(llm,qa_prompt)
    rag_chain=create_retrieval_chain(history_aware_retriever,question_answer_chain)
    return rag_chain, llm

