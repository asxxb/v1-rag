import os
import uuid
from app.database.session import engine
from sqlalchemy.orm import sessionmaker
from app.retrieval.vector_store import VectorStore
from app.retrieval.chunking import chunk_document

def ingest_documents():
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    vector_store = VectorStore(db)
    
    # Clean existing documents
    from app.database.models import Document
    db.query(Document).delete()
    db.commit()
    
    # Synthetic Documents
    raw_documents = [
        {
            "id": "runbook-checkout-1",
            "title": "Checkout API Runbook",
            "document_type": "runbook",
            "source": "data/runbooks/checkout-api.md",
            "content": "# Checkout API Runbook\n\n## Known Failure Modes\n\n### PaymentClientTimeout\nIf 5xx errors increase on checkout-api and logs show 'PaymentClientTimeout', this means the API is dropping connections to payment-service because payment-service is taking too long to respond. Check if the timeout configuration in deployment environment was changed. Safe fallback is 500ms.",
        },
        {
            "id": "postmortem-inc-1234",
            "title": "Postmortem INC-1234",
            "document_type": "postmortem",
            "source": "data/postmortems/inc-1234.md",
            "content": "# Postmortem INC-1234: Checkout Failures\n\nRoot Cause: Aggressive timeout configuration on PaymentClient (100ms) caused false timeouts when payment gateway latency spiked. The checkout API returned 5xx for these requests. Resolution was to revert the timeout configuration to 500ms.",
        },
        {
            "id": "architecture-checkout",
            "title": "Checkout Architecture",
            "document_type": "architecture",
            "source": "data/architecture/checkout.md",
            "content": "The Checkout API is the main entry point for user orders. It depends on `payment-service` to authorize payments and `user-service` to validate user details. Critical path latency must be under 1000ms.",
        }
    ]
    
    documents_to_insert = []
    for doc in raw_documents:
        chunks = chunk_document(doc["id"], doc["title"], doc["content"])
        for chunk in chunks:
            documents_to_insert.append({
                "id": chunk["chunk_id"],
                "title": chunk["title"],
                "document_type": doc["document_type"],
                "source": doc["source"],
                "content": chunk["text"],
                "metadata": {"chunk_index": chunk["chunk_index"]}
            })
            
    vector_store.add_documents(documents_to_insert)
    print(f"Ingested {len(documents_to_insert)} document chunks.")

if __name__ == "__main__":
    ingest_documents()
