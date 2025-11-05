import os
from typing import List

from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse

from app.config import settings
from app.service.kb_service import KBService

router = APIRouter(prefix="/api", tags=["knowledge base"])
kb_service = KBService(settings.kb_name)

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
    return files

@router.get("/kb/check", response_class=JSONResponse)
async def check_kb():
    """Check existing files in the knowledge base"""
    return kb_service.is_vector_store_not_empty()

@router.post("/kb/new", response_class=JSONResponse)
async def create_new_knowledge_base():
    """Create a new knowledge base from all uploaded files"""
    vector_store = await kb_service.create_new_knowledge_base()
    return {"message": f"Knowledge base '{settings.kb_name}' created successfully"}