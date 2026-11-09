from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import (
    BugCreate,
    BugResponse,
    BugStatusUpdate,
    BugAssignmentUpdate
)
from app.service import BugService


router = APIRouter(
    prefix="/bugs",
    tags=["Bug Management"]
)


@router.post("/", response_model=BugResponse, status_code=201)
def create_bug(data: BugCreate, db: Session = Depends(get_db)):
    return BugService(db).create_bug(data)


@router.get("/", response_model=list[BugResponse])
def get_all_bugs(db: Session = Depends(get_db)):
    return BugService(db).get_all_bugs()


@router.get("/{bug_id}", response_model=BugResponse)
def get_bug(bug_id: int, db: Session = Depends(get_db)):
    try:
        return BugService(db).get_bug(bug_id)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.patch("/{bug_id}/status", response_model=BugResponse)
def update_status(
    bug_id: int,
    data: BugStatusUpdate,
    db: Session = Depends(get_db)
):
    try:
        return BugService(db).update_status(bug_id, data.status)
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.patch("/{bug_id}/assignment", response_model=BugResponse)
def assign_bug(
    bug_id: int,
    data: BugAssignmentUpdate,
    db: Session = Depends(get_db)
):
    try:
        return BugService(db).assign_bug(
            bug_id, data.assigned_to
        )
    except ValueError as error:
        raise HTTPException(status_code=404, detail=str(error))
    
    
    