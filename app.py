import uuid

import gradio as gr

from app.document import create_vector_db_from_files, is_vector_store_not_empty
from app.config import settings

from app.service.rag_agent import RagAgent

# State to track database creation
db_created = gr.State(False)
db_status_msg = gr.State([])
rag_agent = None
thread_id = None

existing_files = ["Chinh_sach_hoc_bong_va_ho_tro.md", "Hoc_phi.md", "Tai_sao_chon_DLA.md"]

# UI callbacks
def process_files(files):
    if not files:
        files = []
        files.extend(settings.project_path + "/db/" + file for file in existing_files)

    global vector_db
    vector_db, titles = create_vector_db_from_files(files)

    db_created.value = True

    status_message = "Database created.\nFiles:\n  " + "\n  ".join(titles)
    db_status_msg.value.append(status_message)
    return gr.update(value="\n".join(db_status_msg.value))

def start_chat_session():
    if not is_vector_store_not_empty():
        status_message = "\nDatabase not created. Please upload files and create the database first."
        return gr.update(value=status_message)

    if not db_status_msg.value:
        status_message = "Use existing database. \nFiles:\n  " + "\n  ".join(existing_files)
        db_status_msg.value.append(status_message)

    global thread_id
    thread_id = make_thread_id()

    status_message = "\nChat session started. You can now ask questions based on the uploaded documents."
    db_status_msg.value.append(status_message)
    return gr.update(value="\n".join(db_status_msg.value))

def chat(user_input, history):
    if not is_vector_store_not_empty():
        return "Chat cannot be started. Database not created." if not db_created.value else f"Echo: {user_input}"
    global thread_id
    config = {"configurable": {"thread_id": thread_id}}
    rag_agent = get_rag_agent()
    response = rag_agent.invoke({"messages": [{"role": "user", "content": user_input}]}, config=config)
    return response["messages"][-1].content

def get_rag_agent():
    global rag_agent
    if rag_agent is None:
        rag = RagAgent()
        rag_agent = rag.create_rag_agent()

    return rag_agent

def make_thread_id() -> str:
    return str(uuid.uuid4())

with gr.Blocks() as demo:
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Database")
            file_upload = gr.File(label="Upload Markdown Files", file_count="multiple", file_types=[".md"])
            submit_btn = gr.Button("Create new database")
            db_status = gr.Textbox(label="Status", interactive=False, lines=5)
            chat_btn = gr.Button("Start chat session")
        with gr.Column(scale=1):
            gr.Markdown("## Chat")
            chatbot = gr.ChatInterface(chat)

    submit_btn.click(
        process_files,
        inputs=[file_upload],
        outputs=[db_status]
    )
    chat_btn.click(
        start_chat_session,
        outputs=[db_status]
    )

demo.launch(debug=True)
