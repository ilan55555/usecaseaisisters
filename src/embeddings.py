from src.config import settings
from typing import List
from sentence_transformers import SentenceTransformer
import requests
import os

_local_model = None

def _openai_embed(texts: List[str]) -> List[List[float]]:
    # ton code REST ici
    ...

def get_embedder():
    if settings.embeddings_provider == "openai":
        return _openai_embed
    else:
        global _local_model
        if _local_model is None:
            _local_model = SentenceTransformer("all-MiniLM-L6-v2")
        def _embed(texts: list[str]) -> list[list[float]]:
            return _local_model.encode(texts, convert_to_numpy=True).tolist()
        return _embed