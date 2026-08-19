"""Engine 4M — Phil Town (Rule #1 Investing).

4M = Meaning · Moat · Management · Margin of Safety.

- Moat: "Big Five" ≥ 10%/năm — ROIC, tăng trưởng Doanh thu, EPS, BVPS, FCF.
- Management: ROE ≥ 15%, D/E lành mạnh.
- Margin of Safety: Sticker Price = giá trị nội tại chiết khấu 15%/năm (MARR),
  giá mua an toàn (MOS price) = 50% sticker price.
- Meaning: định tính — do AI analyst đánh giá từ tin tức/ngành (module ai_analyst).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from app.config import settings
from app.services.market_data import FundamentalSnapshot


@dataclass(frozen=True)
class BigFive:
    roic_avg: float
    revenue_growth: float
    eps_growth: float
    bvps_growth: float
    fcf_growth: float

    def passed(self) -> dict[str, bool]:
        return {
            "roic": self.roic_avg >= 10.0,
            "revenue": self.revenue_growth >= 10.0,
            "eps": self.eps_growth >= 10.0,
            "bvps": self.bvps_growth >= 10.0,
            "fcf": self.fcf_growth >= 10.0,
        }


@dataclass(frozen=True)
class FourMResult:
    symbol: str
    big_five: BigFive
    moat_score: int                 # 0-100
    management_score: int           # 0-100
    sticker_price: float            # giá trị nội tại / cp
    mos_price: float                # giá mua an toàn (50% sticker)
    current_price: float
    upside_pct: float               # (sticker - giá) / giá
    is_wonderful: bool              # đạt chuẩn "wonderful company"
    on_sale: bool                   # giá hiện tại <= MOS price
    growth_rate_used: float         # g dùng trong định giá
    pe_used: float
    notes: list[str] = field(default_factory=list)
    data_reliability: int = 100     # điểm tin cậy dữ liệu (data_quality)
    data_warnings: list[str] = field(default_factory=list)
    missing_metrics: list[str] = field(default_factory=list)


def _cagr(series: list[float]) -> float:
    """CAGR (%) của một chuỗi năm; bỏ qua giá trị đầu <= 0."""
    clean = [x for x in series if x > 0]
    if len(clean) < 2:
        return 0.0
    first, last, n = clean[0], clean[-1], len(clean) - 1
    try:
        return (math.pow(last / first, 1 / n) - 1) * 100
    except (ValueError, ZeroDivisionError):
        return 0.0


def _avg(series: list[float]) -> float:
    clean = [x for x in series if not math.isnan(x)]
    return sum(clean) / len(clean) if clean else 0.0


def _available(series: list[float]) -> bool:
    """Chuỗi có đủ dữ liệu để tính (≥2 điểm > 0)? — phân biệt 'thiếu dữ liệu'
    với 'dữ liệu xấu': thiếu thì KHÔNG chấm 0 oan mà ghi chú rõ ràng."""
    return sum(1 for x in series if x and x > 0) >= 2


def analyze_4m(f: FundamentalSnapshot) -> FourMResult:
    notes: list[str] = []
    quality = f.quality  # None trong demo mode
    data_reliability = quality.score if quality else 100
    data_warnings = list(quality.warnings) if quality else []

    # ---- MOAT: Big Five --------------------------------------------------
    big_five = BigFive(
        roic_avg=round(_avg(f.roic), 1),
        revenue_growth=round(_cagr(f.revenue), 1),
        eps_growth=round(_cagr(f.eps), 1),
        bvps_growth=round(_cagr(f.bvps), 1),
        fcf_growth=round(_cagr(f.fcf), 1),
    )
    availability = {
        "roic": _available(f.roic),
        "revenue": _available(f.revenue),
        "eps": _available(f.eps),
        "bvps": _available(f.bvps),
        "fcf": sum(1 for x in f.fcf if x) >= 2,  # FCF âm vẫn là dữ liệu hợp lệ
    }
    missing_metrics = [k for k, ok in availability.items() if not ok]
    passed = big_five.passed()
    n_avail = sum(availability.values())

    if n_avail >= 4:
        # Chỉ chấm trên các chỉ số CÓ dữ liệu — không phạt oan vì thiếu số liệu
        moat_score = round(
            sum(v for k, v in passed.items() if availability[k]) / n_avail * 100
        )
        if missing_metrics:
            notes.append(
                f"Thiếu dữ liệu {', '.join(missing_metrics).upper()} — "
                f"Moat chấm trên {n_avail}/5 chỉ số"
            )
    else:
        moat_score = 0
        notes.append(
            f"Dữ liệu BCTC không đủ để kết luận Moat (chỉ có {n_avail}/5 chỉ số: "
            f"thiếu {', '.join(missing_metrics).upper()}) — loại khỏi khuyến nghị "
            "cho đến khi kiểm chứng được dữ liệu"
        )
    if availability["roic"] and not passed["roic"]:
        notes.append("ROIC bình quân dưới 10% — dấu hiệu thiếu lợi thế cạnh tranh bền vững")

    # ---- MANAGEMENT ------------------------------------------------------
    roe_avg = _avg(f.roe)
    mgmt_points = 0
    mgmt_points += 50 if roe_avg >= 15 else round(max(roe_avg, 0) / 15 * 50)
    if f.debt_to_equity <= 1.0:
        mgmt_points += 50
    elif f.debt_to_equity <= 2.0:
        mgmt_points += 25
        notes.append(f"D/E = {f.debt_to_equity:.1f} hơi cao, cần theo dõi khả năng trả nợ")
    else:
        notes.append(f"D/E = {f.debt_to_equity:.1f} quá cao theo chuẩn Rule #1")
    management_score = min(mgmt_points, 100)

    # ---- MARGIN OF SAFETY: Sticker price ---------------------------------
    # g = min(CAGR EPS lịch sử, 25%) — thận trọng theo Phil Town
    g = min(max(big_five.eps_growth, 0.0), 25.0) / 100
    eps_now = next((x for x in reversed(f.eps) if x > 0), 0.0)
    # PE tương lai = min(2 × g×100, PE trung bình lịch sử); sàn 5
    pe_hist = _avg([p for p in f.pe_history if 0 < p < 60])
    pe_used = max(min(2 * g * 100, pe_hist if pe_hist > 0 else 2 * g * 100), 5.0)

    if eps_now > 0 and g > 0:
        future_eps = eps_now * math.pow(1 + g, 10)
        future_price = future_eps * pe_used
        sticker = future_price / math.pow(1 + settings.marr, 10)
    else:
        sticker = 0.0
        notes.append("EPS hiện tại hoặc tăng trưởng <= 0 — không định giá được theo Rule #1")

    mos_price = sticker * (1 - settings.margin_of_safety)
    upside = ((sticker - f.current_price) / f.current_price * 100) if f.current_price else 0.0

    # Chuẩn wonderful: Moat + Management ĐẠT và dữ liệu ĐÃ kiểm chứng đủ tin cậy
    reliable = quality.reliable if quality else True
    is_wonderful = moat_score >= 80 and management_score >= 60 and reliable
    if moat_score >= 80 and management_score >= 60 and not reliable:
        notes.append(
            f"Chỉ số đạt chuẩn nhưng độ tin cậy dữ liệu chỉ {data_reliability}/100 "
            "— tạm không xếp 'wonderful' cho đến khi dữ liệu được kiểm chứng"
        )
    on_sale = 0 < f.current_price <= mos_price

    if is_wonderful and on_sale:
        notes.append("Doanh nghiệp tuyệt vời đang bán dưới giá MOS — vùng mua theo Rule #1")
    elif is_wonderful:
        notes.append("Doanh nghiệp đạt chuẩn nhưng giá chưa về vùng an toàn — kiên nhẫn chờ")

    return FourMResult(
        symbol=f.symbol,
        big_five=big_five,
        moat_score=moat_score,
        management_score=management_score,
        sticker_price=round(sticker, 0),
        mos_price=round(mos_price, 0),
        current_price=f.current_price,
        upside_pct=round(upside, 1),
        is_wonderful=is_wonderful,
        on_sale=on_sale,
        growth_rate_used=round(g * 100, 1),
        pe_used=round(pe_used, 1),
        notes=notes,
        data_reliability=data_reliability,
        data_warnings=data_warnings,
        missing_metrics=missing_metrics,
    )
