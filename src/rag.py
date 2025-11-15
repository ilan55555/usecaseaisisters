from src.config import settings
from typing import List, Dict
import requests, time, random

SYSTEM_PROMPT = """Tu es un assistant juridique interne.
Réponds UNIQUEMENT avec les informations contenues dans le CONTEXTE fourni.
Si le contexte ne contient pas la réponse, dis poliment que tu ne peux pas répondre.
Toujours citer les documents sources (nom + chunk) en fin de réponse.
Langue: français.
"""

# on limite la taille du contexte pour réduire le risque de 429/timeout
def _truncate(text: str, max_chars: int = 6000) -> str:
    return text if len(text) <= max_chars else text[:max_chars] + "\n[...]"

def build_context(hits: List[Dict]) -> str:
    blocks = []
    for h in hits:
        fn = h["meta"].get("filename","?")
        idx = h["meta"].get("chunk_index",0)
        blocks.append(f"[{fn} | chunk {idx}]\n{h['text']}")
    ctx = "\n\n---\n\n".join(blocks)
    return _truncate(ctx, 6000)

def _openai_chat(messages: List[Dict]) -> str:
    api_key = settings.openai_api_key
    if not api_key:
        return "Configuration manquante : la clé OPENAI_API_KEY n'est pas définie dans le fichier .env."

    url = "https://api.openai.com/v1/chat/completions"
    payload = {
        "model": "gpt-4o-mini",   # tu peux mettre un modèle encore plus petit si 429 persiste
        "messages": messages,
        "temperature": 0.0,
        "max_tokens": 500,
    }

    s = requests.Session()
    s.trust_env = False  # pas de proxies système

    backoff = 1.0
    for attempt in range(6):  # 6 tentatives: ~1+2+4+8+16+16s max
        r = s.post(
            url,
            json=payload,
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=60,
        )
        if r.status_code in (429, 500, 502, 503, 504):
            # backoff exponentiel + jitter
            sleep_s = backoff + random.uniform(0, 0.5)
            time.sleep(sleep_s)
            backoff = min(backoff * 2, 16)
            continue
        try:
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]
        except Exception:
            # autre erreur -> on sort de la boucle
            break

    # Fallback propre si ça échoue encore
    return (
        "Le service d'IA est momentanément saturé (429). "
        "Voici les passages pertinents trouvés ; réessaie dans quelques secondes.\n\n"
    )

def grounded_answer(question: str, hits: List[Dict]) -> str:
    if not hits:
        return "Je n’ai rien trouvé de pertinent dans les documents indexés pour répondre à cette question."
    context = build_context(hits)
    user_prompt = (
        f"CONTEXTE:\n{context}\n\nQUESTION:\n{question}\n\n"
        "INSTRUCTIONS:\n- Réponds de façon concise et structurée.\n- Ne pas inventer.\n"
        "- Ajoute une section 'Sources' listant [filename | chunk]."
    )
    messages = [
        {"role":"system", "content": SYSTEM_PROMPT},
        {"role":"user", "content": user_prompt}
    ]
    return _openai_chat(messages)