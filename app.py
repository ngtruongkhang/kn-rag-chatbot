import os

import gradio as gr

from app.config import settings
from app.service.kb_service import KBService
from app.service.rag_service import RagService
from app.utils import fetch_uploaded_files, create_new_uuid

# State to track database creation
db_created = gr.State(False)
db_status_msg = gr.State([])
rag_agent = None
thread_id = None

kb_service = KBService(settings.kb_name)
rag_service = RagService()

def onLoad():
    # check existing knowledge base
    kb_exists = check_kb()
    if kb_exists:
        kb_msg = "Existing knowledge base found."
    else:
        kb_msg = "No knowledge base found. Please create new."

    uploaded_files = fetch_uploaded_files()
    uploaded_files_msg = "\n".join(f"{file['name']} ({file['size'] / 1024:.2f} KB)" for file in uploaded_files)
    return uploaded_files_msg, kb_msg

def check_kb():
    return kb_service.is_vector_store_not_empty()

def upload_files(files):
    if not files:
        return None, gr.update(value="No files uploaded.")

    # save uploaded files to raw directory
    raw_dir = os.path.join(settings.project_path, "db", "raw")
    os.makedirs(raw_dir, exist_ok=True)
    for file in files:
        if hasattr(file, "name") and hasattr(file, "read"):
            # file-like object
            file_path = os.path.join(raw_dir, file.name)
            with open(file_path, "wb") as f:
                f.write(file.read())
        else:
            # file path
            file_path = os.path.join(raw_dir, os.path.basename(file))
            with open(file, "rb") as src_f, open(file_path, "wb") as dest_f:
                dest_f.write(src_f.read())

    msg = f"{len(files)} files uploaded successfully"

    # display uploaded files
    uploaded_files = fetch_uploaded_files()
    uploaded_files_msg = "\n".join(f"{file['name']} ({file['size'] / 1024:.2f} KB)" for file in uploaded_files)

    return uploaded_files_msg, msg

async def create_kb():
    await kb_service.create_new_knowledge_base()
    return f"Knowledge base '{settings.kb_name}' created successfully"

def start_chat_session():
    global thread_id
    thread_id = create_new_uuid()

    status_message = f"Chat session {thread_id} started. You can now ask questions based on the uploaded documents."
    db_status_msg.value.append(status_message)
    return gr.update(value="\n".join(db_status_msg.value))

def query_llm(user_input, history):
    agent = rag_service.create_rag_agent()
    config = {"configurable": {"thread_id": thread_id}}
    response = agent.invoke(
        {"messages": [{"role": "user", "content": user_input}]},
        config=config,
    )
    return response["messages"][-1].content


with gr.Blocks() as demo:
    with gr.Row(equal_height=True):
        with gr.Column(scale=1):
            gr.Markdown("## Knowledge Base")
            file_upload = gr.File(label="Upload Markdown Files", file_count="multiple", file_types=[".md"])
            upload_btn = gr.Button("Upload files")
            uploaded_files_status = gr.Textbox(label="Files in knowledge base:", interactive=False, lines=5)
            create_kb_btn = gr.Button("Create new knowledge base")
            kb_status = gr.Textbox(label="Status", interactive=False, lines=5)
            chat_btn = gr.Button("Start chat session")
        with gr.Column(scale=1):
            gr.Markdown("## Chat")
            chatbot = gr.ChatInterface(query_llm, type="messages", fill_height=True)

    upload_btn.click(
        upload_files,
        inputs=[file_upload],
        outputs=[uploaded_files_status, kb_status]
    )
    create_kb_btn.click(
        create_kb,
        outputs=[kb_status]
    )
    chat_btn.click(
        start_chat_session,
        outputs=[kb_status]
    )
    demo.load(
        fn=onLoad,
        outputs=[uploaded_files_status, kb_status]
    )

port = int(os.environ.get("PORT", 8080))
demo.launch(server_name="0.0.0.0", server_port=port)