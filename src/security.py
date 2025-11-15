import streamlit as st
from src.config import settings

def gated_access():
    if settings.allow_signin_password:
        if "auth_ok" not in st.session_state:
            st.session_state.auth_ok = False
        if not st.session_state.auth_ok:
            pwd = st.text_input("Mot de passe (démo interne)", type="password")
            if st.button("Entrer"):
                st.session_state.auth_ok = (pwd == settings.allow_signin_password)
                if not st.session_state.auth_ok:
                    st.error("Mot de passe incorrect.")
            st.stop()

import time
SESSION_TIMEOUT_MIN = 20

def session_timeout_guard():
    now = time.time()
    if "last_active" not in st.session_state:
        st.session_state.last_active = now
    elif now - st.session_state.last_active > SESSION_TIMEOUT_MIN * 60:
        st.session_state.auth_ok = False
        st.warning("Session expirée, merci de vous reconnecter.")
        st.stop()
    st.session_state.last_active = now