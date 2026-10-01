from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.database.models import Metric

def query_metrics(db: Session, service: str, metric_name: str, start_time: datetime, end_time: datetime) -> List[Dict[str, Any]]:
    """Query metrics for a service within a time range."""
    results = db.query(Metric).filter(
        Metric.service == service,
        Metric.metric_name == metric_name,
        Metric.timestamp >= start_time,
        Metric.timestamp <= end_time
    ).order_by(Metric.timestamp.asc()).all()
    
    return [{
        "timestamp": r.timestamp.isoformat(),
        "service": r.service,
        "metric_name": r.metric_name,
        "value": r.value,
        "labels": r.labels
    } for r in results]
