import requests
import streamlit as st

def action_ai_response(question):
    auth = 'your_token_here'  # Replace with actual token
    headers = {
        'Authorization': f'Bearer {auth}',
        'Content-Type': 'application/json'
    }
    data = {"input": question}

    try:
        response = requests.post('http://127.0.0.1:3012/aihelpdesk/get_response', headers=headers, json=data)

        if response.status_code != 200:
            return f"Request failed with status code {response.status_code}"

        json_data = response.json()
        output_items = json_data.get("data", {}).get("output", [])

        if not output_items:
            return "No output received from model."

        # Try to get the first message
        for item in output_items:
            if "message" in item:
                return item["message"]

        # If no message, try to get the first link
        for item in output_items:
            if "link" in item:
                return item["link"]

        return "No message or link found in output."

    except requests.exceptions.RequestException as e:
        return f"Request failed: {str(e)}"
    except ValueError:
        return "Failed to parse response JSON."
    except Exception as e:
        return f"Unexpected error: {str(e)}"






# def get_api_response(question, session_id, model):                                              10/07/25 works fine uncomment to use
#     print(question)
#     print(session_id)
#     print(model)
#     headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
#     data = {"question": question, "model": model}
#     print(data) 

#     if session_id:
#         data["session_id"] = session_id

#     try:
#         print("Sending request to API...")
#         response = requests.post("http://127.0.0.1:8000/chat", headers=headers, json=data)                      # debug url, headers, data
#         print(response.status_code)
#         if response.status_code == 200:
#             return response.json()
#         else:
#             st.error(f"❌ API request failed [{response.status_code}]: {response.text}")
#             return None
#     except Exception as e:
#         st.error(f"❌ Exception during API call: {str(e)}")
#         return None




def get_api_response(question, session_id, model):
    print("Question:", question)
    print("Session ID:", session_id)
    print("Selected Model:", model)

    # Only allow qwen3 for now                                                                          Added this whole function
    supported_models = ["qwen3"]
    if model not in supported_models:
        print(f"Model '{model}' not supported. Falling back to 'qwen3'.")
        model = "qwen3"

    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json'
    }

    data = {
        "question": question,
        "model": model
    }

    if session_id:
        data["session_id"] = session_id

    try:
        print("Sending request to API...")
        print("Payload:", data)
        response = requests.post("http://127.0.0.1:8000/chat", headers=headers, json=data)

        print("Status Code:", response.status_code)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"❌ API request failed [{response.status_code}]: {response.text}")
            return None
    except Exception as e:
        st.error(f"❌ Exception during API call: {str(e)}")
        return None
