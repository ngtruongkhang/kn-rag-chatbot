import os
import shutil

from app.config import settings
from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma


class KBService:
    def __init__(self, kb_name: str):
        self.kb_name = kb_name
        self.raw_dir = os.path.join(settings.project_path, "db", "raw")
        self.kb_dir = os.path.join(settings.project_path, "db", "chroma_" + kb_name)


    async def create_new_knowledge_base(self):
        """Create a new knowledge base from all uploaded files"""
        self.reset_kb()
        docs = self._load_markdown_documents()
        doc_splits = self._split_documents(docs)
        vector_store = self._storing_documents(doc_splits)
        return vector_store


    def _load_markdown_documents(self):
        documents = []
        if os.path.exists(self.raw_dir):
            for filename in os.listdir(self.raw_dir):
                file_path = os.path.join(self.raw_dir, filename)
                loader = UnstructuredMarkdownLoader(file_path, mode="single", strategy="fast")
                documents.extend(loader.load())

        return documents

    def _split_documents(self, documents):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,  # chunk size (characters)
            chunk_overlap=150,  # chunk overlap (characters)
            add_start_index=True,  # track index in original document
        )
        all_splits = text_splitter.split_documents(documents)

        return all_splits

    def _storing_documents(self, doc_splits):
        vector_store = self.get_vector_db()
        vector_store.add_documents(documents=doc_splits)
        return vector_store

    def get_vector_db(self):
        embeddings = GoogleGenerativeAIEmbeddings(model=f"models/{settings.embedding_model}")
        # vector store Chroma
        vector_store = Chroma(
            collection_name=self.kb_name,
            embedding_function=embeddings,
            persist_directory=self.kb_dir
        )
        return vector_store

    def is_vector_store_not_empty(self):
        if not os.path.exists(self.kb_dir):
            return False
        vector_store = self.get_vector_db()
        return len(vector_store.get()['ids']) > 0

    def reset_kb(self):
        """Reset the knowledge base by deleting raw files and vector store"""
        if os.path.exists(self.kb_dir):
            shutil.rmtree(self.kb_dir)
        os.makedirs(self.kb_dir, exist_ok=True)