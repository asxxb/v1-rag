from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from app.api.schemas import InvestigateRequest, InvestigationResult
from app.database.session import get_db
from app.agent.agent import TracePilotAgent
from app.safety.validators import validate_query_safety, redact_secrets
import logging

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

app = FastAPI(title="TracePilot API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/investigate", response_model=InvestigationResult)
def investigate(request: InvestigateRequest, db: Session = Depends(get_db)):
    # 1. Safety Check
    is_safe, reason = validate_query_safety(request.query)
    if not is_safe:
        raise HTTPException(status_code=400, detail=f"Safety violation: {reason}")
        
    # 2. Agent Execution
    agent = TracePilotAgent(db)
    result = agent.investigate(request.query)
    
    # 3. Output Redaction
    result.incident_summary = redact_secrets(result.incident_summary)
    result.likely_root_cause = redact_secrets(result.likely_root_cause)
    for ev in result.evidence:
        ev.excerpt = redact_secrets(ev.excerpt)
        
    return result
