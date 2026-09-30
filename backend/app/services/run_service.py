from fastapi import HTTPException
from app.engines.wrap_math import fold_sheets, paper_area
from app.repositories import boxes, history

def build_recheck(run: dict) -> dict:
    """用落库时快照卷宽/系数 + 当前盒型尺寸再干算, 与回看的 sheets 互证。"""
    snapshot_sheets = run.get("sheets")
    base = {
        "roll_width": run.get("roll_width"),
        "overlap": run.get("overlap"),
        "snapshot_sheets": snapshot_sheets,
        "sheets_match": None,
        "reason": None,
    }
    box = boxes.get_box(run["box_id"])
    if box is None:
        return {**base, "reason": "box_missing"}
    base["current_box"] = [box["length"], box["width"], box["height"]]
    base["box_dirty"] = box.get("data_quality") == "dirty"
    if not run.get("snapshot_complete"):
        return {**base, "reason": "legacy_run_without_snapshot"}
    calc = paper_area(box["length"], box["width"], box["height"], run["overlap"])
    fold = fold_sheets(calc["paper_m2"], run["roll_width"])
    snapshot_paper_m2 = run["result"].get("paper_m2")
    return {
        **base,
        "paper_m2": calc["paper_m2"],
        "snapshot_paper_m2": snapshot_paper_m2,
        "paper_m2_match": calc["paper_m2"] == snapshot_paper_m2,
        "sheets": fold["sheets"],
        "sheets_match": fold["sheets"] == snapshot_sheets,
    }

def get_run_detail(run_id: int) -> dict:
    run = history.get_run(run_id)
    if run is None:
        raise HTTPException(404)
    run["recheck"] = build_recheck(run)
    return run
