from app.config import DEFAULT_OVERLAP
from app.db import connect

def get_all():
    c = connect()
    try:
        d = {r["key"]: r["value"] for r in c.execute("SELECT key,value FROM settings").fetchall()}
        d.setdefault("overlap", str(DEFAULT_OVERLAP))
        return d
    finally:
        c.close()

def get_overlap():
    return float(get_all().get("overlap", DEFAULT_OVERLAP))

def set_value(key, value):
    c = connect()
    try:
        c.execute(
            "INSERT INTO settings(key,value) VALUES (?,?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, str(value)),
        )
        c.commit()
    finally:
        c.close()

def get_selected_paper_id():
    """算纸台当前选用纸卷；悬空/损坏时自愈为第一张纸。无纸返回 None。"""
    from app.repositories import papers as papers_repo
    raw = get_all().get("selected_paper_id")
    try:
        pid = int(raw) if raw is not None else None
    except (TypeError, ValueError):
        pid = None
    if pid is not None and papers_repo.get_paper(pid) is not None:
        return pid
    papers = papers_repo.list_papers()
    if not papers:
        return None
    pid = papers[0]["id"]
    set_value("selected_paper_id", pid)
    return pid

def set_selected_paper_id(paper_id):
    set_value("selected_paper_id", int(paper_id))
