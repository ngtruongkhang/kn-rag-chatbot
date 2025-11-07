from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool
from langgraph.checkpoint.memory import MemorySaver


from app.config import settings
from app.service.kb_service import KBService


class RagService:
    def __init__(self):
        self.model = init_chat_model("google_genai:" + settings.llm_model,
                                     google_api_key=settings.google_api_key)
        self.agent = None

    def create_rag_agent(self):
        if not self.agent:
            tools = [self.retrieve_context]
            # If desired, specify custom instructions
            system_prompt = ("You can use the `retrieve_context` tool to find relevant information from documents. "
                             "Always use this tool to retrieve context if the intent of query is about 'DLA', policies, scholarships, or tuition fees. ")

            self.agent = create_agent(self.model, tools, system_prompt=system_prompt, checkpointer=MemorySaver())

        return self.agent

    @staticmethod
    @tool
    def retrieve_context(query: str):
        """Retrieve information to help answer a query."""
        kb_service = KBService(settings.kb_name)
        vector_db = kb_service.get_vector_db()
        retrieved_docs = vector_db.similarity_search(query)
        serialized = "\n\n".join(
            f"Source: {doc.metadata}\nContent: {doc.page_content}"
            for doc in retrieved_docs
        )
        return serialized, retrieved_docs