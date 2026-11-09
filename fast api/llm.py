import os
from dotenv import load_dotenv
from google import genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file")

client = genai.Client(api_key=api_key)


def analyze_document(document_text: str, instruction: str):

    prompt = f"""
You are an AI Document Intelligence Assistant.

DOCUMENT:
{document_text}

USER REQUEST:
{instruction}

Use only the information in the document.
Answer clearly and concisely.
Do not invent information.
"""

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text







