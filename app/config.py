from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings(BaseModel):
    project_path: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    # Server settings
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", 8000))
    cors_origins: str = os.getenv("CORS_ORIGINS", "http://localhost:3000")
    @property
    def cors_origins_list(self):
        """Convert comma-separated CORS origins to list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]

settings = Settings()
