# src/app.py
import streamlit as st
from src.agents.decision_agent import decide_action
from src.agents.wheather_agent import fetch_weather_by_city
from src.agents.rag_agent import answer_from_docs
import os

st.set_page_config(page_title="AI Pipeline Demo", layout="centered")

st.title("AI Pipeline Demo — Weather + PDF RAG")

# sidebar
st.sidebar.header("Settings")
pdf_path = st.sidebar.text_input("Path to PDF (for RAG)", value="data/pdfs/Assignment - AI Engineer.pdf")
city_default = st.sidebar.text_input("Default city for weather", value="Mumbai")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Ask a question (e.g. 'What's the weather in Delhi?' or 'Explain section 2 of assignment')")

if st.button("Send") and user_input.strip():
    d = decide_action(user_input)
    if d["action"] == "weather":
        # crude city extraction: take last word as city (user should enter city)
        # better: use NER or ask user for city
        city = None
        # try to parse city from input
        parts = user_input.split("in")
        if len(parts) > 1:
            city = parts[-1].strip()
        if not city:
            city = city_default or "Mumbai"
        try:
            weather = fetch_weather_by_city(city)
            reply = f"Weather in {weather['city']}: {weather['description']}. Temp: {weather['temp']}°C (feels like {weather['feels_like']}°C). Humidity: {weather['humidity']}%."
        except Exception as e:
            reply = f"Failed to fetch weather: {e}"
    else:
        # RAG flow
        if not os.path.exists(pdf_path):
            reply = f"PDF not found at {pdf_path}. Put a PDF there or change path in sidebar."
        else:
            try:
                rag_resp = answer_from_docs(pdf_path, user_input)
                reply = rag_resp["answer"]
            except Exception as e:
                reply = f"RAG pipeline failed: {e}"

    st.session_state.history.append(("user", user_input))
    st.session_state.history.append(("assistant", reply))

# display conversation
for role, text in st.session_state.history:
    if role == "user":
        st.markdown(f"**You:** {text}")
    else:
        st.markdown(f"**Assistant:** {text}")
