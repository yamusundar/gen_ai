from app.services.llm_service import ask_gemini


question = """
You are a multilingual railway assistant.

Translate this Tanglish question into clear English:

"12675 la next station enna?"
"""


answer = ask_gemini(question)


print("\nGemini response:\n")
print(answer)