import gradio as gr

from app.document import create_vector_db_from_files, get_vector_db
from app.config import settings
from langchain.agents import create_agent
from langchain.chat_models import init_chat_model
from langchain.tools import tool, ToolRuntime
from langchain_chroma import Chroma

# State to track database creation
db_created = gr.State(False)
db_titles = gr.State([])
vector_db: Chroma
rag_agent = None


# UI callbacks
def process_files(files):
    if not files:
        files = [settings.project_path + "/db/Chinh_sach_hoc_bong_va_ho_tro.md",
                 settings.project_path + "/db/Hoc_phi.md",
                 settings.project_path + "/db/Tai_sao_chon_DLA.md"]

    global vector_db
    vector_db, titles = create_vector_db_from_files(files)
    print(vector_db)

    db_created.value = True
    db_titles.value = titles
    status_message = "Database created.\nFiles:\n  " + "\n  ".join(titles)
    return gr.update(value=status_message), titles

def start_chat_session():
    if not db_created.value:
        status_message = "\nDatabase not created. Please upload files and create the database first."
        return gr.update(value=status_message)


    status_message = "\nChat session started. You can now ask questions based on the uploaded documents."
    return gr.update(value=status_message)

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


def chat(user_input, history):
    # Replace with actual chat logic
    if not db_created.value:
        return "Chat cannot be started. Database not created." if not db_created.value else f"Echo: {user_input}"

    rag_agent = get_rag_agent()

    response = rag_agent.invoke({"messages": [{"role": "user", "content": user_input}]})
    return response["messages"][-1].content


def get_rag_agent():
    global rag_agent

    if rag_agent is None:
        model = init_chat_model("google_genai:gemini-2.5-flash-lite")
        tools = [retrieve_context]
        # If desired, specify custom instructions
        system_prompt = ("You can use the `retrieve_context` tool to find relevant information from documents. Always use this tool to retrieve context before answering user queries.")
        rag_agent = create_agent(model, tools, system_prompt=system_prompt)

    return rag_agent

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Database")
            file_upload = gr.File(label="Upload Markdown Files", file_count="multiple", file_types=[".md"])
            submit_btn = gr.Button("Create database")
            db_status = gr.Textbox(label="Status", interactive=False, lines=10)
            chat_btn = gr.Button("Start chat session")
        with gr.Column(scale=1):
            gr.Markdown("## Chat")
            chatbot = gr.ChatInterface(chat)

    submit_btn.click(
        process_files,
        inputs=[file_upload],
        outputs=[db_status, db_titles]
    )
    chat_btn.click(
        start_chat_session,
        outputs=[db_status]
    )

demo.launch(debug=True)
