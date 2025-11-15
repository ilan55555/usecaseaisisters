from src.rag import grounded_answer

def test_rag_does_not_hallucinate():
    """Vérifie que le LLM ne répond pas à une question hors corpus"""
    hits = []  # aucun document fourni
    q = "Quelle est la date aujourd'hui ?"
    ans = grounded_answer(q, hits)

    print("Réponse LLM:", ans[:200])
    assert not any(word in ans.lower() for word in ["novembre", "2025", "aujourd'hui", "demain"]), \
        "⚠️ Le modèle semble avoir répondu avec des infos externes"