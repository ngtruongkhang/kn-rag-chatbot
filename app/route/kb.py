import os
from typing import List

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from app.config import settings

router = APIRouter(prefix="/api", tags=["knowledge base"])

@router.post("/kb/upload", response_class=JSONResponse)
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload files for knowledge base"""
    raw_dir = os.path.join(settings.project_path, "db", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    for file in files:
        file_path = os.path.join(raw_dir, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())
    return {"message": f"{len(files)} files uploaded successfully"}

@router.get("/kb/list", response_class=JSONResponse)
async def list_files():
    """List all files in knowledge base with their sizes"""
    raw_dir = os.path.join(settings.project_path, "db", "raw")
    files = []
    if os.path.exists(raw_dir):
        for filename in os.listdir(raw_dir):
            file_path = os.path.join(raw_dir, filename)
            if os.path.isfile(file_path):
                size = os.path.getsize(file_path)
                files.append({"name": filename, "size": size})
    return {"files": files}

@router.post("/kb/new", response_class=JSONResponse)
async def create_new_knowledge_base():
    """Create a new knowledge base from all uploaded files"""
    ...