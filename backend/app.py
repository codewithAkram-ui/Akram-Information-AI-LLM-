"""
AkramAI — Flask API Server
Personal AI Knowledge Assistant powered by RAG + Grok API
"""

import os
import sys
from dotenv import load_dotenv

# Load .env file from the backend directory
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
load_dotenv(env_path, override=True)
print(f"📋 Loaded .env from: {env_path}")
print(f"🔑 GROK_API_KEY: {'✅ Found' if os.getenv('GROK_API_KEY') else '❌ Not found'}")
import time
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

from pdf_processor import process_pdf
from vector_store import VectorStore
from generator import GrokGenerator

app = Flask(__name__, static_folder="../frontend/dist", static_url_path="")
CORS(app)

# Global instances
vector_store = None
generator = None
is_ready = False
startup_error = None


def initialize():
    """Initialize the RAG pipeline on startup."""
    global vector_store, generator, is_ready, startup_error

    try:
        print("=" * 60)
        print("🚀 AkramAI — Personal Knowledge Assistant")
        print("=" * 60)

        # 1. Initialize vector store (with GPU if available)
        print("\n📦 Step 1: Loading embedding model...")
        vector_store = VectorStore()

        # 2. Check for saved index
        index_dir = os.path.join(os.path.dirname(__file__), "data", "index")
        pdf_path = os.path.join(os.path.dirname(__file__), "data", "report.pdf")

        # Check if PDF is newer than the cached index
        index_pkl = os.path.join(index_dir, "chunks.pkl")
        needs_rebuild = False
        if os.path.exists(index_pkl):
            if os.path.getmtime(pdf_path) > os.path.getmtime(index_pkl):
                print("🔄 PDF has been updated! Rebuilding index...")
                needs_rebuild = True

        if not needs_rebuild and vector_store.load(index_dir):
            print("⚡ Loaded existing index from disk — fast startup!")
        else:
            print("📄 Extracting text from:", pdf_path)
            chunks = process_pdf(pdf_path)
            
            print(f"🔢 Building vector index...")
            vector_store.build_index(chunks)
            
            # Save for next time
            vector_store.save(index_dir)

        # 3. Initialize Grok generator
        print("\n🤖 Step 4: Connecting to Grok API...")
        generator = GrokGenerator()

        is_ready = True
        print("\n" + "=" * 60)
        print("✅ AkramAI is READY!")
        print(f"🌐 Frontend: http://localhost:5000")
        print(f"📡 API: http://localhost:5000/api/ask")
        print("=" * 60 + "\n")

    except Exception as e:
        startup_error = str(e)
        print(f"\n❌ Startup error: {e}")
        print("The server will still start, but queries won't work until the error is fixed.")


# ─── Routes ───────────────────────────────────────────────

@app.route("/")
def serve_frontend():
    """Serve the frontend."""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/api/health")
def health():
    """Health check endpoint."""
    return jsonify({
        "status": "ready" if is_ready else "initializing",
        "error": startup_error,
        "gpu": "cuda" if vector_store and vector_store.device == "cuda" else "cpu",
        "chunks_indexed": vector_store.index.ntotal if vector_store and vector_store.index else 0
    })


@app.route("/api/ask", methods=["POST"])
def ask():
    """Main Q&A endpoint."""
    if not is_ready:
        return jsonify({
            "error": startup_error or "System is still initializing. Please wait...",
            "answer": None
        }), 503

    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "Please provide a question.", "answer": None}), 400

    try:
        start_time = time.time()

        # Step 1: Search for relevant chunks
        # Retrieve 6 chunks to avoid hitting Groq's strict 6000 tokens-per-minute limit
        results = vector_store.search(question, top_k=6)

        # Step 2: Generate answer with Grok
        response = generator.generate_answer(question, results)

        elapsed = round(time.time() - start_time, 2)

        return jsonify({
            "answer": response["answer"],
            "confidence": response["confidence"],
            "sources_used": response["sources_used"],
            "model": response["model"],
            "response_time": elapsed,
            "error": None
        })

    except Exception as e:
        return jsonify({
            "error": f"Error processing question: {str(e)}",
            "answer": None
        }), 500


@app.route("/api/reindex", methods=["POST"])
def reindex():
    """Re-index the PDF (useful if PDF is updated)."""
    global is_ready

    try:
        is_ready = False
        pdf_path = os.path.join(os.path.dirname(__file__), "data", "report.pdf")
        index_dir = os.path.join(os.path.dirname(__file__), "data", "index")

        chunks = process_pdf(pdf_path)
        vector_store.build_index(chunks)
        vector_store.save(index_dir)

        is_ready = True
        return jsonify({"status": "success", "chunks": len(chunks)})

    except Exception as e:
        is_ready = True
        return jsonify({"error": str(e)}), 500


# ─── Startup ──────────────────────────────────────────────

if __name__ == "__main__":
    initialize()
    app.run(host="0.0.0.0", port=5000, debug=False)
