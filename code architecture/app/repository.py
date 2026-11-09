
from app.models import BugReport


class BugRepository:
    def __init__(self, db):
        self.db = db

    def create(self, bug):
        self.db.add(bug)
        self.db.commit()
        self.db.refresh(bug)
        return bug

    def get_all(self):
        return self.db.query(BugReport).order_by(
            BugReport.id.desc()
        ).all()

    def get_by_id(self, bug_id):
        return self.db.query(BugReport).filter(
            BugReport.id == bug_id
        ).first()

    def update(self, bug):
        self.db.commit()
        self.db.refresh(bug)
        return bug




