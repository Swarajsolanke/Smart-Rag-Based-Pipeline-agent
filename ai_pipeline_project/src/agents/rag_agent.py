# src/agents/rag_agent.py
"""
RAG pipeline:
 - load chunks from PDF (pdf_loader)
 - ensure embeddings in Qdrant (embedding_pipeline)
 - retrieve top-k docs (qdrant_helper)
 - call Gemini to answer using context + user question
"""

from src.utils.pdf_loader import load_pdf_text_chunks
from src.pipelines.embedding_pipeline import ensure_embeddings_upsert
from src.pipelines.retervial import retrieve_top_k  # fixed typo
from src.utils.evaluation import evaluate_response
from config.settings import GEMINI_MODEL, GEMINI_API_KEY

import google.generativeai as genai

# configure Gemini
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


def answer_from_docs(pdf_path: str, question: str, top_k: int = 4) -> dict:
    """
    Returns dict with:
      - 'answer': LLM text
      - 'sources': list of retrieved passages
      - 'raw': raw LLM response
      - 'eval': evaluation metrics
    """
    # 1) Load chunks from PDF
    chunks = load_pdf_text_chunks(pdf_path)

    # 2) Store embeddings in Qdrant
    ensure_embeddings_upsert(chunks)

    # 3) Retrieve relevant docs
    hits = retrieve_top_k(question, top_k=top_k)

    # 4) Build context for prompt
    context_text = "\n\n---\n\n".join(
        [h["payload"].get("text", "") for h in hits]
    )

    prompt = f"""Use the following extracted document snippets to answer the question.

CONTEXT:
{context_text}

QUESTION: {question}

Provide a concise, referenced answer and mention which snippet (by index) you used if relevant."""

    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY not set in environment for LLM calls.")

    # ✅ Updated Gemini call
    model = genai.GenerativeModel(GEMINI_MODEL)
    response = model.generate_content(prompt)

    # Extract generated text
    text = getattr(response, "text", str(response))

    # 5) Evaluate answer
    eval_metrics = evaluate_response(question, text, hits)

    return {
        "answer": text,
        "sources": hits,
        "raw": response,
        "eval": eval_metrics
    }
