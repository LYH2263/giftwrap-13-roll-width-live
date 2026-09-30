from app.db import connect

def list_papers():
    c = connect()
    try:
        return [dict(r) for r in c.execute("SELECT * FROM papers ORDER BY id").fetchall()]
    finally:
        c.close()

def get_paper(pid):
    c = connect()
    try:
        row = c.execute("SELECT * FROM papers WHERE id = ?", (pid,)).fetchone()
        return dict(row) if row else None
    finally:
        c.close()

def update_paper(pid, roll_width, name=None, note=None):
    c = connect()
    try:
        c.execute(
            "UPDATE papers SET roll_width = ?, name = COALESCE(?, name), note = COALESCE(?, note) WHERE id = ?",
            (roll_width, name, note, pid),
        )
        c.commit()
    finally:
        c.close()
    return get_paper(pid)
