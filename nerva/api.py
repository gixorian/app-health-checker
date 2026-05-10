from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import exists
from sqlalchemy.orm import Session
from nerva.database import SessionLocal, engine, Base
from nerva.models import TaskDefinition, TaskRecord
from nerva.engine import nerva_worker
from typing import List
from nerva.schemas import TaskSchema, TriggerRequest
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nerva Engine API")


def parse_flexible_datetime(dt_str: str):
    """
    Handles:
    '2024-05-01' -> Start of day
    '2024-05-01 14:30' -> Exact minute
    '2024-05-01T14:30:00' -> ISO format
    """

    dt_str = dt_str.replace("T", " ").replace(":", "-").replace("_", " ")

    formats = ["%Y-%m-%d", "%Y-%m-%d %H-%M", "%Y-%m-%d %H-%M-%S"]

    for fmt in formats:
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            continue

    raise ValueError(
        f"Invalid date format: {dt_str}. Use YYYY-MM-DD or YYYY-MM-DD HH:MM"
    )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health_check():
    return {"status": "ok", "service": "Nerva Engine"}


@app.get("/status/{task_id}", response_model=TaskSchema)
def get_task_status(task_id: int, db: Session = Depends(get_db)):
    task = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return task


@app.get("/history", response_model=List[TaskSchema])
def get_all_tasks(
    limit: int = 10,
    status: str | None = None,
    after: str | None = None,
    before: str | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(TaskRecord)

    if after:
        after_dt = parse_flexible_datetime(after)
        query = query.filter(TaskRecord.created_at >= after_dt)

    if before:
        before_dt = parse_flexible_datetime(before)
        query = query.filter(TaskRecord.created_at <= before_dt)

    query = query.order_by(TaskRecord.id.desc())

    if status is not None:
        query = query.filter(TaskRecord.status == status)

    if limit != -1:
        query = query.limit(limit)

    return query.all()


@app.post("/trigger")
def trigger_task(data: TriggerRequest, db: Session = Depends(get_db)):
    task = TaskRecord(task_type=data.task_name.upper(), payload=data.params)

    db.add(task)
    db.commit()
    db.refresh(task)

    nerva_worker.delay(task.id)  # type: ignore

    return {
        "message": f"Task {data.task_name} queued",
        "id": task.id,
        "params_received": data.params,
    }


@app.get("/tasks/definitions")
def get_task_definitions(db: Session = Depends(get_db)):
    return db.query(TaskDefinition).all()


@app.post("/tasks/register")
def register_task_definition(definition: dict, db: Session = Depends(get_db)):
    existing = (
        db.query(TaskDefinition)
        .filter(TaskDefinition.name == definition["name"])
        .first()
    )

    if existing:
        existing.entrypoint = definition["entrypoint"]
        existing.params_schema = definition["params_schema"]
    else:
        new_def = TaskDefinition(**definition)
        db.add(new_def)

    db.commit()
    return {"status": "registered", "task": definition["name"]}
