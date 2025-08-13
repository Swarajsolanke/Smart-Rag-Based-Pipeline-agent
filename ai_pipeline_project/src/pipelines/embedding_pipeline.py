# src/pipelines/embedding_pipeline.py
"""
Create embeddings for text chunks and upsert to Qdrant.
This example uses sentence-transformers locally (stable & free).
"""

from sentence_transformers import SentenceTransformer
from src.utils.qdrant_helper import upsert_documents, collection_exists, create_collection
from config.settings import EMBEDDING_MODEL, QDRANT_COLLECTION

_model = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)
    return _model

def chunks_to_embeddings(docs: list):
    """
    docs = list of {"id": str, "text": str, "meta": {...}}
    returns list of {"id": id, "vector": [...], "payload": {...}}
    """
    model = _get_model()
    texts = [d["text"] for d in docs]
    vectors = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
    results = []
    for d, vec in zip(docs, vectors):
        results.append({"id": d["id"], "vector": vec.tolist(), "payload": {"text": d["text"], **(d.get("meta") or {})}})
    return results

def ensure_embeddings_upsert(chunks: list):
    """
    chunks: list of strings OR list of dicts {"id","text"}.
    This will create collection if not exists and upsert vectors.
    """
    # normalize
    docs = []
    for i, c in enumerate(chunks):
        if isinstance(c, str):
            docs.append({"id": f"doc_{i}", "text": c})
        elif isinstance(c, dict):
            docs.append({"id": c.get("id", f"doc_{i}"), "text": c.get("text", ""), "meta": c.get("meta", {})})
        else:
            docs.append({"id": f"doc_{i}", "text": str(c)})

    # create collection if needed
    if not collection_exists(QDRANT_COLLECTION):
        create_collection(QDRANT_COLLECTION)

    # prepare vectors
    items = chunks_to_embeddings(docs)
    upsert_documents(QDRANT_COLLECTION, items)
