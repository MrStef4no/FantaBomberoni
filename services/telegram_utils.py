import requests
import streamlit as st

def send_telegram_message(message):

    try:
        bot_token = st.secrets["BOT_TOKEN"]
        chat_id = st.secrets["CHAT_ID"]

        url = f"https://api.telegram.org/bot8672495625:AAGM9HdS97OawKpBo_nOCmvYz6Yr4UNxQgY/sendMessage"

        payload = {
            "chat_id": chat_id,
            "text": message
        }

        requests.post(url, json=payload)

    except Exception as e:
        print(f"Telegram error: {e}")