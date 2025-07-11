import streamlit as st
import re
from uuid import uuid4

from api_utils import get_api_response, action_ai_response
from db_utils import get_chat_history, insert_application_logs


def display_chat_interface():                                                                      
    
    if st.session_state.session_id and not st.session_state.messages:
        st.session_state.messages = get_chat_history(st.session_state.session_id)

 
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

  
    if prompt := st.chat_input("Query:"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        print("Line pre-spinner executed")

        with st.spinner("Generating response..."):

            print("Line 27 executed")
            if not st.session_state.session_id:
                st.session_state.session_id = str(uuid4())

            print("Line 31 executed")
            if re.match(r"^.{0,2}/", prompt):
                response_text = action_ai_response(prompt)
                if response_text:
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
                    with st.chat_message("assistant"):
                        st.markdown(response_text)

                    insert_application_logs(
                        session_id=st.session_state.session_id,
                        user_query=prompt,
                        gpt_response=response_text,
                        model="helpdesk"
                    )
                else:
                    st.error("❌ Failed to get a response from Helpdesk API.")

            else:
                # Otherwise, use LangChain-style API
                print("Line query executed")
                response = get_api_response(prompt, st.session_state.session_id, st.session_state.model)
                print(response)
                print("Line query response executed")
                if response:
                    st.session_state.session_id = response.get("session_id")
                    answer = response["answer"]

                    st.session_state.messages.append({"role": "assistant", "content": answer})
                    with st.chat_message("assistant"):
                        st.markdown(answer)

                    with st.expander("Details"):
                        st.subheader("Generated Answer")
                        st.code(answer)
                        st.subheader("Model Used")
                        st.code(response["model"])
                        st.subheader("Session ID")
                        st.code(response["session_id"])

                    
                    # insert_application_logs(
                    #     session_id=st.session_state.session_id,
                    #     user_query=prompt,
                    #     gpt_response=answer,
                    #     model=response["model"]
                    # )

                else:
                    st.error(" Failed to get a response from the backend API.")
