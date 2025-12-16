"""Configuration for VoxEngine."""

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    llm_provider: str = "ollama"      # "ollama" | "llama_cpp"
    tts_provider: str = "cosyvoice"   # "cosyvoice" | "piper"
    cache_dir: str = ".voxengine_cache"

    class Config:
        env_prefix = "VOXENGINE_"

settings = Settings()
