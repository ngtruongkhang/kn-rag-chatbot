import os
import shutil
from typing import List

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma

from app.config import settings


def create_vector_db_from_files(files: List):
    docs, titles = load_markdown_documents(files)
    doc_splits = split_documents(docs)
    vector_store = storing_documents(doc_splits)
    return vector_store, titles


def load_markdown_documents(files: List):
    documents = []
    titles = []
    for file in files:
        # Handle both file-like objects and file paths
        if hasattr(file, 'name'):
            file_path = file.name
        else:
            file_path = str(file)

        loader = UnstructuredMarkdownLoader(file, mode="single", strategy="fast")
        documents.extend(loader.load())
        titles.append(os.path.basename(file_path))

    return documents, titles

def split_documents(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,  # chunk size (characters)
        chunk_overlap=200,  # chunk overlap (characters)
        add_start_index=True,  # track index in original document
    )
    all_splits = text_splitter.split_documents(documents)
    return all_splits

def storing_documents(doc_splits):
    db_dir = os.path.join(settings.project_path, "db", "chroma_langchain_db")
    if os.path.exists(db_dir):
        shutil.rmtree(db_dir)

    # vector store Chroma
    vector_store = get_vector_db()
    vector_store.add_documents(documents=doc_splits)
    return vector_store

def get_vector_db_old():
    db_dir = os.path.join(settings.project_path, "db", "chroma_langchain_db")
    # embeddings model
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")
    # vector store Chroma
    vector_store = Chroma(
        collection_name="example_collection",
        embedding_function=embeddings,
        persist_directory=db_dir
    )
    return vector_store

def is_vector_store_not_empty():
    db_dir = os.path.join(settings.project_path, "db", "chroma_langchain_db")
    if not os.path.exists(db_dir):
        return False
    vector_store = get_vector_db()
    return len(vector_store.get()['ids']) > 0