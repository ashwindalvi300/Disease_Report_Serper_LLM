# llm_client.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("LLM_API_URL")
API_KEY = os.getenv("LLM_API_KEY")

if not API_URL:
    raise ValueError("❌ Missing LLM_API_URL in .env")

if not API_KEY:
    raise ValueError("❌ Missing LLM_API_KEY in .env")

LLM_CONFIG = {
    "model": "gpt-oss:20b",# "mistral-small3.2:latest"
    "temperature": 0,
    "timeout": 180
}

def chat_llm(prompt: str) -> str:

    headers = {
        "Content-Type": "application/json",
        "x-api-key": API_KEY
    }

    payload = {
        "model": LLM_CONFIG["model"],
        "prompt": prompt,
        "temperature": LLM_CONFIG["temperature"]
    }

    try:
        response = requests.post(
            API_URL,
            json=payload,
            headers=headers,
            timeout=LLM_CONFIG["timeout"]
        )

        response.raise_for_status()

        data = response.json()
        return data.get("response") or data.get("text") or str(data)

    except Exception as e:
        return f"❌ LLM Error: {str(e)}"
