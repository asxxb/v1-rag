from app.safety.validators import validate_query_safety, redact_secrets

def test_validate_query_safety_safe():
    is_safe, msg = validate_query_safety("Checkout API is slow")
    assert is_safe
    assert msg == ""

def test_validate_query_safety_unsafe():
    is_safe, msg = validate_query_safety("Restart the database")
    assert not is_safe
    assert "forbidden" in msg

def test_redact_secrets():
    text = "Here is the api_key: \"12345ABCD\" and some other text"
    redacted = redact_secrets(text)
    assert "[REDACTED]" in redacted
    assert "12345ABCD" not in redacted
