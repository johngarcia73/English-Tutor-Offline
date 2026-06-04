from ollama import chat

SYSTEM_PROMPT = """
You are an English tutor.
Speak only English.
Correct grammar mistakes.
Keep responses short.
Ask a follow-up question.
"""

def ask_llm(user_text: str, history=None) -> str:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    if history:
        messages += history

    messages.append({"role": "user", "content": user_text})

    response = chat(
        model="llama3.1:latest",
        messages=messages
    )

    return response["message"]["content"]