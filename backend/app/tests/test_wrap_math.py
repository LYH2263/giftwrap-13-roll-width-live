import pytest
from app.engines.wrap_math import paper_area, plan_sheets, ribbon_estimate

def test_book_box():
    r = paper_area(0.30, 0.20, 0.15, 1.15)
    assert r["box_surface"] == 0.27
    assert r["paper_m2"] == 0.31

def test_ribbon_cross():
    rb = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    assert rb["ribbon_m"] > 0.5

def test_sheets_book_box():
    p = plan_sheets(0.31, 1.0)
    assert p["sheets"] == 1
    assert p["strip_len"] == 0.31
    assert p["sheet_len"] == 0.31

def test_sheets_narrow_roll_needs_more():
    wide = plan_sheets(0.31, 1.0)
    narrow = plan_sheets(0.31, 0.5)
    assert narrow["sheets"] >= wide["sheets"]
    assert narrow["sheets"] == 2

def test_smaller_roll_width_never_drops_sheets():
    # 同一面积，卷宽收窄任意比例，sheets 单调不降
    area = 1.234
    prev = 0
    for k in range(1, 40):
        rw = 1.5 / k
        got = plan_sheets(area, rw)["sheets"]
        assert got >= prev
        prev = got

def test_sheet_len_bounded_by_roll_width():
    for rw in (0.3, 0.7, 1.0):
        p = plan_sheets(0.87, rw)
        assert p["sheet_len"] <= rw + 1e-9
        assert p["sheets"] * p["roll_width"] * p["sheet_len"] >= 0.87 - 1e-6

def test_nonpositive_roll_width_rejected():
    with pytest.raises(ValueError):
        plan_sheets(0.31, 0)
    with pytest.raises(ValueError):
        plan_sheets(0.31, -0.2)
