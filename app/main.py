from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.route import kb

app = FastAPI(title="RAG AI Chat API",
              version="0.0.1",
              docs_url="/docs",
              redoc_url="/redoc")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(kb.router)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to RAG Chat Backend",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=True
    )