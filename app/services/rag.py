from app.services.retriever import retrieve
from app.services.generator import generate_answer
from app.services.memory import get_history, update_history

def rag_pipeline(query: str):
    query = query.strip()
    if not query:
        return {"answer": "Please enter a question.", "contexts": []}

    contexts = retrieve(query)
    history = get_history()

    answer = generate_answer(query, contexts, history)

    update_history(query, answer)

    return {"answer": answer, "contexts": contexts}
