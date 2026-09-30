import pytest
from app.engines.wrap_math import fold_sheets, paper_area, ribbon_estimate

def test_book_box():
    r = paper_area(0.30, 0.20, 0.15, 1.15)
    assert r["box_surface"] == 0.27
    assert r["paper_m2"] == 0.31

def test_ribbon_cross():
    rb = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    assert rb["ribbon_m"] > 0.5

def test_fold_sheet_len_equals_width():
    r = fold_sheets(0.31, 0.5)
    assert r["sheet_len"] == 0.5
    assert r["sheets"] == 2

@pytest.mark.parametrize("width,expected", [(1.0, 1), (0.7, 1), (0.5, 2), (0.3, 4), (0.2, 8)])
def test_fold_smaller_width_never_fewer_sheets(width, expected):
    # 书型盒 paper_m2=0.31
    assert fold_sheets(0.31, width)["sheets"] == expected

def test_fold_float_exact_ratio():
    # 0.49 / 0.7**2 在二进制浮点下为 1.0000000000000002, 不得多算一张
    assert fold_sheets(0.49, 0.7)["sheets"] == 1

def test_fold_zero_area():
    assert fold_sheets(0.0, 1.0)["sheets"] == 0

@pytest.mark.parametrize("width", [0, -0.1, float("nan")])
def test_fold_rejects_nonpositive_width(width):
    with pytest.raises(ValueError):
        fold_sheets(0.31, width)

def test_fold_rejects_negative_area():
    with pytest.raises(ValueError):
        fold_sheets(-0.1, 1.0)
