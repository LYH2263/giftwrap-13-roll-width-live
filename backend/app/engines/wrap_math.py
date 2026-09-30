import math


def paper_area(length: float, width: float, height: float, overlap: float = 1.15) -> dict:
    L, W, H = float(length), float(width), float(height)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    base = 2 * (L * W + L * H + W * H)
    need = base * float(overlap)
    return {"box_surface": round(base, 3), "overlap": float(overlap), "paper_m2": round(need, 3)}


FOLD_EPS = 1e-9


def fold_sheets(paper_m2: float, roll_width: float) -> dict:
    """按卷宽折张: 每张为卷宽见方, sheet_len = roll_width,
    sheets = ceil(paper_m2 / roll_width^2)。paper_m2 必须取 paper_area 已舍入后的值。"""
    area = float(paper_m2)
    w = float(roll_width)
    if not (w > 0):  # 同时拒绝 0、负数与 nan
        raise ValueError("roll_width must be positive")
    if area < 0:
        raise ValueError("paper_m2 must be non-negative")
    sheets = math.ceil(area / (w * w) - FOLD_EPS)
    return {"sheet_len": round(w, 3), "sheets": sheets}


def ribbon_estimate(length: float, width: float, height: float, wrap_style: str = "cross") -> dict:
    """Helper: approximate ribbon length in meters (not stored as primary metric)."""
    L, W, H = float(length), float(width), float(height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}
