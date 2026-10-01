from app.retrieval.chunking import chunk_text

def test_chunk_text():
    text = "A" * 1000
    chunks = chunk_text(text, chunk_size=500, overlap=50)
    assert len(chunks) == 3
    assert len(chunks[0]) == 500
    assert len(chunks[1]) == 500
    assert len(chunks[2]) == 100
