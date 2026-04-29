from app.config.settings import (
    GROQ_API_KEY,
    GROQ_MODEL,
    LLM_PROVIDER,
    OPENAI_API_KEY,
    OPENAI_MODEL,
    require_setting,
)

def generate_answer(query, contexts, history=""):
    context_text = "\n\n".join(contexts)
    if not context_text:
        context_text = "No matching context was found in the knowledge base."

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful customer support assistant. "
                "Answer using the retrieved context when it is relevant. "
                "If the context does not contain the answer, say that you do not know from the available data. "
                "Keep answers concise and easy to read. Use short bullet points only when there are multiple steps. "
                "Do not write long paragraphs. "
                "At the end of your response, always suggest 1 or 2 relevant follow-up clarifications or questions the user might want to ask to continue the conversation."
            ),
        },
        {
            "role": "user",
            "content": f"""Chat History:
{history or "No previous chat history."}

Retrieved Context:
{context_text}

Question:
{query}""",
        },
    ]

    if LLM_PROVIDER == "openai":
        from openai import OpenAI

        client = OpenAI(api_key=require_setting("OPENAI_API_KEY", OPENAI_API_KEY))
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=messages,
            temperature=0.2,
        )
        return response.choices[0].message.content

    from groq import Groq

    client = Groq(api_key=require_setting("GROQ_API_KEY", GROQ_API_KEY))
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=messages,
        temperature=0.2,
    )

    return response.choices[0].message.content
