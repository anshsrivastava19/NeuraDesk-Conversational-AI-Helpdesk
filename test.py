from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser

def get_last_n_turns(chat_history: list[dict], n: int = 5) -> str:
    """
    Returns the last `n` chat turns formatted as a string.
    Each turn is a dict with 'user_query' and 'gpt_response'.
    """
    last_n = chat_history[-n:]
    formatted = []

    for turn in last_n:
        user = turn.get("user_query", "")
        assistant = turn.get("gpt_response", "")
        formatted.append(f"User: {user}\nAssistant: {assistant}")
    
    return "\n".join(formatted)



summary_prompt = PromptTemplate.from_template("""
Summarize the following conversation between a user and an assistant.

Only include the key points and avoid repetition.
Keep the summary clear, concise, and under **250 words**.

Conversation:
{chat_history}
""")

def get_summarization_chain(llm):
    return summary_prompt | llm | StrOutputParser()




# last_5_turns_text = get_last_n_turns(chat_history, n=5)
# summary_chain = get_summarization_chain(llm)
# summary = summary_chain.invoke({"chat_history": last_5_turns_text})


# metadata = {
#     "summary_last_5_turns": summary,
#     "turn_number": len(chat_history),
#     "model": model_used
# }

# insert_application_logs(
#     session_id=session_id,
#     user_query=user_input,
#     gpt_response=llm_response,
#     model=model_used,
#     metadata=metadata
# )