from datetime import datetime, timezone

from sqlalchemy import Column, Integer, String, Text, DateTime
from app.database import Base


class BugReport(Base):
    __tablename__ = "bug_reports"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(String(50), nullable=False)
    severity = Column(String(30), nullable=False)
    priority = Column(String(30), nullable=False)
    status = Column(String(30), default="open", nullable=False)
    reported_by = Column(String(100), nullable=False)
    assigned_to = Column(String(100), nullable=True)
    ai_summary = Column(Text, nullable=True)
    ai_provider = Column(String(50), default="rule_based")
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )
    
    
    
    