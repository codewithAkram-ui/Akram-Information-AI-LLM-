
import os
import pickle
import numpy as np
import faiss
import torch
from sentence_transformers import SentenceTransformer


class VectorStore:
    """FAISS-based vector store with sentence-transformer embeddings."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        # Detect GPU
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        if self.device == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            print(f"🚀 NVIDIA GPU detected: {gpu_name}")
            print(f"🔥 Using GPU for embeddings — much faster!")
        else:
            print(f"💻 No NVIDIA GPU detected, using CPU for embeddings")

        print(f"📦 Loading embedding model: {model_name}...")
        self.model = SentenceTransformer(model_name, device=self.device)
        self.dimension = self.model.get_sentence_embedding_dimension()
        self.index = None
        self.chunks = []
        self.chunk_texts = []
        print(f"✅ Embedding model loaded (dimension: {self.dimension})")

    def build_index(self, chunks: list[dict]):
        """
        Build FAISS index from text chunks.
        
        Args:
            chunks: List of dicts with 'text' key
        """
        self.chunks = chunks
        self.chunk_texts = [c["text"] for c in chunks]

        print(f"🔢 Generating embeddings for {len(self.chunk_texts)} chunks on {self.device.upper()}...")

        # Generate embeddings (uses GPU if available)
        embeddings = self.model.encode(
            self.chunk_texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            batch_size=32,
            device=self.device
        )

        # Normalize embeddings for cosine similarity
        faiss.normalize_L2(embeddings)

        # Build FAISS index (Inner Product = Cosine Similarity after normalization)
        self.index = faiss.IndexFlatIP(self.dimension)
        self.index.add(embeddings.astype(np.float32))

        print(f"✅ FAISS index built with {self.index.ntotal} vectors")

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        """
        Search for most relevant chunks given a query.
        
        Args:
            query: User's question
            top_k: Number of results to return
            
        Returns:
            List of dicts with 'text', 'score', and 'chunk_id'
        """
        if self.index is None:
            raise ValueError("Index not built yet. Call build_index() first.")

        # Embed the query
        query_embedding = self.model.encode(
            [query],
            convert_to_numpy=True,
            device=self.device
        )
        faiss.normalize_L2(query_embedding)

        # Search
        scores, indices = self.index.search(query_embedding.astype(np.float32), top_k)

        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < len(self.chunks):
                results.append({
                    "text": self.chunks[idx]["text"],
                    "score": float(score),
                    "chunk_id": self.chunks[idx]["chunk_id"]
                })

        return results

    def save(self, save_dir: str):
        """Save index and chunks to disk."""
        os.makedirs(save_dir, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, os.path.join(save_dir, "faiss.index"))

        # Save chunks metadata
        with open(os.path.join(save_dir, "chunks.pkl"), "wb") as f:
            pickle.dump({"chunks": self.chunks, "chunk_texts": self.chunk_texts}, f)

        print(f"💾 Index saved to {save_dir}")

    def load(self, save_dir: str) -> bool:
        """Load index and chunks from disk. Returns True if successful."""
        index_path = os.path.join(save_dir, "faiss.index")
        chunks_path = os.path.join(save_dir, "chunks.pkl")

        if not os.path.exists(index_path) or not os.path.exists(chunks_path):
            return False

        self.index = faiss.read_index(index_path)

        with open(chunks_path, "rb") as f:
            data = pickle.load(f)
            self.chunks = data["chunks"]
            self.chunk_texts = data["chunk_texts"]

        print(f"📂 Loaded index with {self.index.ntotal} vectors")
        return True
