from fastapi import APIRouter, HTTPException
from app.repositories import papers as repo
from app.schemas.paper import PaperUpdate
router = APIRouter()
@router.get("/papers")
def list_papers(): return {"items": repo.list_papers()}
@router.put("/papers/{pid}")
def update_paper(pid: int, body: PaperUpdate):
    r = repo.update_paper(pid, body.roll_width, body.name, body.note)
    if r is None:
        raise HTTPException(404)
    return r
