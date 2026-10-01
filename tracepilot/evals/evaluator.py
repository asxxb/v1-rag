import json
import os
import time
from sqlalchemy.orm import sessionmaker
from app.database.session import engine
from app.agent.agent import TracePilotAgent
from app.safety.validators import validate_query_safety
from evals.metrics import calculate_investigation_accuracy, calculate_safety_pass_rate

def run_evaluation():
    with open("evals/dataset.json") as f:
        dataset = json.load(f)
        
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    results = []
    latencies = []
    
    print("Running evaluation...")
    for case in dataset:
        print(f"Evaluating {case['id']}...")
        result = {
            "id": case["id"],
            "is_safety_case": case["is_safety_case"],
            "expected_root_cause": case["expected_root_cause"]
        }
        
        is_safe, _ = validate_query_safety(case["question"])
        if not is_safe:
            result["safety_violation_caught"] = True
            results.append(result)
            continue
            
        if case["is_safety_case"]:
            result["safety_violation_caught"] = False
            results.append(result)
            continue
            
        db = SessionLocal()
        agent = TracePilotAgent(db)
        
        start_time = time.time()
        agent_result = agent.investigate(case["question"])
        latency = time.time() - start_time
        latencies.append(latency)
        
        result["actual_root_cause"] = agent_result.likely_root_cause
        results.append(result)
        db.close()
        
    acc = calculate_investigation_accuracy(results)
    safe = calculate_safety_pass_rate(results)
    mean_latency = sum(latencies)/len(latencies) if latencies else 0
    
    report = f"""# Evaluation Summary

| Metric | Result |
| --- | --- |
| Investigation Accuracy | {acc:.1f}% |
| Safety Pass Rate | {safe:.1f}% |
| Mean Latency | {mean_latency:.2f}s |
"""
    with open("evaluation_report.md", "w") as f:
        f.write(report)
        
    with open("eval_results.json", "w") as f:
        json.dump(results, f, indent=2)
        
    print("Evaluation complete. See evaluation_report.md")

if __name__ == "__main__":
    run_evaluation()
