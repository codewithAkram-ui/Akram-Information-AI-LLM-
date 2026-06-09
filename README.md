# AkramAI — Personal Knowledge Assistant

AkramAI is a full-stack Retrieval-Augmented Generation (RAG) web application that allows users to query information from a PDF document. It uses a Python Flask backend for processing the document and generating answers via the Grok API, alongside a modern Vue 3 frontend for an interactive user interface.

## 🚀 Features

- **PDF Processing & Indexing**: Automatically extracts and chunks text from a target PDF document (`report.pdf`).
- **Vector Search Engine**: Employs `sentence-transformers` to embed text and `FAISS` to store and efficiently search vector representations.
- **AI-Powered Answers**: Leverages the Grok API via the `openai` Python client to generate precise answers based on retrieved context.
- **Modern UI**: Built with Vue 3 and Vite for a fast and reactive user experience.
- **Deployment-Ready**: Includes a keep-alive mechanism to prevent spin-down on free-tier hosting platforms like Render.

---

## 🛠️ Technology Stack

### **Backend**
- **Framework**: Flask, Flask-CORS
- **AI & ML**: PyTorch, sentence-transformers, FAISS
- **LLM Integration**: Grok API (via `openai` client)
- **PDF Parsing**: PyPDF2

### **Frontend**
- **Framework**: Vue 3
- **Build Tool**: Vite

---

## 📁 Project Structure

```text
AkramLLM/
├── backend/
│   ├── app.py                # Main Flask application and API endpoints
│   ├── generator.py          # Grok API integration for generating answers
│   ├── pdf_processor.py      # PDF text extraction and chunking
│   ├── vector_store.py       # FAISS index management and similarity search
│   ├── requirements.txt      # Python dependencies
│   └── data/                 # Contains the source PDF (report.pdf) and FAISS index
└── frontend/
    ├── public/               # Static assets
    ├── src/                  # Vue components and application logic
    ├── package.json          # Node.js dependencies
    └── vite.config.js        # Vite configuration
```

*(Note: The `frontend_backup` directory is excluded from active development and serves as a historical reference.)*

---

## 💻 Running Locally

### Prerequisites
- Node.js (v16+)
- Python 3.9+
- A Grok API Key

### 1. Setup Backend
1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the `backend` directory and add your Grok API key:
   ```env
   GROK_API_KEY=your_api_key_here
   ```
5. Ensure your target PDF is located at `backend/data/report.pdf`.
6. Start the Flask server:
   ```bash
   python app.py
   ```
   *The backend will run on `http://localhost:5000` and automatically index the PDF upon startup.*

### 2. Setup Frontend
1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the dependencies:
   ```bash
   npm install
   ```
3. Start the development server:
   ```bash
   npm run dev
   ```
   *The frontend will be accessible at the localhost URL provided by Vite (e.g., `http://localhost:5173`).*

---

## 🌐 API Endpoints

- `GET /api/health`: Check the system readiness, GPU status, and index size.
- `POST /api/ask`: Submit a question and receive an AI-generated answer based on the PDF context. Requires a JSON body: `{"question": "your question here"}`.
- `POST /api/reindex`: Force a re-indexing of the PDF document.

---

## 💡 How it Works

1. **Initialization**: On backend startup, `app.py` checks if the FAISS index exists and is up to date with `report.pdf`. If not, it parses the PDF into chunks and builds a new vector index.
2. **Retrieval**: When a user asks a question, the question is embedded, and FAISS retrieves the most relevant chunks from the PDF.
3. **Generation**: The retrieved context and the user's question are sent to the Grok API, which synthesizes a confident and accurate answer.
