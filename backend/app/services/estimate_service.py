from fastapi import HTTPException
from app.engines.wrap_math import paper_area, plan_sheets, ribbon_estimate
from app.repositories import boxes, history, papers, settings_repo

def _resolve_paper(paper_id):
    if paper_id is None:
        all_papers = papers.list_papers()
        if not all_papers:
            raise HTTPException(422, "尚未配置包装纸")
        return all_papers[0]
    paper = papers.get_paper(paper_id)
    if not paper:
        raise HTTPException(404, "paper not found")
    return paper

def run_estimate(box_id, overlap, wrap_style, save, note, paper_id=None):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")
    paper = _resolve_paper(paper_id)
    roll_width = float(paper["roll_width"])
    if roll_width <= 0:
        raise HTTPException(422, "卷宽必须为正数")
    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()
    # 新切张走现行卷宽；paper_m2 仍是纯几何口径，与卷宽无关
    calc = paper_area(box["length"], box["width"], box["height"], ov)
    plan = plan_sheets(calc["paper_m2"], roll_width)
    ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
    run_id = None
    if save:
        # 写入时把现行卷宽/折张快照钉进列里，之后改卷宽不动旧单
        run_id = history.insert_run(
            box_id, ov, {**calc, "ribbon": ribbon}, note,
            paper_id=paper["id"], roll_width=plan["roll_width"],
            sheet_len=plan["sheet_len"], sheets=plan["sheets"],
        )
    return {
        "box": box,
        "paper": {"id": paper["id"], "name": paper["name"], "roll_width": plan["roll_width"]},
        "run_id": run_id,
        **calc,
        **plan,
        "ribbon": ribbon,
    }

def recheck_run(run_id):
    """用写入时钉住的卷宽/系数再干算一遍，与回看快照互证。"""
    run = history.get_run(run_id)
    if not run:
        raise HTTPException(404)
    if run.get("roll_width") is None:
        raise HTTPException(422, "该单为无卷宽快照的旧单，无法按卷宽复算")
    calc = paper_area(run["length"], run["width"], run["height"], run["overlap"])
    plan = plan_sheets(calc["paper_m2"], run["roll_width"])
    return {
        "run_id": run_id,
        "snapshot": {
            "roll_width": run["roll_width"],
            "sheet_len": run["sheet_len"],
            "sheets": run["sheets"],
            "paper_m2": run["result"].get("paper_m2"),
        },
        "recomputed": {"paper_m2": calc["paper_m2"], **plan},
        "sheets_match": plan["sheets"] == run["sheets"],
    }
