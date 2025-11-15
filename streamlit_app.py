import streamlit as st
from src.security import gated_access

st.set_page_config(page_title="Legal RAG PoC", page_icon="⚖️", layout="wide")
gated_access()
st.title("⚖️ Legal RAG – PoC")
st.caption("Chat interne sécurisé basé sur vos documents anonymisés.")

st.page_link("pages/1_Chat.py", label="💬 Interface Chatbot", icon="💬")
st.page_link("pages/2_Gestion_des_documents.py", label="🗂️ Gestion des documents", icon="🗂️")