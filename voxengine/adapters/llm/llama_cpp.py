"""llama.cpp adapter (placeholder)."""

class LlamaCppLLMAdapter:
    def generate_scene(self, prompt: str, constraints: dict) -> dict:
        return {"text": f"[llama.cpp placeholder]\n\n{prompt}", "metadata": {"constraints": constraints}}

    def rewrite_line(self, line: str, direction: str, num: int) -> list[str]:
        return [f"[llama.cpp placeholder] ({direction}) {line}" for _ in range(num)]
