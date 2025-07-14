import subprocess

class OllamaEngine:
    def __init__(self, model="llama3.2:latest"):
        self.model = model

    def chat(self, prompt: str) -> str:
        result = subprocess.run(
            ["ollama", "run", self.model],
            input=prompt.encode(),
            stdout=subprocess.PIPE
        )
        return result.stdout.decode("utf-8").strip()