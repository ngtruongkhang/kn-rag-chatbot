from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings(BaseModel):
    project_path: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Model settings
    llm_model: str = os.getenv("LLM_MODEL")
    embedding_model: str = os.getenv("EMBEDDING_MODEL")

    # KB
    kb_name: str = os.getenv("KB_NAME", "default_kb")

    # Server settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    api_base_url: str = f"http://{host}:{port}/api"
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    @property
    def cors_origins_list(self):
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()
