from fastapi import HTTPException
from app.engines.wrap_math import fold_sheets, paper_area, ribbon_estimate
from app.repositories import boxes, history, papers, settings_repo

def _resolve_paper(paper_id):
    pid = paper_id if paper_id is not None else settings_repo.get_selected_paper_id()
    paper = papers.get_paper(pid) if pid is not None else None
    if paper is None:
        raise HTTPException(404, "no usable paper selected")
    rw = float(paper["roll_width"])
    if not (rw > 0):  # 兜底库内坏数据; API 边界已由 Pydantic 422 拦截
        raise HTTPException(422, "paper roll_width must be positive")
    return pid, paper, rw

def run_estimate(box_id: int, overlap: float | None, wrap_style: str, save: bool,
                 note: str, paper_id: int | None = None):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")
    pid, paper, rw = _resolve_paper(paper_id)
    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()
    calc = paper_area(box["length"], box["width"], box["height"], ov)
    ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
    fold = fold_sheets(calc["paper_m2"], rw)
    snapshot = {"paper_id": pid, "paper_name": paper["name"],
                "roll_width": rw, **fold}
    payload = {**calc, **snapshot, "ribbon": ribbon, "box_id": box_id}
    run_id = None
    if save:
        run_id = history.insert_run(
            box_id, ov, payload, note,
            paper_id=pid, roll_width=rw,
            sheet_len=fold["sheet_len"], sheets=fold["sheets"],
        )
    return {"box": box, "run_id": run_id, **calc, **snapshot, "ribbon": ribbon}
