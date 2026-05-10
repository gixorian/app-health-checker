from sqlalchemy import Column, Integer, String, JSON, DateTime
from sqlalchemy.sql import func
from .database import Base


class TaskRecord(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_type = Column(String)
    payload = Column(JSON)
    status = Column(String, default="PENDING")
    result = Column(JSON, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class TaskDefinition(Base):
    __tablename__ = "task_definitions"
    name = Column(String, primary_key=True, index=True)
    entrypoint = Column(String, nullable=False)
    params_schema = Column(JSON, nullable=True)
