from typing import List
from app.config import settings

class MockEmbeddings:
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        # text-embedding-3-small uses 1536 dimensions
        # return a deterministic but pseudo-random vector based on text length for mock purposes
        return [[(len(text) % 100) / 100.0] * 1536 for text in texts]
    
    def embed_query(self, text: str) -> List[float]:
        return [(len(text) % 100) / 100.0] * 1536

def get_embedding_model():
    if not settings.llm_api_key or settings.llm_api_key == "your_api_key_here":
        return MockEmbeddings()
    
    from openai import OpenAI
    client = OpenAI(api_key=settings.llm_api_key, base_url=settings.llm_base_url)
    
    class OpenAIEmbeddings:
        def embed_documents(self, texts: List[str]) -> List[List[float]]:
            response = client.embeddings.create(input=texts, model=settings.embedding_model)
            return [data.embedding for data in response.data]
            
        def embed_query(self, text: str) -> List[float]:
            response = client.embeddings.create(input=[text], model=settings.embedding_model)
            return response.data[0].embedding
            
    return OpenAIEmbeddings()
