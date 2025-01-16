import streamlit as st
import requests
import time
import json

def read_questions_from_text(input_text):
    """
    Reads a text block where each question starts with '##',
    followed by one or more lines of options.
    Removes surrounding '**' from lines to avoid bold markers in Telegram.
    Returns a list of dicts: [{'question': str, 'options': [str, ...]}, ...]
    """
    lines = [line.strip() for line in input_text.splitlines()]
    questions = []
    question = ""
    options = []

    for line in lines:
        # Skip completely blank lines
        if not line:
            continue
        
        if line.startswith("##"):
            # If we already have a question in progress, store it before starting a new one
            if question:
                questions.append({"question": question, "options": options})
            # Start a new question (strip off '##')
            question = line[2:].strip()
            options = []
        else:
            # Remove leading and trailing '**' if present
            if line.startswith("**") and line.endswith("**") and len(line) > 4:
                line = line[2:-2].strip()
            elif line.startswith("**"):  
                # if there's only a leading '**'
                line = line[2:].strip()
            elif line.endswith("**"):  
                # if there's only a trailing '**'
                line = line[:-2].strip()

            options.append(line)

    # If the very last line was a question, add it
    if question:
        questions.append({"question": question, "options": options})

    return questions


def send_questions_to_telegram(questions):
    """
    Sends each question as a quiz poll to the specified Telegram chat.
    """
    # Update with your Telegram bot token and chat ID
    base_url = "https://api.telegram.org/bot7491440082:AAHGhMSot01aN3VLH9zn-G_0aPsRd3BMJZk/sendPoll"
    chat_id = "-4674739167"

    delay_between_requests = 2  # seconds between each poll

    for q in questions:
        # Basic validations
        if not q['question']:
            st.error(f"Question text is empty. Skipping this question.")
            continue

        if len(q['question']) > 300:
            st.error(f"Question is too long (>300 chars): {q['question']}")
            continue

        if len(q['options']) < 2:
            st.error(f"Question '{q['question']}' must have at least 2 options. Skipping.")
            continue

        # correct_option_id must be valid (0 is valid only if there's at least 1 option)
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
            st.write(response_data)  # Log the response for debugging

            if not response_data.get("ok"):
                st.error(f"Failed to send question: '{q['question']}'. "
                         f"Error: {response_data.get('description')}")
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")

        # Delay before sending the next question
        time.sleep(delay_between_requests)


def process_questions(input_text):
    """
    Parses questions from text input and sends them to Telegram.
    """
    questions = read_questions_from_text(input_text)
    send_questions_to_telegram(questions)


# Streamlit UI
st.title("Send Quiz Questions to Telegram")
st.write("Paste your questions below. Use '##' to start each question, followed by at least 2 options.\n"
         "If you have used '**' for bold, they will be stripped from the final poll options.")

input_text = st.text_area("Paste Questions Here", height=300)

if st.button("Send to Telegram"):
    if input_text.strip():
        process_questions(input_text)
    else:
        st.error("Please paste some questions before sending.")
