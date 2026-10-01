from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.retrieval.vector_store import VectorStore

def search_runbooks(db: Session, query: str, service: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search for relevant runbooks using vector similarity."""
    vs = VectorStore(db)
    # The query might specify the service, but we'll let vector search handle the text. 
    # Can also append service name to query for better matching.
    if service:
        query = f"service {service} {query}"
        
    return vs.similarity_search(query=query, document_type="runbook", top_k=3)
