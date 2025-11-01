from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langgraph.checkpoint.memory import MemorySaver

from app.document import get_vector_db


class RagAgent:
    def __init__(self):
        self.model = init_chat_model("google_genai:gemini-2.5-flash")

    def create_rag_agent(self):
        tools = [retrieve_context]
        # If desired, specify custom instructions
        system_prompt = ("You can use the `retrieve_context` tool to find relevant information from documents. "
                         "Always use this tool to retrieve context if the intent of query is about 'DLA', policies, scholarships, or tuition fees. ")

        agent = create_agent(self.model, tools, system_prompt=system_prompt, checkpointer=MemorySaver())

        return agent

@tool
def retrieve_context(query: str):
    """Retrieve information to help answer a query."""
    vector_db = get_vector_db()
    retrieved_docs = vector_db.similarity_search(query, k=2)
    serialized = "\n\n".join(
        f"Source: {doc.metadata}\nContent: {doc.page_content}"
        for doc in retrieved_docs
    )
    return serialized, retrieved_docs