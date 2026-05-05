from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from nerva.database import SessionLocal, engine, Base
from nerva.models import TaskRecord
from nerva.engine import nerva_worker
from typing import List
from nerva.schemas import TaskSchema

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nerva Engine API")


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
    limit: int = 10, status: str | None = None, db: Session = Depends(get_db)
):
    query = db.query(TaskRecord).order_by(TaskRecord.created_at.desc())

    if status is not None:
        query = query.filter(TaskRecord.status == status)

    tasks = query.limit(limit).all()
    return (
        tasks
        # db.query(TaskRecord).order_by(TaskRecord.created_at.desc()).limit(limit).all()
    )


@app.post("/test-worker")
def test_worker(seconds: int = 10, db: Session = Depends(get_db)):
    task = TaskRecord(task_type="DEBUG_SLEEP", payload={"seconds": seconds})
    db.add(task)
    db.commit()
    db.refresh(task)

    nerva_worker.delay(task.id)  # type: ignore
    return {"message": f"Fake task {task.id} started for {seconds}s", "id": task.id}
