from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import Document
from app.retrieval.embeddings import get_embedding_model

class VectorStore:
    def __init__(self, db_session: Session):
        self.db = db_session
        self.embeddings = get_embedding_model()

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add chunked documents to the database with embeddings."""
        texts = [doc["content"] for doc in documents]
        vectors = self.embeddings.embed_documents(texts)
        
        db_docs = []
        for i, doc in enumerate(documents):
            db_docs.append(Document(
                id=doc["id"],
                title=doc["title"],
                document_type=doc["document_type"],
                content=doc["content"],
                source=doc["source"],
                metadata_=doc.get("metadata", {}),
                embedding=vectors[i]
            ))
        
        self.db.add_all(db_docs)
        self.db.commit()

    def similarity_search(self, query: str, document_type: Optional[str] = None, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents using pgvector."""
        query_embedding = self.embeddings.embed_query(query)
        
        # Determine filtering
        filters = []
        if document_type:
            filters.append(Document.document_type == document_type)
            
        # L2 distance search
        q = self.db.query(Document)
        if filters:
            q = q.filter(*filters)
            
        # Order by L2 distance and limit to top_k
        results = q.order_by(Document.embedding.l2_distance(query_embedding)).limit(top_k).all()
        
        return [{
            "id": r.id,
            "title": r.title,
            "document_type": r.document_type,
            "content": r.content,
            "source": r.source,
            "metadata": r.metadata_
        } for r in results]
