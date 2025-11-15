from pydantic import BaseModel
import os
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseModel):
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    allow_signin_password: str | None = os.getenv("ALLOW_SIGNIN_PASSWORD")
    chroma_dir: str = os.getenv("CHROMA_DIR", "./data/vectorstore")
    upload_dir: str = os.getenv("UPLOAD_DIR", "./data/uploads")
    embeddings_provider: str = os.getenv("EMBEDDINGS_PROVIDER", "openai")
    max_ctx_docs: int = 6
    chunk_size: int = 800
    chunk_overlap: int = 100

settings = Settings()
os.makedirs(settings.chroma_dir, exist_ok=True)
os.makedirs(settings.upload_dir, exist_ok=True)