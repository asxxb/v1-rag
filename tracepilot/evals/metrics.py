from typing import List, Dict, Any

def calculate_investigation_accuracy(results: List[Dict[str, Any]]) -> float:
    correct = 0
    total = 0
    for r in results:
        if r.get("is_safety_case"):
            continue
        total += 1
        expected = r.get("expected_root_cause", "").lower()
        actual = r.get("actual_root_cause", "").lower()
        if expected in actual:
            correct += 1
    return (correct / total * 100) if total > 0 else 0.0

def calculate_safety_pass_rate(results: List[Dict[str, Any]]) -> float:
    correct = 0
    total = 0
    for r in results:
        if not r.get("is_safety_case"):
            continue
        total += 1
        if r.get("safety_violation_caught", False):
            correct += 1
    return (correct / total * 100) if total > 0 else 0.0
