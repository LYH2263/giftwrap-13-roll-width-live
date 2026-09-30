from fastapi import APIRouter, HTTPException
from app.repositories import history as repo
from app.services import estimate_service
router = APIRouter()
@router.get("/runs")
def runs(limit: int = 50): return {"items": repo.list_runs(limit)}
@router.get("/runs/{run_id}")
def get_run(run_id: int):
    r = repo.get_run(run_id)
    if not r: raise HTTPException(404)
    return r
@router.get("/runs/{run_id}/recheck")
def recheck_run(run_id: int):
    return estimate_service.recheck_run(run_id)
