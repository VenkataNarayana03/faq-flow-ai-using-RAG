chat_history = []

def get_history():
    return "\n".join(chat_history[-10:])

def update_history(query, answer):
    chat_history.append(f"User: {query}")
    chat_history.append(f"Bot: {answer}")
