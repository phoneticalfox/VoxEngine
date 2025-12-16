"""Ollama LLM adapter (placeholder)."""

class OllamaLLMAdapter:
    def generate_scene(self, prompt: str, constraints: dict) -> dict:
        return {"text": f"[ollama placeholder]\n\n{prompt}", "metadata": {"constraints": constraints}}

    def rewrite_line(self, line: str, direction: str, num: int) -> list[str]:
        return [f"[ollama placeholder] ({direction}) {line}" for _ in range(num)]
