from config import config
from .assistants.ollama_engine import OllamaEngine
from .assistants.openrouter_engine import OpenRouterEngine

class LLMEngine:
    def __init__(self):
        # Primary model using Ollama (local)
        self.primary = OllamaEngine(model=config.OLLAMA_MODEL)

        # Fallback model using OpenRouter (only if configured)
        self.fallback = OpenRouterEngine() if config.OPENROUTER_API_KEY else None

    def chat(self, prompt: str) -> str:
        try:
            return self.primary.chat(prompt)
        except Exception as e:
            print(f"[LLMEngine] ⚠️ Ollama failed: {e}")
            if self.fallback:
                print("[LLMEngine] ⏪ Falling back to OpenRouter...")
                return self.fallback.chat(prompt)
            else:
                raise RuntimeError("No fallback LLM engine available and primary failed.")