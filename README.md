⚖️ Legal RAG PoC – Extraction d’information juridique assistée par IA

PoC démontrant une solution RAG locale, sécurisée et contrôlable, permettant d’interroger un corpus juridique sans fuite de données. Interface Streamlit, réponses fondées uniquement sur les documents internes, anti-hallucination et traçabilité des sources.

⚙️ Installation
git clone https://github.com/ilan55555/usecaseaisisters.git
cd legal_rag_poc

1. Environnement
conda create -n legal_rag_env python=3.11 -y
conda activate legal_rag_env
pip install -r requirements.txt

2. Clés API

Créer un fichier .env à la racine du projet :

OPENAI_API_KEY=sk-xxxx


💡 Pour utiliser Claude, Gemini ou un autre LLM, adapter src/rag.py.

🚀 Lancement
streamlit run streamlit_app.py


Puis ouvrir : http://localhost:8501

🧩 Structure du projet
legal_rag_poc/
├── streamlit_app.py
├── pages/
│   ├── 1_Chat.py
│   └── 2_Gestion_docs.py
├── src/
│   ├── embeddings.py
│   ├── vectorstore.py
│   ├── rag.py
│   ├── config.py
│   ├── security.py
│   └── persist.py
├── data/
│   ├── uploads/
│   ├── vectorstore/
│   └── chat_history.json
└── tests/
    ├── test_smoke.py
    └── test_rag_guardrails.py

🧠 Fonctionnement

Upload de documents internes (.txt, .csv, .html)

Nettoyage → segmentation → vectorisation (embeddings)

Indexation dans une base vectorielle locale (Qdrant)

À chaque question :

recherche des passages les plus pertinents

génération d’une réponse strictement basée sur ces passages

Historique des conversations enregistré dans data/chat_history.json

🧪 Tests

Exécuter tous les tests :

python -m pytest -s -q


Tests inclus :

test_smoke.py → vérifie que le pipeline RAG complet fonctionne (ingestion → recherche → réponse)

test_rag_guardrails.py → vérifie qu’aucune réponse n’est générée hors du corpus interne

Exemple de sortie attendue :

Réponse LLM : La clause de non-concurrence dure 12 mois après la rupture du contrat.
✅ OK

🔐 Sécurité
Mesures déjà en place

Données stockées uniquement en local dans data/

Aucune transmission des documents bruts vers Internet

L’API LLM est utilisée uniquement pour les embeddings et la génération

Données anonymisées pour la PoC

Session utilisateur temporaire (timeout)

Aucun log contenant de données sensibles

Améliorations possibles (roadmap sécurité)

🔒 Chiffrement des fichiers et embeddings (AES-256)

🔑 Authentification unique (SSO)

🧩 Gestion des rôles et droits d’accès (RBAC)

📜 Audit log complet des accès et requêtes

🛡️ Hébergement on-premise ou cloud souverain

📈 Monitoring et alertes de sécurité

🗺️ Roadmap
Phase 1 – PoC (terminée ✅)

RAG local avec embeddings OpenAI / SentenceTransformers

Interface Streamlit (2 pages : Chat + Gestion des documents)

Upload et vectorisation automatiques

Historique conversationnel persistant

Tests end-to-end et garde-fous anti-hallucination

Phase 2 – Fiabilisation 🔧

Passage complet à Qdrant serveur (ou ChromaDB serveur)

Nettoyage et validation automatique des métadonnées

Journalisation et gestion d’erreurs plus fines

Intégration CI/CD (tests automatisés à chaque push)

Phase 3 – Sécurité & Scalabilité 🔐

Authentification SSO

Chiffrement complet des données (au repos et en transit)

Audit logs + supervision

Multi-utilisateurs avec isolation des espaces de travail

Phase 4 – Intelligence améliorée 🧠

Recherche hybride (full-text + sémantique)

Reranking (ex. BGE / ColBERT)

Fine-tuning / adaptation sur corpus juridique interne

Mémoire conversationnelle par utilisateur (contexte long terme)

📚 Technologies clés

Interface : Streamlit

LLM : OpenAI GPT-4 (via API)

Vectorisation : SentenceTransformers / OpenAI embeddings

Stockage vectoriel : Qdrant (local) / compatible ChromaDB

Tests : Pytest

Configuration : dotenv + Pydantic

👤 Auteur

Développé par Ilan Schwarz (2025)
Projet de démonstration pour validation technique – Cabinet d’avocats, PoC confidentiel.