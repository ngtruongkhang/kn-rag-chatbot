from fastapi import APIRouter
from fastapi.responses import JSONResponse, PlainTextResponse

from app.model.RagRequest import RagRequest
from app.service.rag_service import RagService
from app.utils import create_new_uuid

router = APIRouter(prefix="/api", tags=["RAG chat"])

rag_service = RagService()

@router.post("/rag/chat", response_class=JSONResponse)
async def chat(request: RagRequest):
    """Handle RAG chat messages"""
    agent = rag_service.create_rag_agent()
    thread_id = request.conversation_id if request.conversation_id else create_new_uuid()
    config = {"configurable": {"thread_id": thread_id}}
    response = await agent.ainvoke(
        {"messages": [{"role": "user", "content": request.user_input}]},
        config=config,
    )
    return response["messages"][-1]

@router.get("/rag/start", response_class=PlainTextResponse)
async def start_new_session():
    """Start a new RAG chat session"""
    return create_new_uuid()


