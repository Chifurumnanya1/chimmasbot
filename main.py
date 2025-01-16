import streamlit as st
import requests
import time
import json

def read_questions_from_text(input_text):
    questions = []
    # Split input text into lines and strip leading spaces from each line
    lines = [line.lstrip() for line in input_text.splitlines()]
    question = ''
    options = []
    for line in lines:
        if line.startswith('##'):
            if question:
                questions.append({'question': question, 'options': options})
                question = ''
                options = []
            question = line[2:].strip()
        elif line.startswith(''):
            options.append(line[2:].strip())
    if question:  # Check if there is a question at the end without a following ##
        questions.append({'question': question, 'options': options})
    return questions

def send_questions_to_telegram(questions):
    base_url = "https://api.telegram.org/bot7491440082:AAHGhMSot01aN3VLH9zn-G_0aPsRd3BMJZk/sendPoll"  # Update with your Telegram bot token
    chat_id = "-4674739167"  # Update with your chat ID
    delay_between_requests = 5  # seconds
    for q in questions:
        parameters = {
            "chat_id": chat_id,
            "question": q['question'],
            "options": json.dumps(q['options']),
            "type": "quiz",
            "correct_option_id": 0
        }
        try:
            response = requests.post(base_url, data=parameters)
            response_data = response.json()
            st.write(response_data)  # Log the response data for debugging

            if not response_data.get("ok"):
                st.error(f"Failed to send question: {q['question']}. Error: {response_data.get('description')}")
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")

        # Delay before sending the next question
        time.sleep(delay_between_requests)

def process_questions(input_text):
    questions = read_questions_from_text(input_text)
    send_questions_to_telegram(questions)

st.title("Send Quiz Questions to Telegram")
st.write("Paste your questions below. Format questions with '##' for questions and '' for options.")

# Add a text area for user input
input_text = st.text_area("Paste Questions Here", height=300)

if st.button("Send to Telegram"):
    if input_text.strip():  # Check if the text area is not empty
        process_questions(input_text)
    else:
        st.error("Please paste some questions before clicking the button.")
