from fastapi import APIRouter, HTTPException
from app.repositories import papers as papers_repo
from app.repositories import settings_repo
from app.schemas.settings import SettingsUpdate
router = APIRouter()
@router.get("/settings")
def settings(): return settings_repo.get_all()
@router.put("/settings")
def update_settings(body: SettingsUpdate):
    if body.selected_paper_id is not None:
        if papers_repo.get_paper(body.selected_paper_id) is None:
            raise HTTPException(404, "paper not found")
        settings_repo.set_selected_paper_id(body.selected_paper_id)
    return settings_repo.get_all()
