# src/agents/decision_agent.py
"""
Simple decision logic that picks between weather or RAG based on user input.
This can be replaced with a LangGraph node later.
"""

from typing import Dict

def decide_action(user_message: str) -> Dict[str, str]:
    """
    Very simple keyword-based decision. Returns dict:
      {"action": "weather"|"rag", "intent": short_intent_str}
    """
    text = user_message.lower().strip()

    # Weather keywords
    weather_keywords = ["weather", "temperature", "forecast", "rain", "sunny", "wind"]
    if any(k in text for k in weather_keywords):
        return {"action": "weather", "intent": "get_weather"}

    # If user asks about the PDF (document, assignment, file, pdf)
    doc_keys = ["pdf", "document", "assignment", "file", "read", "paper"]
    if any(k in text for k in doc_keys) or text.endswith("?"):
        # assume question to RAG unless explicit weather mention
        return {"action": "rag", "intent": "query_document"}

    # Default to RAG
    return {"action": "rag", "intent": "query_document"}
