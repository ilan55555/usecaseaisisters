import streamlit as st, os
from src.config import settings
from src.vectorstore import add_path, delete_by_source

st.title("🗂️ Gestion des documents")
st.caption("Uploader / supprimer. La vectorisation est automatique.")

upl = st.file_uploader("Ajouter des fichiers (.txt, .csv, .html)", type=["txt","csv","html"], accept_multiple_files=True)
if upl:
    for f in upl:
        dest = os.path.join(settings.upload_dir, f.name)
        with open(dest, "wb") as out:
            out.write(f.read())
        with st.spinner(f"Vectorisation de {f.name}..."):
            try:
                n_chunks, n_chars = add_path(dest)
                st.success(f"{f.name}: {n_chunks} chunks indexés ({n_chars} caractères).")
            except Exception as e:
                st.error(f"Echec pour {f.name}: {e}")

st.subheader("Fichiers existants")
files = sorted([f for f in os.listdir(settings.upload_dir) if not f.startswith(".")])
if files:
    for name in files:
        col1,col2 = st.columns([6,1])
        with col1: st.write(name)
        with col2:
            if st.button("Supprimer", key=f"del-{name}"):
                path = os.path.join(settings.upload_dir, name)
                with st.spinner("Suppression des vecteurs..."):
                    try:
                        delete_by_source(path)
                        os.remove(path)
                        st.success("Supprimé.")
                        st.experimental_rerun()
                    except Exception as e:
                        st.error(f"Erreur: {e}")
else:
    st.info("Aucun fichier pour le moment.")