# src/embeddings.py
import os
import numpy as np

# --- Fallback offline/CI: vecteur constant déterministe ---
def _dummy_embed(texts, dim=384):
    return [np.ones(dim, dtype=np.float32).tolist() for _ in texts]

def get_embedder():
    """
    Choisit la source d'embeddings.
    Priorité:
      1) RAG_EMBEDDINGS (ou EMBEDDINGS_PROVIDER) dans l'environnement
      2) settings.embeddings_provider si dispo
      3) 'dummy' en CI, sinon 'local'
    Renvoie toujours une fonction: List[str] -> List[List[float]]
    """
    # 1) Variables d'env (CI, prod, etc.)
    provider = (os.getenv("RAG_EMBEDDINGS")
                or os.getenv("EMBEDDINGS_PROVIDER"))

    # 2) Config code (optionnelle)
    if not provider:
        try:
            from src.config import settings  # import lazy pour éviter erreurs en tests
            provider = getattr(settings, "embeddings_provider", None)
        except Exception:
            provider = None

    # 3) Défaut robuste
    if not provider:
        provider = "dummy" if os.getenv("CI") else "local"

    provider = provider.lower().strip()

    # --- Dummy forcé (CI / offline) ---
    if provider == "dummy":
        return _dummy_embed

    # --- Local: SentenceTransformers ---
    if provider == "local":
        try:
            from sentence_transformers import SentenceTransformer
            model_name = os.getenv("ST_MODEL", "all-MiniLM-L6-v2")
            _model = SentenceTransformer(model_name)

            def _local_embed(texts):
                # IMPORTANT: numpy=True -> toujours .tolist() derrière
                arr = _model.encode(texts, convert_to_numpy=True)
                return arr.tolist()

            return _local_embed
        except Exception:
            # Pas dispo ? On retombe en dummy
            return _dummy_embed

    # --- OpenAI embeddings ---
    if provider == "openai":
        try:
            import requests
            api_key = os.getenv("OPENAI_API_KEY", "")
            model = os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")

            def _openai_embed(texts):
                r = requests.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={"Authorization": f"Bearer {api_key}"},
                    json={"input": texts, "model": model},
                    timeout=60,
                )
                r.raise_for_status()
                data = r.json().get("data", [])
                return [d["embedding"] for d in data]

            return _openai_embed
        except Exception:
            return _dummy_embed

    # Provider inconnu -> dummy
    return _dummy_embed