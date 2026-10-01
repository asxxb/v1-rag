from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from app.api.schemas import Evidence, TimelineEvent, InvestigationResult

class InvestigationState(BaseModel):
    incident_description: str
    discovered_services: List[str] = Field(default_factory=list)
    tool_calls: List[Dict[str, Any]] = Field(default_factory=list)
    observations: List[str] = Field(default_factory=list)
    evidence: List[Evidence] = Field(default_factory=list)
    hypotheses: List[str] = Field(default_factory=list)
    timeline: List[TimelineEvent] = Field(default_factory=list)
    final_conclusion: Optional[str] = None
    confidence: Optional[str] = None
    recommended_next_step: Optional[str] = None
    iterations: int = 0
