"""Recommender — hợp nhất 4M (Phil Town) + VCP (Minervini) thành khuyến nghị.

Logic quyết định:
  MUA         : wonderful company (4M) + VCP breakout có volume xác nhận
  CHỜ PIVOT   : wonderful company + VCP hợp lệ nhưng chưa breakout
  TÍCH LŨY DÀI HẠN: wonderful + on sale (giá < MOS) nhưng chưa có setup kỹ thuật
  THEO DÕI    : đạt một trong hai tầng
  ĐỨNG NGOÀI  : không đạt cả hai

Midas chỉ đưa thông tin hỗ trợ quyết định — không phải lệnh giao dịch tự động.
"""

from __future__ import annotations

import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime

from app.services import market_data
from app.services.ai_analyst import MeaningAssessment, assess_meaning
from app.services.four_m import FourMResult, analyze_4m
from app.services.news_feed import fetch_news
from app.services.vcp import VCPResult, detect_vcp

logger = logging.getLogger(__name__)

ACTIONS = ("MUA", "CHỜ PIVOT", "TÍCH LŨY DÀI HẠN", "THEO DÕI", "ĐỨNG NGOÀI")


@dataclass(frozen=True)
class Recommendation:
    symbol: str
    action: str
    conviction: int             # 0-100
    reasons: list[str]
    four_m: FourMResult
    vcp: VCPResult
    meaning: MeaningAssessment
    generated_at: str = field(
        default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    def to_dict(self) -> dict:
        d = asdict(self)
        d["vcp"]["buy_zone"] = list(self.vcp.buy_zone)
        return d


def analyze_symbol(symbol: str) -> Recommendation:
    symbol = symbol.upper()
    price_df = market_data.get_price_history(symbol)
    index_df = market_data.get_index_history()
    fundamentals = market_data.get_fundamentals(symbol)
    news = fetch_news(symbol, limit=10)

    four_m = analyze_4m(fundamentals)
    vcp = detect_vcp(symbol, price_df, index_df)
    meaning = assess_meaning(symbol, news)

    action, conviction, reasons = _decide(four_m, vcp, meaning)
    return Recommendation(
        symbol=symbol, action=action, conviction=conviction,
        reasons=reasons, four_m=four_m, vcp=vcp, meaning=meaning,
    )


def _decide(
    four_m: FourMResult, vcp: VCPResult, meaning: MeaningAssessment
) -> tuple[str, int, list[str]]:
    reasons: list[str] = []
    fundamental_ok = four_m.is_wonderful and meaning.meaning_score >= 40
    technical_setup = vcp.is_vcp
    technical_trigger = vcp.buy_signal

    if fundamental_ok:
        reasons.append(
            f"4M đạt chuẩn: Moat {four_m.moat_score}/100, Management "
            f"{four_m.management_score}/100, sentiment tin tức {meaning.sentiment}"
        )
    if meaning.verification_note:
        reasons.append(f"Kiểm chứng tin tức: {meaning.verification_note}")
    if four_m.data_reliability < 100:
        reasons.append(
            f"Độ tin cậy dữ liệu BCTC: {four_m.data_reliability}/100"
            + (f" — {'; '.join(four_m.data_warnings[:2])}" if four_m.data_warnings else "")
        )
    if four_m.on_sale:
        reasons.append(
            f"Giá {four_m.current_price:,.0f} dưới MOS {four_m.mos_price:,.0f} "
            f"(sticker {four_m.sticker_price:,.0f})"
        )
    if technical_setup:
        depths = " → ".join(f"{c.depth_pct}%" for c in vcp.contractions)
        reasons.append(f"VCP hợp lệ ({depths}), pivot {vcp.pivot:,.0f}")

    if fundamental_ok and technical_trigger:
        reasons.append(
            f"Breakout pivot với volume {vcp.last_volume / vcp.avg_volume_50:.1f}x TB50 "
            f"— stop loss {vcp.stop_loss:,.0f}"
        )
        conviction = min(
            95, 55 + four_m.moat_score // 5 + vcp.trend.passed_count * 2
        )
        return "MUA", conviction, reasons

    if fundamental_ok and technical_setup:
        return "CHỜ PIVOT", 70, reasons + [
            f"Chờ giá vượt {vcp.pivot:,.0f} kèm volume > 1.5x TB50 rồi mới vào lệnh"
        ]

    if fundamental_ok and four_m.on_sale:
        return "TÍCH LŨY DÀI HẠN", 60, reasons + [
            "Chưa có setup kỹ thuật — phù hợp tích lũy theo Rule #1, không lướt sóng"
        ]

    if fundamental_ok or technical_setup or vcp.trend.in_stage2:
        reasons.append(
            "Chỉ đạt một tầng lọc (cơ bản hoặc kỹ thuật) — đưa vào danh sách theo dõi"
        )
        return "THEO DÕI", 40, reasons

    reasons.append(
        f"Không đạt 4M (Moat {four_m.moat_score}/100) và không có setup "
        f"(Trend Template {vcp.trend.passed_count}/8)"
    )
    return "ĐỨNG NGOÀI", 15, reasons


def scan_watchlist() -> list[Recommendation]:
    """Quét toàn bộ watchlist, xếp theo mức độ ưu tiên hành động."""
    order = {a: i for i, a in enumerate(ACTIONS)}
    results: list[Recommendation] = []
    for symbol in market_data.load_watchlist():
        try:
            results.append(analyze_symbol(symbol))
        # Bắt cả SystemExit: vnai (vnstock) gọi sys.exit khi vượt rate-limit
        except (Exception, SystemExit):  # noqa: BLE001 - không chặn cả scan
            logger.exception("Lỗi phân tích %s", symbol)
    return sorted(results, key=lambda r: (order.get(r.action, 9), -r.conviction))
