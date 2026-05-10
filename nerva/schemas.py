from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict


class TaskSchema(BaseModel):
    id: int
    status: str
    result: Optional[Any] = None
    task_type: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TriggerRequest(BaseModel):
    task_name: str
    params: Optional[Dict[str, Any]] = None
