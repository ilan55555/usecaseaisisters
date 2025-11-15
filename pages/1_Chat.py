# pages/1_Chat.py
import streamlit as st
from datetime import datetime
import uuid

from src.security import gated_access, session_timeout_guard
from src.config import settings
from src.vectorstore import query
from src.rag import grounded_answer
from src.persist import load_history, save_history

# --- Config Streamlit (doit être tout en haut) ---
st.set_page_config(page_title="Chat", page_icon="💬", layout="wide")

# --- Accès protégé + timeout de session ---
gated_access()
session_timeout_guard()

st.title("💬 Chat sur les documents")
st.caption("Réponses strictement basées sur les documents vectorisés. Les sources sont citées.")

# =========================
# State & Persistance
# =========================
def _init_state():
    if "conversations" not in st.session_state:
        st.session_state.conversations = load_history()  # charge depuis data/chat_history.json
    if "current_conv_id" not in st.session_state:
        st.session_state.current_conv_id = (
            st.session_state.conversations[-1]["id"] if st.session_state.conversations else None
        )
    if "last_submitted_q" not in st.session_state:
        st.session_state.last_submitted_q = None
    if "last_answer" not in st.session_state:
        st.session_state.last_answer = None

def _new_conversation(init_title="Nouvelle conversation"):
    cid = str(uuid.uuid4())[:8]
    now = datetime.utcnow().isoformat(timespec="seconds")
    conv = {
        "id": cid,
        "title": init_title,
        "messages": [],
        "created_at": now,
        "updated_at": now,
    }
    st.session_state.conversations.append(conv)
    st.session_state.current_conv_id = cid
    save_history(st.session_state.conversations)
    return cid

def _get_current_conv():
    for c in st.session_state.conversations:
        if c["id"] == st.session_state.current_conv_id:
            return c
    return None

def _set_current_conv(cid: str):
    st.session_state.current_conv_id = cid

def _rename_current_conv(title: str):
    conv = _get_current_conv()
    if conv and title.strip():
        conv["title"] = title.strip()
        conv["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
        save_history(st.session_state.conversations)

def _delete_current_conv():
    cid = st.session_state.current_conv_id
    if cid is None:
        return
    st.session_state.conversations = [c for c in st.session_state.conversations if c["id"] != cid]
    st.session_state.current_conv_id = (
        st.session_state.conversations[-1]["id"] if st.session_state.conversations else None
    )
    save_history(st.session_state.conversations)

_init_state()

# =========================
# Sidebar : gestion des conversations (tri par dernière activité)
# =========================
with st.sidebar:
    st.subheader("💬 Conversations")

    if st.button("➕ Nouvelle conversation", use_container_width=True):
        _new_conversation()

    st.divider()

    convs = sorted(
        st.session_state.conversations,
        key=lambda c: c.get("updated_at", c.get("created_at", "")),
        reverse=True,
    )
    if convs:
        labels = [
            f"{c['title']}  ·  {c.get('updated_at', c['created_at']).replace('T',' ')}"
            for c in convs
        ]
        ids = [c["id"] for c in convs]
        picked = st.radio("Historique (récents en haut)", labels, index=0, key="conv_picker")
        _set_current_conv(ids[labels.index(picked)])

        conv = _get_current_conv()
        if conv:
            new_title = st.text_input("Renommer", value=conv["title"])
            if new_title != conv["title"]:
                _rename_current_conv(new_title)
            if st.button("🗑️ Supprimer cette conversation"):
                _delete_current_conv()
                st.experimental_rerun()
    else:
        st.info("Aucune conversation. Crée la première avec le bouton ci-dessus.")

# Si aucune conversation, en créer une par défaut
if not st.session_state.conversations:
    _new_conversation()

conv = _get_current_conv()

# =========================
# Affichage intégral de la conversation sélectionnée
# =========================
if conv:
    if conv["messages"]:
        for m in conv["messages"]:
            with st.chat_message(m["role"]):
                st.markdown(m["content"])
    else:
        st.info("Aucun message dans cette conversation. Pose ta première question ci-dessous.")

# =========================
# Zone de saisie (form pour éviter doubles appels)
# =========================
st.divider()
with st.form("chat_form", clear_on_submit=True):
    q = st.text_input(
        "Pose ta question…",
        placeholder="Ex. Quelle est la durée de la clause de non-concurrence ?",
    )
    submit = st.form_submit_button("Envoyer")

if submit and q:
    # Anti double appel en cas de re-render
    if q == st.session_state.last_submitted_q and st.session_state.last_answer:
        with st.chat_message("assistant"):
            st.markdown(st.session_state.last_answer)
    else:
        # 1) Append message user
        conv["messages"].append({"role": "user", "content": q})
        conv["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
        save_history(st.session_state.conversations)

        # 2) Retrieval
        hits = query(q, settings.max_ctx_docs)
        if not hits:
            st.warning("Aucun passage pertinent trouvé. Ajoute des documents dans 🗂️ Gestion des documents.")
            st.stop()

        # 3) Passages utilisés (transparence)
        with st.expander("🧠 Passages utilisés (pour ce tour)"):
            for h in hits:
                st.markdown(
                    f"**{h['meta'].get('filename','?')}** · chunk {h['meta'].get('chunk_index',0)} · score {h['meta'].get('score',0):.3f}"
                )
                st.code(h["text"][:800])

        # 4) Appel LLM (réponse ancrée) + spinner
        with st.spinner("Je réfléchis…"):
            try:
                ans = grounded_answer(q, hits)
            except Exception as e:
                ans = f"Le service est momentanément indisponible : {e}"

        # 5) Afficher + stocker
        with st.chat_message("assistant"):
            st.markdown(ans)
            # petit rappel des sources en dessous (optionnel)
            st.code(
                "\n".join([f"[{h['meta']['filename']} | chunk {h['meta']['chunk_index']}]"
                           for h in hits]),
                language=None
            )

        conv["messages"].append({"role": "assistant", "content": ans})
        conv["updated_at"] = datetime.utcnow().isoformat(timespec="seconds")
        save_history(st.session_state.conversations)

        # 6) Mémos anti-doubles
        st.session_state.last_submitted_q = q
        st.session_state.last_answer = ans

        # 7) Titre auto depuis la 1ʳᵉ question
        if conv["title"] in ("Nouvelle conversation", "", None):
            _rename_current_conv(q[:60])

st.caption("Sélectionne une conversation dans la barre latérale pour revoir **tous** ses échanges. L’historique est sauvegardé sur disque.")