import re
from typing import Tuple

def redact_secrets(text: str) -> str:
    """Basic secret redaction."""
    # Redact simple patterns
    text = re.sub(r'(api[_-]?key)\s*[:=]\s*["\']?[a-zA-Z0-9_\-]+["\']?', r'\1: [REDACTED]', text, flags=re.IGNORECASE)
    text = re.sub(r'(password)\s*[:=]\s*["\']?[^"\']+["\']?', r'\1: [REDACTED]', text, flags=re.IGNORECASE)
    text = re.sub(r'(token)\s*[:=]\s*["\']?[a-zA-Z0-9_\-\.]+["\']?', r'\1: [REDACTED]', text, flags=re.IGNORECASE)
    return text

def validate_query_safety(query: str) -> Tuple[bool, str]:
    """Check if the user query is asking for malicious actions."""
    lower_query = query.lower()
    
    forbidden_actions = ["deploy", "restart", "delete", "drop table", "rm -rf", "update configuration"]
    for action in forbidden_actions:
        if action in lower_query:
            return False, f"Action '{action}' is forbidden. TracePilot is read-only."
            
    if "api key" in lower_query and ("show" in lower_query or "what is" in lower_query or "reveal" in lower_query):
         return False, "Cannot reveal secrets."
         
    return True, ""
