from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class BugCategory(str, Enum):
    ui = "ui"
    backend = "backend"
    database = "database"
    security = "security"
    performance = "performance"
    other = "other"


class Severity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class Priority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class BugStatus(str, Enum):
    open = "open"
    in_progress = "in_progress"
    resolved = "resolved"
    closed = "closed"


class BugCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10)
    reported_by: str = Field(min_length=2, max_length=100)


class BugStatusUpdate(BaseModel):
    status: BugStatus


class BugAssignmentUpdate(BaseModel):
    assigned_to: str = Field(min_length=2, max_length=100)


class BugResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    category: BugCategory
    severity: Severity
    priority: Priority
    status: BugStatus
    reported_by: str
    assigned_to: str | None
    ai_summary: str | None
    ai_provider: str
    
    
    
    