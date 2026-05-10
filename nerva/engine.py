import os
from celery import Celery
from nerva.database import SessionLocal
from nerva.models import TaskRecord, TaskDefinition
import importlib.util

redis_url = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
celery_app = Celery("nerva", broker=redis_url, backend=redis_url)


@celery_app.task(bind=True)
def nerva_worker(self, task_id: int):
    db = SessionLocal()
    try:
        task = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
        if not task:
            return f"Task {task_id} not found"

        task.status = "WORKING"  # type: ignore
        db.commit()

        task_def = (
            db.query(TaskDefinition)
            .filter(TaskDefinition.name == task.task_type)
            .first()
        )

        if task_def:
            execution_result = load_and_run(task_def.entrypoint, task.payload)

            if (
                not isinstance(execution_result, (dict, list, str, int, float, bool))
                and execution_result is not None
            ):
                execution_result = str(execution_result)

            task.result = execution_result  # type: ignore
            task.status = "COMPLETED"  # type: ignore
        else:
            task.status = "FAILED"  # type: ignore
            task.result = {  # type: ignore
                "error": f"No definition found for {task.task_type}. Did you register it?"
            }

        db.commit()
        return f"Task {task_id} finished with status: {task.status}"

    except Exception as e:
        db.rollback()
        task = db.query(TaskRecord).filter(TaskRecord.id == task_id).first()
        if task:
            task.status = "FAILED"  # type: ignore
            task.result = {"error": str(e)}  # type: ignore
            db.commit()
        raise e
    finally:
        db.close()


def load_and_run(entrypoint, payload):
    file_path, func_name = entrypoint.split(":")

    module_name = "nerva_external_task"
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load file at {file_path}")

    module = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(module)  # type: ignore

    func = getattr(module, func_name)
    return func(**payload)


# def perform_debug_sleep(payload: dict):
#    seconds = payload.get("seconds", 10)
#    time.sleep(seconds)
#    return {"message": "Sleep finished", "slept_for": seconds}


# register_task("DEBUG_SLEEP", perform_debug_sleep)
