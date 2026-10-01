from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import Deployment

def get_deployment_history(db: Session, service: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """Get deployment history for a service."""
    results = db.query(Deployment).filter(
        Deployment.service_id == service,
        Deployment.deployed_at >= start_time,
        Deployment.deployed_at <= end_time
    ).order_by(Deployment.deployed_at.desc()).all()
    
    return [{
        "version": r.version,
        "deployed_at": r.deployed_at.isoformat(),
        "change_summary": r.change_summary,
        "status": r.status
    } for r in results]
