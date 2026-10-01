from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.retrieval.vector_store import VectorStore

def search_incidents(db: Session, query: str, service: Optional[str] = None) -> List[Dict[str, Any]]:
    """Search for relevant past incidents and postmortems."""
    vs = VectorStore(db)
    if service:
        query = f"service {service} {query}"
        
    return vs.similarity_search(query=query, document_type="postmortem", top_k=3)
