import os
import numpy as np
from src.config import settings

# --- Fallback très simple : si rien n'est dispo, on encode en vecteurs constants ---
def _dummy_embed(texts):
    # Renvoie une liste de vecteurs identiques, juste pour les tests CI
    return [np.ones(384).tolist() for _ in texts]


def get_embedder():
    """Choisit le fournisseur d'embedding disponible."""
    provider = getattr(settings, "embeddings_provider", "local")

    # 🔹 Option 1 : OpenAI (production)
    if provider == "openai":
        try:
            from openai import OpenAI
            _client = OpenAI(api_key=settings.openai_api_key)

            def _openai_embed(texts):
                res = _client.embeddings.create(model="text-embedding-3-small", input=texts)
                return [d.embedding for d in res.data]

            return _openai_embed
        except Exception:
            pass  # fallback automatique

    # 🔹 Option 2 : SentenceTransformer (local)
    try:
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer("all-MiniLM-L6-v2")

        def _local_embed(texts):
            arr = model.encode(texts, convert_to_numpy=True)  # ✅ renvoie un np.ndarray
            return arr.tolist()

        return _local_embed
    except Exception:
        # 🔹 Fallback : dummy embed (CI ou offline)
        return _dummy_embed