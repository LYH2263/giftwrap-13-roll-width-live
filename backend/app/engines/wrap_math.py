import math


def paper_area(length: float, width: float, height: float, overlap: float = 1.15) -> dict:
    L, W, H = float(length), float(width), float(height)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    base = 2 * (L * W + L * H + W * H)
    need = base * float(overlap)
    return {"box_surface": round(base, 3), "overlap": float(overlap), "paper_m2": round(need, 3)}


def plan_sheets(paper_m2: float, roll_width: float) -> dict:
    """按卷宽折张：几何用纸量 paper_m2 不变，另算裁长、每张长度与张数。

    从卷上裁下的总长度 strip_len = paper_m2 / roll_width（面积守恒：
    roll_width × strip_len = paper_m2）；按卷宽一折一张，每折不超过卷宽，
    sheets = ceil(strip_len / roll_width)，末张不足也算一张；每张等分为
    roll_width × sheet_len，sheet_len = strip_len / sheets。
    roll_width 越小 → strip_len 越长、张数越多，故 sheets 单调不降。
    """
    rw = float(roll_width)
    if rw <= 0:
        raise ValueError("roll_width must be positive")
    if float(paper_m2) <= 0:
        raise ValueError("paper_m2 must be positive")
    strip = float(paper_m2) / rw
    sheets = max(1, math.ceil(strip / rw - 1e-9))
    return {
        "roll_width": rw,
        "strip_len": strip,
        "sheet_len": strip / sheets,
        "sheets": sheets,
    }


def ribbon_estimate(length: float, width: float, height: float, wrap_style: str = "cross") -> dict:
    """Helper: approximate ribbon length in meters (not stored as primary metric)."""
    L, W, H = float(length), float(width), float(height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}
