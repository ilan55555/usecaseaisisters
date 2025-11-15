import os
from src.vectorstore import add_path, query
from src.rag import grounded_answer
from src.config import settings

DOC = "data/uploads/test_doc.txt"

def test_rag_pipeline():
    os.makedirs("data/uploads", exist_ok=True)
    with open(DOC, "w", encoding="utf-8") as f:
        f.write("La clause de non-concurrence dure 12 mois après la rupture du contrat.")

    chunks, _ = add_path(DOC)
    assert chunks > 0, "Aucun chunk indexé"

    hits = query("Quelle est la durée de la clause de non-concurrence ?", settings.max_ctx_docs)
    assert hits, "Aucun passage trouvé"

    ans = grounded_answer("Quelle est la durée de la clause de non-concurrence ?", hits)
    print("Réponse LLM:", ans[:200])
    assert ("12 mois" in ans) or ("douze" in ans.lower())

if __name__ == "__main__":
    test_rag_pipeline()
    print("✅ OK")