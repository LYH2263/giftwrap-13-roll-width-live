import json
from datetime import datetime, timezone
from app.db import connect

SNAPSHOT_KEYS = ("paper_id", "roll_width", "sheet_len", "sheets")

def insert_run(box_id, overlap, result, note="",
               paper_id=None, roll_width=None, sheet_len=None, sheets=None):
    c = connect()
    try:
        cur = c.execute(
            "INSERT INTO calc_runs(box_id,overlap,result_json,note,created_at,"
            "paper_id,roll_width,sheet_len,sheets) VALUES (?,?,?,?,?,?,?,?,?)",
            (box_id, overlap, json.dumps(result, ensure_ascii=False), note,
             datetime.now(timezone.utc).isoformat(),
             paper_id, roll_width, sheet_len, sheets),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()

def _map_row(row):
    d = dict(row)
    result = json.loads(d.pop("result_json"))
    d["result"] = result
    for key in SNAPSHOT_KEYS:
        val = d.get(key)
        d[key] = val if val is not None else result.get(key)  # 旧行回退到 result_json
    d["snapshot_complete"] = all(d.get(k) is not None for k in SNAPSHOT_KEYS)
    return d

_RUN_SELECT = (
    "SELECT r.*, b.name box_name FROM calc_runs r "
    "LEFT JOIN boxes b ON b.id = r.box_id"
)

def list_runs(limit=50):
    c = connect()
    try:
        rows = c.execute(
            _RUN_SELECT + " ORDER BY r.id DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [_map_row(r) for r in rows]
    finally:
        c.close()

def get_run(run_id):
    c = connect()
    try:
        row = c.execute(_RUN_SELECT + " WHERE r.id = ?", (run_id,)).fetchone()
        return _map_row(row) if row else None
    finally:
        c.close()
