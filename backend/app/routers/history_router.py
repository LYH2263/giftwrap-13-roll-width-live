from fastapi import APIRouter
from app.repositories import history as repo
from app.services import run_service
router = APIRouter()
@router.get("/runs")
def runs(limit: int = 50): return {"items": repo.list_runs(limit)}
@router.get("/runs/{rid}")
def get_run(rid: int): return run_service.get_run_detail(rid)
