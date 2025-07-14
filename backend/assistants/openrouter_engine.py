import requests
import os

class OpenRouterEngine:
    def __init__(self, model="cognitivecomputations/dolphin-mistral-24b-venice-edition:free"):
        self.api_key = os.getenv("OPENROUTER_API_KEY")
        self.model = model

    def chat(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}]
        }
        resp = requests.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
        return resp.json()["choices"][0]["message"]["content"].strip()