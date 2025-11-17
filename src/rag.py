# src/rag.py
import os
import re
from typing import List, Dict

# --- DUMMY (offline, déterministe) ---
_DURATION_RX = re.compile(r"(\b\d{1,3}\b)\s*(mois|jour|jours|semaine|semaines|an|ans)", re.IGNORECASE)

def _dummy_answer(question: str, hits: List[Dict]) -> str:
    joined = "\n".join(h.get("text", "") for h in hits)
    m = _DURATION_RX.search(joined)
    if m:
        val, unit = m.group(1), m.group(2).lower()
        base = f"La durée indiquée est **{val} {unit}**."
    else:
        snip = (joined[:300] + "…") if len(joined) > 300 else joined
        base = "Voici les passages pertinents trouvés dans les documents fournis :\n\n" + snip

    sources = []
    for h in hits:
        meta = h.get("meta", {})
        sources.append(f"- {meta.get('filename','?')} · chunk {meta.get('chunk_index',0)}")
    src_block = "\n".join(sources) if sources else "Aucune source trouvée."
    return f"{base}\n\n**Sources**\n{src_block}"

# --- Sélecteur de provider (NE JAMAIS APPELER LE RESEAU EN CI) ---
def _pick_provider() -> str:
    # Forcer offline si CI ou si clés factices/absentes
    if os.getenv("CI") == "true" or os.getenv("CI") == "True" or os.getenv("CI") == "1":
        return "dummy"
    if (os.getenv("LLM_PROVIDER") or "").lower().strip() == "dummy":
        return "dummy"
    if (os.getenv("OPENAI_API_KEY", "") in ("", "dummy")) and (os.getenv("ANTHROPIC_API_KEY", "") in ("", "dummy")):
        return "dummy"
    # sinon, laisser "openai" par défaut (ou anthropic si tu veux)
    return (os.getenv("LLM_PROVIDER") or "openai").lower().strip()

# --- OpenAI (prod locale uniquement) ---
def _openai_answer(question: str, hits: List[Dict]) -> str:
    import requests
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key or api_key == "dummy":  # sécurité supplémentaire
        return _dummy_answer(question, hits)

    ctx = "\n\n".join([f"[{i+1}] {h.get('text','')}" for i,h in enumerate(hits)])
    sys_prompt = ("Tu es un assistant juridique interne. Réponds UNIQUEMENT à partir des passages fournis. "
                  "Si l'information n'est pas présente, dis-le. Cite les sources.")
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            json={"model": os.getenv("OPENAI_CHAT_MODEL","gpt-4o-mini"),
                  "messages":[{"role":"system","content":sys_prompt},
                              {"role":"user","content":f"Contexte:\n{ctx}\n\nQuestion: {question}"}],
                  "temperature":0},
            timeout=60,
        )
        r.raise_for_status()
        txt = r.json()["choices"][0]["message"]["content"]
    except Exception:
        return _dummy_answer(question, hits)

    sources = []
    for h in hits:
        meta = h.get("meta", {})
        sources.append(f"- {meta.get('filename','?')} · chunk {meta.get('chunk_index',0)}")
    return f"{txt}\n\n**Sources**\n" + ("\n".join(sources) or "Aucune source trouvée.")

# --- Anthropic (optionnel, prod locale) ---
def _anthropic_answer(question: str, hits: List[Dict]) -> str:
    import requests
    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key or api_key == "dummy":
        return _dummy_answer(question, hits)

    ctx = "\n\n".join([f"[{i+1}] {h.get('text','')}" for i,h in enumerate(hits)])
    sys_prompt = ("Tu es un assistant juridique interne. Réponds UNIQUEMENT à partir des passages fournis. "
                  "Si l'information n'est pas présente, dis-le. Cite les sources.")
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": api_key, "anthropic-version": "2023-06-01", "content-type": "application/json"},
            json={"model": os.getenv("ANTHROPIC_MODEL","claude-3-5-sonnet-latest"),
                  "max_tokens": 512,
                  "system": sys_prompt,
                  "messages": [{"role":"user","content":f"Contexte:\n{ctx}\n\nQuestion: {question}"}]},
            timeout=60,
        )
        r.raise_for_status()
        data = r.json()
        txt = ""
        if "content" in data and data["content"] and isinstance(data["content"][0], dict):
            txt = data["content"][0].get("text", "") or ""
        if not txt:
            return _dummy_answer(question, hits)
    except Exception:
        return _dummy_answer(question, hits)

    sources = []
    for h in hits:
        meta = h.get("meta", {})
        sources.append(f"- {meta.get('filename','?')} · chunk {meta.get('chunk_index',0)}")
    return f"{txt}\n\n**Sources**\n" + ("\n".join(sources) or "Aucune source trouvée.")

# --- Entrée publique ---
def grounded_answer(question: str, hits: List[Dict]) -> str:
    provider = _pick_provider()
    if provider == "dummy":
        return _dummy_answer(question, hits)
    if provider == "anthropic":
        return _anthropic_answer(question, hits)
    return _openai_answer(question, hits)