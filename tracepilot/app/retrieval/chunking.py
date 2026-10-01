from typing import List, Dict

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """Simple text chunker by character count."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def chunk_document(document_id: str, title: str, text: str, chunk_size: int = 500, overlap: int = 50) -> List[Dict]:
    """Returns chunked text along with metadata."""
    chunks = chunk_text(text, chunk_size, overlap)
    return [{"chunk_id": f"{document_id}-chunk-{i}", "title": title, "text": chunk, "chunk_index": i} for i, chunk in enumerate(chunks)]
