import os, hashlib
import streamlit as st
from qdrant_client import QdrantClient, models
from src.config import settings
from src.embeddings import get_embedder
from src.preprocessing import read_any, chunk

# On réutilise ce dossier pour l'index local Qdrant
os.makedirs(settings.chroma_dir, exist_ok=True)

@st.cache_resource(show_spinner=False)
def get_qdrant() -> QdrantClient:
    # Une seule instance par process Streamlit
    return QdrantClient(path=settings.chroma_dir)

_embed = get_embedder()
_COLLECTION = "legal_docs"

def _ensure_collection(dim: int):
    client = get_qdrant()
    try:
        client.get_collection(_COLLECTION)
    except Exception:
        client.create_collection(
            collection_name=_COLLECTION,
            vectors_config=models.VectorParams(size=dim, distance=models.Distance.COSINE),
        )

def _doc_id(path:str, chunk_index:int)->int:
    h = hashlib.sha256(f"{path}-{chunk_index}".encode()).hexdigest()
    return int(h[:16], 16)

def add_path(path: str):
    text = read_any(path)
    chunks = list(chunk(text, settings.chunk_size, settings.chunk_overlap))
    if not chunks:
        return 0, 0
    # calc dim
    dim = len(_embed([chunks[0]])[0])
    _ensure_collection(dim)
    vectors = _embed(chunks)
    fname = os.path.basename(path)
    points = [
        models.PointStruct(
            id=_doc_id(path, i),
            vector=v,
            payload={"source": path, "filename": fname, "chunk_index": i, "text": t},
        )
        for i, (v,t) in enumerate(zip(vectors, chunks))
    ]
    client = get_qdrant()
    client.upsert(collection_name=_COLLECTION, points=points)
    return len(chunks), len(text)

def delete_by_source(source_path: str):
    client = get_qdrant()
    client.delete(
        collection_name=_COLLECTION,
        points_selector=models.FilterSelector(
            filter=models.Filter(
                must=[models.FieldCondition(
                    key="source", match=models.MatchValue(value=source_path)
                )]
            )
        ),
    )
    return True

def query(q: str, k: int):
    qvec = _embed([q])[0]
    _ensure_collection(len(qvec))
    client = get_qdrant()
    res = client.search(
        collection_name=_COLLECTION,
        query_vector=qvec,
        limit=k,
        with_payload=True,
    )
    hits = []
    for r in res:
        pl = r.payload or {}
        hits.append({
            "id": r.id,
            "text": pl.get("text", ""),
            "meta": {
                "source": pl.get("source"),
                "filename": pl.get("filename"),
                "chunk_index": pl.get("chunk_index", 0),
                "score": r.score,
            }
        })
    return hits