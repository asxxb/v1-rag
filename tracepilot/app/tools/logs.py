from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import Log

def query_logs(db: Session, service: str, start_time: datetime, end_time: datetime, level: Optional[str] = None, search_term: Optional[str] = None) -> List[Dict[str, Any]]:
    """Query logs for a service within a time range, optionally filtering by level and search term."""
    q = db.query(Log).filter(
        Log.service == service,
        Log.timestamp >= start_time,
        Log.timestamp <= end_time
    )
    
    if level:
        q = q.filter(Log.level == level)
        
    if search_term:
        q = q.filter(Log.message.ilike(f"%{search_term}%"))
        
    results = q.order_by(Log.timestamp.desc()).limit(100).all()
    
    return [{
        "timestamp": r.timestamp.isoformat(),
        "service": r.service,
        "level": r.level,
        "message": r.message,
        "trace_id": r.trace_id
    } for r in results]
