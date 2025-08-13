# src/pipelines/retrieval_pipeline.py
"""
Retrieval utilities that talk to Qdrant and return hits
"""

from src.utils.qdrant_helper import search
from config.settings import QDRANT_COLLECTION

def retrieve_top_k(query: str, top_k: int = 4):
    """
    Currently uses the same sentence-transformer to embed the query via qdrant helper.
    Returns top_k hits list with structure matching qdrant response -> simplified.
    """
    hits = search(collection_name=QDRANT_COLLECTION, query_text=query, top_k=top_k)
    # standardize fields we expect
    simplified = []
    for h in hits:
        simplified.append({
            "id": h["id"],
            "score": h.get("score", None),
            "payload": h.get("payload", {}),
        })
    return simplified
