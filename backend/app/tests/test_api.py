import json
from datetime import datetime, timezone


def _set_width(client, pid, width):
    return client.put(f"/api/papers/{pid}", json={"roll_width": width})


def test_update_paper_rejects_nonpositive(client):
    assert _set_width(client, 1, 0).status_code == 422
    assert _set_width(client, 1, -0.5).status_code == 422
    assert _set_width(client, 1, "abc").status_code == 422


def test_update_paper_unknown_id_404(client):
    assert _set_width(client, 999, 0.5).status_code == 404


def test_smaller_width_never_decreases_sheets(client):
    seq = []
    for w in (1.0, 0.7, 0.5, 0.3, 0.2):
        assert _set_width(client, 1, w).status_code == 200
        r = client.get("/api/estimate", params={"box_id": 1, "paper_id": 1})
        assert r.status_code == 200
        seq.append(r.json()["sheets"])
    assert seq == [1, 1, 2, 4, 8]


def test_saved_run_pinned_after_width_change(client):
    saved = client.post("/api/estimate", json={"box_id": 1, "paper_id": 1, "save": True}).json()
    assert saved["roll_width"] == 1.0
    pinned_sheets = saved["sheets"]
    assert _set_width(client, 1, 0.4).status_code == 200

    listed = client.get("/api/runs").json()["items"][0]
    detail = client.get(f"/api/runs/{saved['run_id']}").json()
    for r in (listed, detail):
        assert r["roll_width"] == 1.0
        assert r["sheets"] == pinned_sheets
        assert r["snapshot_complete"] is True

    fresh = client.get("/api/estimate", params={"box_id": 1, "paper_id": 1}).json()
    assert fresh["roll_width"] == 0.4
    assert fresh["sheets"] != pinned_sheets or fresh["roll_width"] != listed["roll_width"]


def test_list_and_detail_snapshots_agree(client):
    saved = client.post("/api/estimate", json={"box_id": 2, "paper_id": 2, "save": True}).json()
    rid = saved["run_id"]
    listed = next(r for r in client.get("/api/runs").json()["items"] if r["id"] == rid)
    detail = client.get(f"/api/runs/{rid}").json()
    for k in ("paper_id", "roll_width", "sheet_len", "sheets"):
        assert listed[k] == detail[k] == saved[k]
    assert listed["result"]["paper_m2"] == detail["result"]["paper_m2"] == saved["paper_m2"]


def test_recheck_matches_with_snapshot_width_after_edit(client):
    saved = client.post("/api/estimate", json={"box_id": 1, "paper_id": 1, "save": True}).json()
    rid = saved["run_id"]
    recheck = client.get(f"/api/runs/{rid}").json()["recheck"]
    assert recheck["sheets_match"] is True
    assert recheck["paper_m2_match"] is True

    assert _set_width(client, 1, 0.4).status_code == 200
    recheck = client.get(f"/api/runs/{rid}").json()["recheck"]
    assert recheck["roll_width"] == 1.0  # 再干算用落库时卷宽
    assert recheck["sheets_match"] is True
    assert recheck["paper_m2_match"] is True


def test_selected_paper_setting_roundtrip(client):
    r = client.put("/api/settings", json={"selected_paper_id": 2})
    assert r.status_code == 200
    assert r.json()["selected_paper_id"] == "2"
    assert client.get("/api/estimate", params={"box_id": 1}).json()["paper_id"] == 2
    assert client.put("/api/settings", json={"selected_paper_id": 999}).status_code == 404
    # 显式 paper_id 覆盖设置
    r = client.get("/api/estimate", params={"box_id": 1, "paper_id": 1})
    assert r.status_code == 200
    assert r.json()["paper_id"] == 1
    assert client.get("/api/estimate", params={"box_id": 1, "paper_id": 999}).status_code == 404


def test_legacy_run_without_snapshot(client):
    from app.db import connect
    c = connect()
    c.execute(
        "INSERT INTO calc_runs(box_id,overlap,result_json,note,created_at) VALUES (?,?,?,?,?)",
        (1, 1.15, json.dumps({"paper_m2": 0.31}), "", datetime.now(timezone.utc).isoformat()),
    )
    c.commit()
    rid = c.execute("SELECT last_insert_rowid() i").fetchone()["i"]
    c.close()

    listed = next(r for r in client.get("/api/runs").json()["items"] if r["id"] == rid)
    detail = client.get(f"/api/runs/{rid}").json()
    for r in (listed, detail):
        assert r["roll_width"] is None and r["sheets"] is None
        assert r["snapshot_complete"] is False
    assert detail["recheck"]["sheets_match"] is None
    assert detail["recheck"]["reason"] == "legacy_run_without_snapshot"
