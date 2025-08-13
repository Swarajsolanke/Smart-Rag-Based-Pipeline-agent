# src/graph/flow.py
from __future__ import annotations
from typing import TypedDict, Literal, Optional, List, Dict, Any

from langgraph.graph import StateGraph, START, END
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig

from src.utils.llm import get_gemini_chat
from src.agents.wheather_agent import fetch_weather_by_city
from src.pipelines.embedding_pipeline import ensure_embeddings_upsert
from src.pipelines.retervial import retrieve_top_k
from src.utils.pdf_loader import load_pdf_text_chunks
from src.utils.evaluation import evaluate_response

# ---------- STATE ----------
class AppState(TypedDict, total=False):
    question: str              # user question
    pdf_path: Optional[str]    # path to uploaded pdf (for RAG)
    mode: Optional[Literal["weather", "rag"]]
    location: Optional[str]    # extracted location (for weather)
    weather: Optional[Dict[str, Any]]
    rag_hits: Optional[List[Dict[str, Any]]]
    answer: Optional[str]
    sources: Optional[List[Dict[str, Any]]]
    error: Optional[str]

# ---------- NODE: classify weather vs rag ----------
def classify_node(state: AppState, config: RunnableConfig) -> AppState:
    llm = get_gemini_chat(temperature=0.0)
    prompt = ChatPromptTemplate.from_messages([
        ("system",
         "You route questions. Respond with exactly one word: 'weather' if the user asks about weather/temperature/forecast; otherwise 'rag'."),
        ("human", "{q}")
    ])
    chain = prompt | llm
    out = chain.invoke({"q": state["question"]}, config=config)
    label = out.content.strip().lower()
    mode: Literal["weather", "rag"] = "weather" if "weather" in label else "rag"

    # simple location heuristic if weather
    loc = None
    if mode == "weather":
        import re
        q = state["question"]
        m = re.search(r"\bin\s+([a-zA-Z\s]+)", q, flags=re.IGNORECASE)
        if m:
            loc = m.group(1).strip().title()
        else:
            # fallback: last token(s)
            parts = q.strip().split()
            if parts:
                loc = parts[-1].title()

    new_state: AppState = {"mode": mode, "location": loc}
    return new_state

# ---------- NODE: weather ----------
def weather_node(state: AppState, config: RunnableConfig) -> AppState:
    loc = (state.get("location") or "").strip()
    if not loc:
        return {"error": "No location found in the question. Please specify a city/state."}
    try:
        w = fetch_weather_by_city(loc)
        # Optionally format with LLM (LangChain) for nicer answer
        llm = get_gemini_chat(temperature=0.2)
        prompt = ChatPromptTemplate.from_template(
            "Summarize the following weather info for the user in one sentence.\n{w}"
        )
        chain = prompt | llm
        formatted = chain.invoke({"w": w}, config=config).content
        return {"weather": w, "answer": formatted}
    except Exception as e:
        return {"error": f"Weather fetch failed: {e}"}

# ---------- NODE: rag ----------
def rag_node(state: AppState, config: RunnableConfig) -> AppState:
    pdf_path = state.get("pdf_path")
    if not pdf_path:
        return {"error": "Please upload a PDF to use RAG."}
    try:
        # 1) load & embed
        chunks = load_pdf_text_chunks(pdf_path)
        ensure_embeddings_upsert(chunks)
        # 2) retrieve
        hits = retrieve_top_k(state["question"], top_k=4)
        context = "\n\n---\n\n".join([h["payload"].get("text", "") for h in hits])

        # 3) answer with LangChain Gemini
        llm = get_gemini_chat(temperature=0.2)
        prompt = ChatPromptTemplate.from_template(
            "Use the context to answer the question concisely.\n\nCONTEXT:\n{context}\n\nQUESTION: {question}"
        )
        chain = prompt | llm
        resp = chain.invoke({"context": context, "question": state["question"]}, config=config)
        text = resp.content

        # 4) evaluate (LangSmith-ready metrics placeholder)
        eval_metrics = evaluate_response(state["question"], text, hits)

        return {"rag_hits": hits, "answer": text, "sources": hits}
    except Exception as e:
        return {"error": f"RAG failed: {e}"}

# ---------- CONDITIONAL EDGE ----------
def route(state: AppState) -> Literal["to_weather", "to_rag"]:
    return "to_weather" if state.get("mode") == "weather" else "to_rag"

# ---------- BUILD GRAPH ----------
def build_graph():
    graph = StateGraph(AppState)
    graph.add_node("classify", classify_node)
    graph.add_node("weather", weather_node)
    graph.add_node("rag", rag_node)

    graph.add_edge(START, "classify")
    graph.add_conditional_edges("classify", route, {"to_weather": "weather", "to_rag": "rag"})
    graph.add_edge("weather", END)
    graph.add_edge("rag", END)

    return graph.compile()
