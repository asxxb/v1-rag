from typing import List, Optional, Any, Dict
from pydantic import BaseModel

class Evidence(BaseModel):
    evidence_id: str
    source_type: str
    source_name: str
    source_reference: str
    excerpt: str
    relevance: str

class TimelineEvent(BaseModel):
    timestamp: str
    event: str

class InvestigationResult(BaseModel):
    incident_summary: str
    affected_services: List[str]
    timeline: List[TimelineEvent]
    observations: List[str]
    hypotheses: List[str]
    likely_root_cause: str
    confidence: str
    evidence: List[Evidence]
    recommended_next_step: str
    limitations: str
    trace_id: str
    latency_ms: int

class InvestigateRequest(BaseModel):
    query: str
