"""Script service (calls an LLM adapter)."""

from voxengine.core.registry import registry

class ScriptService:
    def __init__(self, llm_provider: str) -> None:
        self.llm_provider = llm_provider

    def generate_scene(self, prompt: str, constraints: dict) -> dict:
        return registry.llm_adapters[self.llm_provider].generate_scene(prompt, constraints)

    def rewrite_line(self, line: str, direction: str, num: int) -> list[str]:
        return registry.llm_adapters[self.llm_provider].rewrite_line(line, direction, num)
