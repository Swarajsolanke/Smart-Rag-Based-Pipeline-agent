# import os
# import sys
# import re
# import tempfile
# import streamlit as st

# # Add project root to sys.path
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.agents.decision_agent import decide_action
from src.agents.wheather_agent import fetch_weather_by_city
from src.agents.rag_agent import answer_from_docs


# def extract_location_from_text(text: str) -> str:
#     """
#     Extract location (city/state) from a sentence like
#     'what is weather in Aurangabad'.
#     """
#     # Try 'in <location>'
#     match = re.search(r"\bin\s+([a-zA-Z\s]+)", text.lower())
#     if match:
#         return match.group(1).strip().title()
#     # Else, use last word(s) as fallback
#     words = text.strip().split()
#     return words[-1].title()


# st.set_page_config(page_title="AI Pipeline Demo", layout="centered")

# st.title("RAG  Based AI Pipeline — Weather + PDF ")

# # Sidebar: PDF uploader
# st.sidebar.header("Settings")
# uploaded_pdf = st.sidebar.file_uploader(
#     "Upload a PDF for RAG",
#     type=["pdf"],
#     accept_multiple_files=False
# )

# # Save uploaded PDF to a temp location
# pdf_path = None
# if uploaded_pdf:
#     temp_dir = tempfile.gettempdir()
#     pdf_path = os.path.join(temp_dir, uploaded_pdf.name)
#     with open(pdf_path, "wb") as f:
#         f.write(uploaded_pdf.read())

# # Conversation history
# if "history" not in st.session_state:
#     st.session_state.history = []

# # User input
# user_input = st.text_input(
#     "Ask a question (e.g. 'What's the weather in Maharashtra?' or 'Explain section 2 of the document')"
# )

# if st.button("Send") and user_input.strip():
#     d = decide_action(user_input)

#     if d["action"] == "weather":
#         location = extract_location_from_text(user_input)
#         try:
#             weather = fetch_weather_by_city(location)
#             reply = (
#                 f"Weather in {weather['city']}: {weather['description']}. "
#                 f"Temp: {weather['temp']}°C (feels like {weather['feels_like']}°C). "
#                 f"Humidity: {weather['humidity']}%."
#             )
#         except Exception as e:
#             reply = f"Failed to fetch weather for '{location}': {e}"

#     else:
#         # RAG flow
#         if not pdf_path:
#             reply = "Please upload a PDF in the sidebar to use RAG."
#         else:
#             try:
#                 rag_resp = answer_from_docs(pdf_path, user_input)
#                 reply = rag_resp["answer"]
#             except Exception as e:
#                 reply = f"RAG pipeline failed: {e}"

#     # Save conversation
#     st.session_state.history.append(("user", user_input))
#     st.session_state.history.append(("assistant", reply))

# # Display conversation
# for role, text in st.session_state.history:
#     if role == "user":
#         st.markdown(f"**You:** {text}")
#     else:
#         st.markdown(f"**Assistant:** {text}")



# src/app.py
import os
import sys
import re
import tempfile
import streamlit as st

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.graph.flow import build_graph

st.set_page_config(page_title="AI Pipeline Demo — LangGraph + LangChain", layout="centered")
st.title("RAG Based Smart Agent")

# Sidebar: PDF upload (for RAG)
st.sidebar.header("RAG Document")
uploaded_pdf = st.sidebar.file_uploader(
    "Upload a PDF for RAG",
    type=["pdf"],
    accept_multiple_files=False
)

pdf_path = None
if uploaded_pdf:
    tmp_dir = tempfile.gettempdir()
    pdf_path = os.path.join(tmp_dir, uploaded_pdf.name)
    with open(pdf_path, "wb") as f:
        f.write(uploaded_pdf.read())

# Conversation history
if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Ask something (weather or about the uploaded PDF)")

if st.button("Send") and user_input.strip():
    graph = build_graph()

    # feed graph state
    state = {
        "question": user_input,
        "pdf_path": pdf_path,  # None if not uploaded
    }

    # If LangSmith is enabled, you can pass run metadata tags:
    config = {"configurable": {"thread_id": "ui-session"}, "tags": ["ui", "streamlit"]}

    result = graph.invoke(state, config=config)
    reply = result.get("answer") or result.get("error") or "No answer produced."

    st.session_state.history.append(("user", user_input))
    st.session_state.history.append(("assistant", reply))

# Display conversation
for role, text in st.session_state.history:
    if role == "user":
        st.markdown(f"**You:** {text}")
    else:
        st.markdown(f"**Assistant:** {text}")
