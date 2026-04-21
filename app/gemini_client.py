import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def ask_gemini(prompt: str, model_name: str):
    model = genai.GenerativeModel(model_name)
    response = model.generate_content(prompt)
    return response.text