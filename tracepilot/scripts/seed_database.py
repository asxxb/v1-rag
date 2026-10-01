import os
from datetime import datetime, timedelta, timezone
import uuid
from sqlalchemy import text
from app.database.session import engine, Base
from app.database.models import Service, Deployment, Log, Metric, Incident, Document

def init_db():
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

def seed_data():
    from sqlalchemy.orm import sessionmaker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    # 1. Services
    services = [
        Service(id="checkout-api", name="Checkout API", team="checkout", environment="prod", repository="checkout-api", owner="checkout-team", dependencies=["payment-service", "user-service"], criticality="high"),
        Service(id="payment-service", name="Payment Service", team="payments", environment="prod", repository="payment-service", owner="payments-team", dependencies=[], criticality="high"),
        Service(id="order-service", name="Order Service", team="orders", environment="prod", repository="order-service", owner="orders-team", dependencies=["inventory-service"], criticality="high"),
        Service(id="inventory-service", name="Inventory Service", team="inventory", environment="prod", repository="inventory-service", owner="inventory-team", dependencies=[], criticality="medium"),
        Service(id="user-service", name="User Service", team="users", environment="prod", repository="user-service", owner="users-team", dependencies=[], criticality="high"),
        Service(id="notification-service", name="Notification Service", team="platform", environment="prod", repository="notification-service", owner="platform-team", dependencies=[], criticality="low"),
        Service(id="recommendation-service", name="Recommendation Service", team="data", environment="prod", repository="recommendation-service", owner="data-team", dependencies=[], criticality="low"),
        Service(id="api-gateway", name="API Gateway", team="platform", environment="prod", repository="api-gateway", owner="platform-team", dependencies=["checkout-api", "order-service", "user-service", "recommendation-service"], criticality="high")
    ]
    db.add_all(services)
    
    # 2. Deployments
    now = datetime.now(timezone.utc)
    deploy_time = now - timedelta(hours=2) # The problematic deployment happened 2 hours ago
    deployments = [
        Deployment(id="d-8471", service_id="checkout-api", version="v2.8.0", commit_sha="abc1234", deployed_at=now - timedelta(days=2), deployed_by="auto", environment="prod", status="success", change_summary="Minor bug fixes"),
        Deployment(id="d-8472", service_id="checkout-api", version="v2.8.1", commit_sha="def5678", deployed_at=deploy_time, deployed_by="jdoe", environment="prod", status="success", change_summary="Update PaymentClient timeout configuration"),
        Deployment(id="d-payment-1", service_id="payment-service", version="v1.5.0", commit_sha="123abcd", deployed_at=now - timedelta(days=5), deployed_by="auto", environment="prod", status="success", change_summary="Security patch"),
    ]
    db.add_all(deployments)

    # 3. Logs & Metrics
    # Generate background normal metrics
    metrics = []
    logs = []
    
    for i in range(24): # Last 24 hours (1 hour intervals)
        t = now - timedelta(hours=24-i)
        
        # Payment service latency
        p_latency = 50.0 if t < deploy_time else 250.0
        metrics.append(Metric(id=str(uuid.uuid4()), timestamp=t, service="payment-service", metric_name="latency_ms", value=p_latency, labels={}))
        
        # Checkout API errors
        err_rate = 1.1 if t < deploy_time else 11.8
        metrics.append(Metric(id=str(uuid.uuid4()), timestamp=t, service="checkout-api", metric_name="error_rate_percent", value=err_rate, labels={"status": "5xx"}))
        
        # Logs
        if t >= deploy_time:
            logs.append(Log(id=str(uuid.uuid4()), timestamp=t, service="checkout-api", level="ERROR", message="PaymentClientTimeout: request exceeded 100ms", trace_id=f"trace-{i}", request_id=f"req-{i}", metadata_={"client": "PaymentClient"}))
        else:
            logs.append(Log(id=str(uuid.uuid4()), timestamp=t, service="checkout-api", level="INFO", message="Checkout successful", trace_id=f"trace-{i}", request_id=f"req-{i}", metadata_={}))

    db.add_all(metrics)
    db.add_all(logs)

    # 4. Incidents (Historical)
    incidents = [
        Incident(id="INC-1234", title="Payment Gateway Timeout leading to Checkout Failures", severity="SEV-2", started_at=now - timedelta(days=60), resolved_at=now - timedelta(days=60, hours=-1), affected_service="checkout-api", root_cause="Aggressive timeout configuration on PaymentClient caused false timeouts when payment gateway latency spiked.", resolution="Reverted timeout config to 500ms.", summary="We saw an increase in 5xx on checkout due to PaymentClientTimeout.")
    ]
    db.add_all(incidents)

    db.commit()
    db.close()
    print("Database seeded successfully.")

if __name__ == "__main__":
    init_db()
    seed_data()
