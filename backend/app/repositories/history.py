import json
from datetime import datetime, timezone
from app.db import connect

_RUN_COLS = """r.id,r.box_id,r.overlap,r.note,r.created_at,r.result_json,
r.paper_id,r.roll_width,r.sheet_len,r.sheets,
b.name box_name,b.length,b.width,b.height"""

def insert_run(box_id, overlap, result, note="", paper_id=None, roll_width=None, sheet_len=None, sheets=None):
    c = connect()
    try:
        cur = c.execute(
            """INSERT INTO calc_runs(box_id,overlap,result_json,note,created_at,paper_id,roll_width,sheet_len,sheets)
               VALUES (?,?,?,?,?,?,?,?,?)""",
            (box_id, overlap, json.dumps(result, ensure_ascii=False), note,
             datetime.now(timezone.utc).isoformat(), paper_id,
             None if roll_width is None else float(roll_width),
             None if sheet_len is None else float(sheet_len),
             None if sheets is None else int(sheets)),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()

def _row_to_run(row):
    d = dict(row)
    result = json.loads(d.pop("result_json"))
    # 读路径拍板：以写入时刻的列快照为准；快照列缺失的旧单才退回 result_json
    roll_width = d.get("roll_width")
    sheet_len = d.get("sheet_len")
    sheets = d.get("sheets")
    if roll_width is None:
        roll_width = result.get("roll_width")
    if sheet_len is None:
        sheet_len = result.get("sheet_len")
    if sheets is None:
        sheets = result.get("sheets")
    d["roll_width"] = roll_width
    d["sheet_len"] = sheet_len
    d["sheets"] = sheets
    d["result"] = result
    return d

def list_runs(limit=50):
    c = connect()
    try:
        rows = c.execute(
            f"""SELECT {_RUN_COLS} FROM calc_runs r
                LEFT JOIN boxes b ON b.id=r.box_id ORDER BY r.id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [_row_to_run(r) for r in rows]
    finally:
        c.close()

def get_run(run_id):
    c = connect()
    try:
        row = c.execute(
            f"SELECT {_RUN_COLS} FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id WHERE r.id=?",
            (run_id,),
        ).fetchone()
        return _row_to_run(row) if row else None
    finally:
        c.close()
