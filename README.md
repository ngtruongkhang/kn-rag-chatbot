# RAG Chatbot

A Retrieval-Augmented Generation (RAG) chatbot for knowledge management and question answering, built with Python. This project leverages local document storage and retrieval to provide accurate, context-aware responses.

## Features
- Upload and manage knowledge base documents (Markdown supported)
- Retrieval-Augmented Generation for answering user queries
- RESTful API endpoints for integration
- Simple UI for interaction
- Modular codebase for easy extension

## Project Structure
```
app.py                # Main application entry point
app/                  # (Backend) Core application modules
  config.py           # Configuration settings
  main.py             # App initialization
  model/              # Data models (e.g., RagRequest)
  route/              # API routes (kb, rag)
  service/            # Business logic (kb_service, rag_service)
db/                   # Knowledge base documents and Chroma DB
  raw/                # uploaded documents
ui/                   # (Frontend) User interface code
app.py                # standalone UI entry point for demo
requirements.txt      # Python dependencies
pyproject.toml        # Project metadata
README.md             # Project documentation
tests/                # Unit and integration tests
```

## Getting Started

### Prerequisites
- Python 3.12+
- pip

### Installation
1. Clone the repository:
   ```sh
   git clone <repo-url>
   cd kn-rag-chatbot
   ```
2. Install dependencies with uv:
   ```sh
   uv sync
   ```
3. Environment variables:
   - Create .env file from .env.local and set the api keys for using llm models and tracing with langsmith
   ```
   GOOGLE_API_KEY=...
   LANGSMITH_API_KEY=...
   ```

### Running the Application
You can run the backend and UI separately or together.
1. Backend and frontend separately:
   - Start the backend server:
   ```sh
   python app/main.py
   ```
   - In another terminal, start the UI:
   ```sh
   python ui/main.py
   ```
2. Backend and frontend together:
   ```sh
    python app.py
    ```
### Running Tests
Currently, no tests are available.

## Usage
- Upload documents via the API or UI
- Ask questions and receive context-aware answers
- Integrate with other systems using the REST API

## API Endpoints
- `/kb/upload` : Upload knowledge base documents
- `/rag/query` : Query the chatbot with a question

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
MIT License

## Acknowledgements
- [Gradio](https://gradio.app/) for UI components
- [ChromaDB](https://www.trychroma.com/) for vector database

