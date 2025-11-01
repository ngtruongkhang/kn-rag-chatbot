from pydantic import BaseModel
import os
from dotenv import load_dotenv

load_dotenv(override=True)

class Settings(BaseModel):
    project_path: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

settings = Settings()
