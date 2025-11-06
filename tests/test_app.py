from app.config import settings
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime

from app.service.kb_service import KBService

files = [settings.project_path + "/db/Chinh_sach_hoc_bong_va_ho_tro.md",
         settings.project_path + "/db/Hoc_phi.md",
         settings.project_path + "/db/Tai_sao_chon_DLA.md"]

@tool
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    kb_service = KBService(settings.kb_name)
    vector_db = kb_service.get_vector_db()
    retrieved_docs = vector_db.similarity_search(query, k=2)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs

# vector_db, titles = create_vector_db_from_files(files)
model = init_chat_model("google_genai:gemini-2.5-flash-lite")
tools = [retrieve_context]
# If desired, specify custom instructions
system_prompt = ("You can use the `retrieve_context` tool to find relevant information from documents. Always use this tool to retrieve context before answering user queries.")
rag_agent = create_agent(model, tools, system_prompt=system_prompt)
response = rag_agent.invoke({"messages": [{"role": "user", "content": "Tại sao chọn DLA?"}]})
print(response)