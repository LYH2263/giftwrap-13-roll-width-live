from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import papers as repo

router = APIRouter()

class PaperUpdate(BaseModel):
    roll_width: float

@router.get("/papers")
def list_papers():
    return {"items": repo.list_papers()}

@router.put("/papers/{pid}")
def update_paper(pid: int, body: PaperUpdate):
    if body.roll_width <= 0:
        raise HTTPException(422, "卷宽必须为正数")
    paper = repo.update_roll_width(pid, body.roll_width)
    if not paper:
        raise HTTPException(404)
    return paper
