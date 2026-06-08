"""
PDF Processor — Extracts and chunks text from report.pdf
"""

import os
import re
from PyPDF2 import PdfReader


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract all text content from a PDF file."""
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF not found at: {pdf_path}")

    reader = PdfReader(pdf_path)
    full_text = []

    for page_num, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            # Clean up the extracted text
            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
            text = text.strip()
            if text:
                full_text.append(f"[Page {page_num + 1}] {text}")

    return "\n\n".join(full_text)


def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[dict]:
    """
    Split text into overlapping chunks for better retrieval.
    
    Args:
        text: Full extracted text
        chunk_size: Number of words per chunk
        overlap: Number of overlapping words between chunks
    
    Returns:
        List of dicts with 'text', 'chunk_id', and 'word_count'
    """
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = min(start + chunk_size, len(words))
        chunk_words = words[start:end]
        chunk_text = " ".join(chunk_words)

        chunks.append({
            "text": chunk_text,
            "chunk_id": len(chunks),
            "word_count": len(chunk_words),
            "start_word": start,
            "end_word": end
        })

        # Move forward by chunk_size - overlap
        start += chunk_size - overlap

        # If remaining words are less than overlap, break
        if end >= len(words):
            break

    return chunks


def process_pdf(pdf_path: str) -> list[dict]:
    """
    Full pipeline: extract text from PDF and split into chunks.
    
    Returns:
        List of text chunks with metadata
    """
    print(f"📄 Extracting text from: {pdf_path}")
    raw_text = extract_text_from_pdf(pdf_path)

    if not raw_text.strip():
        raise ValueError("No text could be extracted from the PDF. The file might be scanned/image-based.")

    print(f"📝 Extracted {len(raw_text)} characters of text")

    chunks = chunk_text(raw_text)
    print(f"🔪 Split into {len(chunks)} chunks")

    return chunks


if __name__ == "__main__":
    # Test with report.pdf
    pdf_path = os.path.join(os.path.dirname(__file__), "data", "report.pdf")
    chunks = process_pdf(pdf_path)
    for i, chunk in enumerate(chunks[:3]):
        print(f"\n--- Chunk {i} ({chunk['word_count']} words) ---")
        print(chunk['text'][:200] + "...")
