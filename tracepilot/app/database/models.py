from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from pgvector.sqlalchemy import Vector
from app.database.session import Base

class Service(Base):
    __tablename__ = "services"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    team = Column(String)
    environment = Column(String)
    repository = Column(String)
    owner = Column(String)
    dependencies = Column(JSON) # List of service ids
    criticality = Column(String)

class Deployment(Base):
    __tablename__ = "deployments"

    id = Column(String, primary_key=True)
    service_id = Column(String, ForeignKey("services.id"), index=True)
    version = Column(String)
    commit_sha = Column(String)
    deployed_at = Column(DateTime(timezone=True), default=func.now(), index=True)
    deployed_by = Column(String)
    environment = Column(String)
    status = Column(String)
    change_summary = Column(String)

class Log(Base):
    __tablename__ = "logs"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime(timezone=True), index=True)
    service = Column(String, index=True)
    level = Column(String)
    message = Column(String)
    trace_id = Column(String, index=True)
    request_id = Column(String)
    metadata_ = Column("metadata", JSON)

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(String, primary_key=True)
    timestamp = Column(DateTime(timezone=True), index=True)
    service = Column(String, index=True)
    metric_name = Column(String, index=True)
    value = Column(Float)
    labels = Column(JSON)

class Incident(Base):
    __tablename__ = "incidents"

    id = Column(String, primary_key=True)
    title = Column(String)
    severity = Column(String)
    started_at = Column(DateTime(timezone=True))
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    affected_service = Column(String)
    root_cause = Column(String)
    resolution = Column(String)
    summary = Column(String)

class Document(Base):
    __tablename__ = "documents"

    id = Column(String, primary_key=True)
    title = Column(String)
    document_type = Column(String)
    content = Column(String)
    source = Column(String)
    metadata_ = Column("metadata", JSON)
    embedding = Column(Vector(1536)) # text-embedding-3-small uses 1536 dimensions
