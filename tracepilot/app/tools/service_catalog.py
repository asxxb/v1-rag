from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database.models import Service

def get_service(db: Session, service: str) -> Optional[Dict[str, Any]]:
    """Get service metadata."""
    r = db.query(Service).filter(Service.id == service).first()
    if not r:
        return None
        
    return {
        "id": r.id,
        "name": r.name,
        "team": r.team,
        "owner": r.owner,
        "dependencies": r.dependencies,
        "criticality": r.criticality
    }
