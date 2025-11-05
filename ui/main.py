import os

import gradio as gr
import requests

from app.config import settings

# State to track database creation
db_created = gr.State(False)
db_status_msg = gr.State([])
rag_agent = None
thread_id = None

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

def fetch_uploaded_files():
    url = f"{settings.api_base_url}/kb/list"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def check_kb():
    url = f"{settings.api_base_url}/kb/check"
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

def upload_files(files):
    if not files:
        return None, gr.update(value="No files uploaded.")

    url = f"{settings.api_base_url}/kb/upload"
    files_payload = []
    for file in files:
        if hasattr(file, "name") and hasattr(file, "read"):
            # file-like object
            files_payload.append(("files", (file.name, file.read(), "application/octet-stream")))
        else:
            # file path
            with open(file, "rb") as f:
                files_payload.append(("files", (os.path.basename(file), f.read(), "application/octet-stream")))

    response = requests.post(url, files=files_payload)
    response.raise_for_status()

    # display uploaded files
    uploaded_files = fetch_uploaded_files()
    uploaded_files_msg = "\n".join(f"{file['name']} ({file['size'] / 1024:.2f} KB)" for file in uploaded_files)

    return uploaded_files_msg, response.json().get("message")

def create_kb():
    url = f"{settings.api_base_url}/kb/new"
    response = requests.post(url)
    response.raise_for_status()

    return response.json().get("message", "Knowledge base created.")

def start_chat_session():
    url = f"{settings.api_base_url}/rag/start"
    response = requests.get(url)
    response.raise_for_status()
    global thread_id
    thread_id = response.text

    status_message = f"Chat session {response.text} started. You can now ask questions based on the uploaded documents."
    db_status_msg.value.append(status_message)
    return gr.update(value="\n".join(db_status_msg.value))

def query_llm(user_input, history):
    payload = {
        "kb_name": settings.kb_name,
        "conversation_id": thread_id,
        "user_input": user_input
    }
    url = f"{settings.api_base_url}/rag/chat"
    response = requests.post(url, json=payload)
    response.raise_for_status()

    return response.json()


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

demo.launch(debug=True)
