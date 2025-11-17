⚙️ Installation et Configuration

**1. Cloner le projet**

git clone https://github.com/AI-Sisters/test_technique.git

cd legal_rag_poc

**2. Créer l’environnement**

conda create -n legal_rag_env python=3.11 -y
conda activate legal_rag_env
pip install -r requirements.txt

**3. Configurer les clés API**

Crée un fichier .env à la racine du projet contenant ta clé OpenAI :
OPENAI_API_KEY=sk-xxxx

💡 Pour Claude, Gemini ou un autre LLM, modifie src/rag.py pour pointer vers une autre API compatible (Anthropic, Mistral, etc.).

🚀 Lancement de l’application

streamlit run streamlit_app.py
Puis ouvre http://localhost:8501

**🧩 Structure du projet
**
legal_rag_poc/
├── streamlit_app.py
├── pages/
│ ├── 1_Chat.py
│ └── 2_Gestion_docs.py
├── src/
│ ├── embeddings.py
│ ├── vectorstore.py
│ ├── rag.py
│ ├── config.py
│ ├── security.py
│ └── persist.py
├── data/
│ ├── uploads/
│ ├── vectorstore/
│ └── chat_history.json
└── tests/
├── test_smoke.py
└── test_rag_guardrails.py

🧠 Fonctionnement

L’utilisateur charge des documents (.txt, .csv, .html)

Le texte est nettoyé, segmenté, puis vectorisé (embeddings)

À chaque question :

Les passages les plus pertinents sont recherchés dans la base vectorielle

Le LLM génère une réponse fondée uniquement sur ces passages

L’historique des conversations est enregistré localement dans data/chat_history.json

🧪 Tests

Pour exécuter tous les tests :
python -m pytest -s -q

Tests inclus

test_smoke.py → Vérifie que le pipeline RAG complet fonctionne
test_rag_guardrails.py → Vérifie qu’aucune réponse n’est générée hors du corpus interne

Exemple de sortie :
Réponse LLM : La clause de non-concurrence dure 12 mois après la rupture du contrat.
✅ OK

🔐 Sécurité
Mesures déjà en place

Données stockées uniquement en local dans data/

Aucun envoi des documents vers Internet

API LLM utilisée uniquement pour embeddings et génération de réponses

Données anonymisées pour la PoC

Session utilisateur temporaire (timeout)

Aucun log contenant de données sensibles

Améliorations prévues

🔒 Chiffrement des fichiers et embeddings (AES-256)

🔑 Authentification unique (SSO)

🧩 Gestion des rôles et droits d’accès

📜 Audit log complet des accès et requêtes

🛡️ Hébergement on-premise ou cloud souverain

📈 Monitoring et alertes de sécurité

**🗺️ Roadmap**

**Phase 1 – PoC (terminée ✅)**
 RAG local avec OpenAI embeddings

 Interface Streamlit (2 pages)

 Upload et vectorisation automatique

 Historique conversationnel persistant

 Tests end-to-end et anti-hallucination

**Phase 2 – Fiabilisation 🔧**
 Passage complet à ChromaDB ou Qdrant serveur

 Nettoyage et validation automatique des métadonnées

 Journalisation et gestion des erreurs

 Tests unitaires automatisés (CI/CD)

**Phase 3 – Sécurité & Scalabilité 🔐**
 Authentification SSO

 Chiffrement complet des données

 Audit logs + supervision

 Multi-utilisateurs isolés

**Phase 4 – Intelligence améliorée 🧠**
 Hybrid Search (texte + sémantique)

 Reranking (BGE / ColBERT)

 Fine-tuning sur corpus juridique

 Mémoire conversationnelle par utilisateur

**📚 Technologies clés
**
Interface : Streamlit
LLM : OpenAI GPT-4 (API)
Vectorisation : SentenceTransformers / OpenAI embeddings
Stockage vectoriel : Qdrant ou ChromaDB
Tests : Pytest
Configuration : dotenv + Pydantic

👤 Auteur

Développé par Ilan Schwarz (2025)
Projet de démonstration pour validation technique – Cabinet d’avocats, PoC confidentiel.
