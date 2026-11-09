
from app.models import BugReport
from app.repository import BugRepository
from app.ai_engine import classify_bug


class BugService:
    def __init__(self, db):
        self.repository = BugRepository(db)

    def create_bug(self, data):
        result = classify_bug(data.title, data.description)

        bug = BugReport(
            title=data.title,
            description=data.description,
            category=result["category"],
            severity=result["severity"],
            priority=result["priority"],
            status="open",
            reported_by=data.reported_by,
            ai_summary=result["summary"],
            ai_provider=result["provider"]
        )
        return self.repository.create(bug)

    def get_all_bugs(self):
        return self.repository.get_all()

    def get_bug(self, bug_id):
        bug = self.repository.get_by_id(bug_id)
        if bug is None:
            raise ValueError("Bug report not found")
        return bug

    def update_status(self, bug_id, status):
        bug = self.get_bug(bug_id)
        bug.status = status.value
        return self.repository.update(bug)

    def assign_bug(self, bug_id, assigned_to):
        bug = self.get_bug(bug_id)
        bug.assigned_to = assigned_to
        return self.repository.update(bug)




