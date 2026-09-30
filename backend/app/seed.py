from app.db import connect

def _migrate(c):
    """对既有 DB 幂等补列（CREATE TABLE IF NOT EXISTS 不会新增列）。"""
    cols = {r["name"] for r in c.execute("PRAGMA table_info(calc_runs)").fetchall()}
    for name, decl in (
        ("paper_id", "INTEGER"),
        ("roll_width", "REAL"),
        ("sheet_len", "REAL"),
        ("sheets", "INTEGER"),
    ):
        if name not in cols:
            c.execute(f"ALTER TABLE calc_runs ADD COLUMN {name} {decl}")

def init_db():
    c = connect()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS boxes(id INTEGER PRIMARY KEY,name TEXT,length REAL,width REAL,height REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS papers(id INTEGER PRIMARY KEY,name TEXT,roll_width REAL,data_quality TEXT,note TEXT);
    CREATE TABLE IF NOT EXISTS settings(key TEXT PRIMARY KEY,value TEXT);
    CREATE TABLE IF NOT EXISTS calc_runs(id INTEGER PRIMARY KEY AUTOINCREMENT,box_id INT,overlap REAL,result_json TEXT,note TEXT,created_at TEXT);
    """)
    _migrate(c)
    if c.execute("SELECT COUNT(*) c FROM boxes").fetchone()["c"] == 0:
        c.executemany("INSERT INTO boxes(name,length,width,height,data_quality,note) VALUES (?,?,?,?,?,?)",[
            ("书型盒",0.30,0.20,0.15,"clean",""),
            ("方形礼盒",0.25,0.25,0.10,"clean",""),
            ("脏数据-负高",0.2,0.2,-0.1,"dirty","高度负"),
        ])
        c.executemany("INSERT INTO papers(name,roll_width,data_quality,note) VALUES (?,?,?,?)",[
            ("哑光纸1.0m",1.0,"clean",""),
            ("牛皮纸0.7m",0.7,"clean",""),
        ])
        c.execute("INSERT INTO settings(key,value) VALUES ('overlap','1.15')")
        c.execute("INSERT INTO settings(key,value) VALUES ('selected_paper_id','1')")
        c.commit()
    else:
        # 既有库补默认项；悬空 id 由 settings_repo.get_selected_paper_id 自愈
        c.execute("INSERT OR IGNORE INTO settings(key,value) VALUES ('selected_paper_id','1')")
        c.commit()
    c.close()
