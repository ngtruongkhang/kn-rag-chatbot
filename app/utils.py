import os
import uuid
from typing import List

from app.config import settings


def fetch_uploaded_files():
    raw_dir = os.path.join(settings.project_path, "db", "raw")
    files = []
    if os.path.exists(raw_dir):
        for filename in os.listdir(raw_dir):
            file_path = os.path.join(raw_dir, filename)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                files.append({"name": filename, "size": size})
    return files

def create_new_uuid() -> str:
    return str(uuid.uuid4())