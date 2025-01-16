import streamlit as st
import requests
import time
import json

# Function to parse questions and options from input text
def read_questions_from_text(input_text):
    questions = []
    lines = [line.strip() for line in input_text.splitlines() if line.strip()]  # Remove empty lines
    question = ''
    options = []
    for line in lines:
        if line.startswith('##'):  # Detect new question
            if question:
                questions.append({'question': question, 'options': options})
                options = []
            question = line[2:].strip()
        else:  # Add options for the current question
            options.append(line.strip())
    if question:  # Append the last question
        questions.append({'question': question, 'options': options})
    return questions

# Function to validate questions before sending them
def validate_questions(questions):
    valid_questions = []
    for q in questions:
        if q['question'] and len(q['options']) >= 2 and all(q['options']):
            valid_questions.append(q)
        else:
            st.warning(f"Invalid question or options: {q}")
    return valid_questions

# Function to send questions to Telegram
def send_questions_to_telegram(questions):
    base_url = "https://api.telegram.org/bot<your-bot-token>/sendPoll"  # Replace with your Telegram bot token
    chat_id = "<your-chat-id>"  # Replace with your Telegram chat ID
    delay_between_requests = 5  # Delay in seconds between each request

    for q in questions:
        parameters = {
            "chat_id": chat_id,
            "question": q['question'],
            "options": json.dumps(q['options']),
            "type": "quiz",
            "correct_option_id": 0  # Modify this if you want to set a different correct option
        }
        try:
            response = requests.post(base_url, data=parameters)
            response_data = response.json()

            if response_data.get("ok"):
                st.success(f"Question sent: {q['question']}")
            else:
                st.error(f"Failed to send question: {q['question']}. Error: {response_data.get('description')}")
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")

        # Delay before sending the next question
        time.sleep(delay_between_requests)

# Main function to process input text and send questions
def process_questions(input_text):
    questions = read_questions_from_text(input_text)
    validated_questions = validate_questions(questions)
    if validated_questions:
        send_questions_to_telegram(validated_questions)
    else:
        st.error("No valid questions to send.")

# Streamlit UI
st.title("Send Quiz Questions to Telegram")
st.write("Paste your questions below. Format questions with '##' for questions and each option on a new line.")

# Text area for user input
input_text = st.text_area("Paste Questions Here", height=300)

# Button to trigger the question sending process
if st.button("Send to Telegram"):
    if input_text.strip():  # Ensure the input is not empty
        process_questions(input_text)
    else:
        st.error("Please paste some questions before clicking the button.")
