"""Tầng kiểm chứng dữ liệu — vòng lặp tự xác thực trước khi chấm điểm.

Nguyên tắc: KHÔNG khuyến nghị dựa trên dữ liệu chưa kiểm chứng.
  1. Sanity check nội tại: đơn vị, thứ tự năm, độ phủ chuỗi, PE hàm ý hợp lý
  2. Đối chiếu chéo 2 nguồn độc lập (VCI vs KBS trong vnstock 4.x)
  3. Chấm điểm tin cậy 0-100; dưới ngưỡng -> loại khỏi lọc tự động,
     và LUÔN ghi rõ "thiếu dữ liệu" thay vì âm thầm chấm 0 điểm oan.
"""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass, field

MIN_QUALITY_FOR_AUTO = 55       # dưới ngưỡng này không đưa vào lọc tự động
CROSS_CHECK_TOLERANCE = 0.20    # lệch >20% giữa 2 nguồn -> cảnh báo
KEY_SERIES = ("revenue", "eps", "bvps", "fcf", "roic", "roe")


@dataclass(frozen=True)
class DataQuality:
    """Kết quả kiểm chứng dữ liệu cơ bản của một mã."""

    score: int                              # 0-100
    sources: list[str]                      # nguồn đã dùng, vd ["VCI", "KBS"]
    cross_checked: bool                     # đã đối chiếu được 2 nguồn?
    cross_check_diff_pct: float | None      # lệch EPS lớn nhất giữa 2 nguồn (%)
    n_years: int                            # số năm BCTC lấy được
    missing: list[str] = field(default_factory=list)   # chuỗi thiếu
    warnings: list[str] = field(default_factory=list)  # cảnh báo cụ thể

    @property
    def reliable(self) -> bool:
        return self.score >= MIN_QUALITY_FOR_AUTO

    def to_dict(self) -> dict:
        d = asdict(self)
        d["reliable"] = self.reliable
        return d


def _has_data(series: list[float], min_points: int = 2) -> bool:
    return sum(1 for x in series if x and not math.isnan(x)) >= min_points


def sanity_check(
    *,
    years: list[int],
    series_map: dict[str, list[float]],
    eps_now: float,
    current_price: float,
) -> tuple[list[str], list[str]]:
    """Kiểm tra nội tại một snapshot. Trả về (missing, warnings)."""
    missing = [name for name in KEY_SERIES
               if not _has_data(series_map.get(name, []))]
    warnings: list[str] = []

    if len(years) < 5:
        warnings.append(
            f"Chỉ lấy được {len(years)} năm BCTC (chuẩn Phil Town cần ≥5, tốt nhất 10)"
        )
    if years != sorted(years):
        warnings.append("Thứ tự năm không tăng dần — đã tự sắp xếp lại")

    # PE hàm ý = giá / EPS phải nằm trong vùng khả dĩ, nếu không là sai đơn vị
    if eps_now > 0 and current_price > 0:
        implied_pe = current_price / eps_now
        if not (1.0 <= implied_pe <= 200.0):
            warnings.append(
                f"PE hàm ý {implied_pe:,.1f} bất thường — nghi sai đơn vị EPS hoặc giá"
            )

    # ROIC/ROE ngoài vùng -100..100% sau chuẩn hóa là dấu hiệu map sai cột
    for name in ("roic", "roe"):
        vals = [x for x in series_map.get(name, []) if x and not math.isnan(x)]
        if vals and max(abs(v) for v in vals) > 150:
            warnings.append(f"{name.upper()} có giá trị ngoài ±150% — nghi map sai cột")

    return missing, warnings


def cross_check_eps(
    primary_eps: list[float], secondary_eps: list[float]
) -> tuple[bool, float | None]:
    """So khớp EPS năm gần nhất giữa 2 nguồn. Trả về (khớp?, %lệch)."""
    p = next((x for x in reversed(primary_eps) if x and not math.isnan(x)), None)
    s = next((x for x in reversed(secondary_eps) if x and not math.isnan(x)), None)
    if p is None or s is None or p == 0:
        return False, None
    diff = abs(p - s) / abs(p)
    return diff <= CROSS_CHECK_TOLERANCE, round(diff * 100, 1)


def score_quality(
    *,
    n_years: int,
    missing: list[str],
    warnings: list[str],
    cross_checked: bool,
    cross_check_ok: bool | None,
) -> int:
    """Điểm tin cậy 0-100 — minh bạch từng khoản trừ."""
    score = 100
    score -= 15 * len(missing)                       # mỗi chuỗi thiếu -15
    if n_years < 5:
        score -= 20
    elif n_years < 8:
        score -= 8
    score -= 10 * sum("nghi sai đơn vị" in w or "map sai cột" in w for w in warnings)
    if not cross_checked:
        score -= 10                                  # chưa đối chiếu được nguồn 2
    elif cross_check_ok is False:
        score -= 25                                  # 2 nguồn lệch nhau lớn
    return max(0, min(100, score))
