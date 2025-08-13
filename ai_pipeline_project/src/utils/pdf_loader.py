# src/utils/pdf_loader.py
"""
Loads PDF and splits text into chunks.
Simple chunker: concatenates page texts and splits by approx token/word count.
"""

from typing import List
from pathlib import Path
from pypdf import PdfReader
import re
import uuid

def _clean_text(s: str) -> str:
    s = re.sub(r"\s+", " ", s).strip()
    return s

def load_pdf_text(pdf_path: str) -> str:
    reader = PdfReader(pdf_path)
    pages = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    return "\n".join(pages)

def split_text_to_chunks(text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
    """
    chunk_size measured in words (approx). Simple sliding window.
    """
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk_words = words[i:i+chunk_size]
        chunks.append(" ".join(chunk_words))
        i += chunk_size - overlap
    return [ _clean_text(c) for c in chunks if c.strip() ]

def load_pdf_text_chunks(pdf_path: str, chunk_size: int = 400, overlap: int = 50):
    text = load_pdf_text(pdf_path)
    return [{"id": str(uuid.uuid4()), "text": chunk} for chunk in split_text_to_chunks(text, chunk_size, overlap)]
