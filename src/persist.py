# src/persist.py
from __future__ import annotations
import json, os, tempfile
from typing import Any, List, Dict
from datetime import datetime

# Dossier data/ déjà dans le projet
HISTORY_DIR = "data"
HISTORY_PATH = os.path.join(HISTORY_DIR, "chat_history.json")

def _ensure_dir():
    os.makedirs(HISTORY_DIR, exist_ok=True)

def load_history() -> List[Dict[str, Any]]:
    """Charge toutes les conversations depuis le disque. Liste vide si rien."""
    _ensure_dir()
    if not os.path.exists(HISTORY_PATH):
        return []
    try:
        with open(HISTORY_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            # format attendu: liste de conversations {id, title, messages, created_at}
            if isinstance(data, list):
                return data
            return []
    except Exception:
        # En cas de JSON corrompu, on repart à vide (PoC)
        return []

def save_history(conversations: List[Dict[str, Any]]) -> None:
    """Écrit le JSON de façon atomique (temp file -> os.replace)."""
    _ensure_dir()
    tmp_fd, tmp_path = tempfile.mkstemp(prefix="chat_hist_", suffix=".json", dir=HISTORY_DIR)
    try:
        with os.fdopen(tmp_fd, "w", encoding="utf-8") as f:
            json.dump(conversations, f, ensure_ascii=False, indent=2)
        os.replace(tmp_path, HISTORY_PATH)
    finally:
        # si quelque chose a planté avant os.replace, nettoyer le fichier temp
        if os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except Exception:
                pass