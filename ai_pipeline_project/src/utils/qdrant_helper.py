# src/utils/qdrant_helper.py
from qdrant_client import QdrantClient
from qdrant_client.http import models as rest
from config.settings import QDRANT_URL, QDRANT_API_KEY, EMBEDDING_MODEL
import numpy as np
from sentence_transformers import SentenceTransformer

_client = None
_model = None

def _get_client():
    global _client
    if _client is None:
        url = QDRANT_URL
        api_key = QDRANT_API_KEY
        if api_key:
            _client = QdrantClient(url=url, api_key=api_key, prefer_grpc=False)
        else:
            _client = QdrantClient(url=url)
    return _client

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBEDDING_MODEL)  # Use same model everywhere
    return _model

def collection_exists(collection_name: str) -> bool:
    client = _get_client()
    try:
        return any(c.name == collection_name for c in client.get_collections().collections)
    except Exception:
        return False

def create_collection(collection_name: str, vector_size: int = 384):
    client = _get_client()
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=rest.VectorParams(size=vector_size, distance=rest.Distance.COSINE)
    )

def upsert_documents(collection_name: str, items: list):
    client = _get_client()
    points = [
        rest.PointStruct(id=it["id"], vector=it["vector"], payload=it.get("payload", {}))
        for it in items
    ]
    client.upsert(collection_name=collection_name, points=points)

def search(collection_name: str, query_text: str, top_k: int = 4):
    model = _get_model()
    qvec = model.encode([query_text])[0].tolist()
    client = _get_client()
    hits = client.search(collection_name=collection_name, query_vector=qvec, limit=top_k)
    return [{"id": h.id, "score": h.score, "payload": h.payload} for h in hits]
