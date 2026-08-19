"""Engine kỹ thuật Minervini: Trend Template + VCP.

Trend Template (SEPA) — 8 tiêu chí xác nhận Giai đoạn 2 (uptrend):
  1. Giá > MA150 và > MA200
  2. MA150 > MA200
  3. MA200 dốc lên ít nhất 1 tháng (~22 phiên)
  4. MA50 > MA150 > MA200
  5. Giá > MA50
  6. Giá cao hơn đáy 52 tuần ít nhất 30%
  7. Giá trong vòng 25% so với đỉnh 52 tuần
  8. RS Rating >= 70 (so với VNINDEX)

VCP (Volatility Contraction Pattern):
  - Nền giá 3-15 tuần với các sóng điều chỉnh co dần (T1 > T2 > T3...)
  - Sóng cuối < 12%, lý tưởng < 8%
  - Volume cạn dần về cuối nền (dry-up)
  - Pivot = đỉnh sóng cuối; tín hiệu MUA khi giá vượt pivot với volume > 1.5x TB50
"""

from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd

from app.config import settings


@dataclass(frozen=True)
class Contraction:
    high_date: str
    low_date: str
    depth_pct: float


@dataclass(frozen=True)
class TrendTemplate:
    criteria: dict[str, bool]
    rs_rating: int
    passed_count: int
    in_stage2: bool


@dataclass(frozen=True)
class VCPResult:
    symbol: str
    trend: TrendTemplate
    contractions: list[Contraction]
    is_vcp: bool
    pivot: float
    buy_signal: bool            # giá vượt pivot + volume xác nhận
    buy_zone: tuple[float, float]  # pivot → pivot +5%
    stop_loss: float            # dưới đáy sóng cuối, tối đa -8%
    volume_dry_up: bool
    last_close: float
    last_volume: float
    avg_volume_50: float
    potential_score: int = 0    # 0-100: mức độ tiệm cận setup Minervini hoàn chỉnh
    notes: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Trend Template
# ---------------------------------------------------------------------------

def weighted_performance(close: pd.Series) -> float:
    """Điểm hiệu suất trọng số kiểu IBD: quý gần nhất x2 + 3 quý trước x1.
    Dùng làm đầu vào cho RS percentile khi quét theo nhóm."""

    def perf(s: pd.Series, n: int) -> float:
        if len(s) < n + 1:
            n = len(s) - 1
        return float(s.iloc[-1] / s.iloc[-n - 1] - 1) if n > 0 else 0.0

    w = [2.0, 1.0, 1.0, 1.0]
    periods = [63, 126, 189, 252]
    return sum(wi * perf(close, p) for wi, p in zip(w, periods))


def compute_rs_percentiles(perf_by_symbol: dict[str, float]) -> dict[str, int]:
    """RS Rating CHUẨN IBD/Minervini = thứ hạng percentile 1-99 trong nhóm.

    Chỉ dùng được khi quét theo nhóm (VN100/HOSE...) — đây là cách tính đúng,
    thay cho công thức quy đổi tuyệt đối cũ vốn trả 99 cho gần như mọi mã.
    """
    n = len(perf_by_symbol)
    if n < 2:
        return {s: 50 for s in perf_by_symbol}
    ranked = sorted(perf_by_symbol.items(), key=lambda kv: kv[1])
    return {
        sym: max(1, min(99, round((i + 0.5) / n * 98 + 1)))
        for i, (sym, _) in enumerate(ranked)
    }


def compute_rs_rating(stock_close: pd.Series, index_close: pd.Series) -> int:
    """Fallback khi phân tích MỘT mã lẻ (không có nhóm để xếp percentile):
    ánh xạ chênh lệch hiệu suất so với VNINDEX qua tanh — bão hòa mềm,
    không còn hiện tượng mã nào cũng 99 như công thức tuyến tính cũ."""
    import math

    spread = weighted_performance(stock_close) - weighted_performance(index_close)
    return max(1, min(99, round(50 + 49 * math.tanh(spread / 0.6))))


def check_trend_template(
    df: pd.DataFrame, index_df: pd.DataFrame, rs_override: int | None = None
) -> TrendTemplate:
    close = df["close"]
    ma50 = close.rolling(50).mean()
    ma150 = close.rolling(150).mean()
    ma200 = close.rolling(200).mean()
    price = float(close.iloc[-1])

    low_52w = float(close.tail(252).min())
    high_52w = float(close.tail(252).max())
    rs = rs_override if rs_override is not None else compute_rs_rating(
        close, index_df["close"]
    )

    ma200_up = (
        len(ma200.dropna()) > 22
        and float(ma200.iloc[-1]) > float(ma200.iloc[-22])
    )

    def last(s: pd.Series) -> float:
        return float(s.iloc[-1]) if not pd.isna(s.iloc[-1]) else 0.0

    criteria = {
        "gia_tren_ma150_ma200": price > last(ma150) > 0 and price > last(ma200) > 0,
        "ma150_tren_ma200": last(ma150) > last(ma200) > 0,
        "ma200_doc_len": ma200_up,
        "ma50_tren_ma150_ma200": last(ma50) > last(ma150) > last(ma200) > 0,
        "gia_tren_ma50": price > last(ma50) > 0,
        "cao_hon_day52w_30pct": low_52w > 0 and price >= low_52w * 1.30,
        "trong_25pct_dinh52w": high_52w > 0 and price >= high_52w * 0.75,
        "rs_rating_70": rs >= settings.min_rs_rating,
    }
    passed = sum(criteria.values())
    return TrendTemplate(
        criteria=criteria, rs_rating=rs, passed_count=passed, in_stage2=passed >= 7
    )


# ---------------------------------------------------------------------------
# VCP detection
# ---------------------------------------------------------------------------

def _swings(df: pd.DataFrame, window: int = 5) -> list[tuple[int, str, float]]:
    """Tìm swing high/low bằng cửa sổ trượt. Trả về (index, 'H'|'L', giá)."""
    highs, lows = df["high"].values, df["low"].values
    pts: list[tuple[int, str, float]] = []
    for i in range(window, len(df) - window):
        seg_h = highs[i - window : i + window + 1]
        seg_l = lows[i - window : i + window + 1]
        if highs[i] == seg_h.max():
            pts.append((i, "H", float(highs[i])))
        elif lows[i] == seg_l.min():
            pts.append((i, "L", float(lows[i])))
    # khử điểm liền kề cùng loại — giữ điểm cực trị hơn
    out: list[tuple[int, str, float]] = []
    for p in pts:
        if out and out[-1][1] == p[1]:
            keep = max(out[-1], p, key=lambda x: x[2]) if p[1] == "H" else min(
                out[-1], p, key=lambda x: x[2]
            )
            out[-1] = keep
        else:
            out.append(p)
    return out


def detect_vcp(
    symbol: str,
    df: pd.DataFrame,
    index_df: pd.DataFrame,
    rs_override: int | None = None,
) -> VCPResult:
    notes: list[str] = []
    trend = check_trend_template(df, index_df, rs_override=rs_override)

    base = df.tail(75).reset_index(drop=True)  # nền tối đa ~15 tuần
    swings = _swings(base)

    # Ghép cặp H→L thành các sóng co thắt
    contractions: list[Contraction] = []
    for i in range(len(swings) - 1):
        if swings[i][1] == "H" and swings[i + 1][1] == "L":
            hi_idx, _, hi = swings[i]
            lo_idx, _, lo = swings[i + 1]
            depth = (hi - lo) / hi * 100
            if 1.0 < depth < 40.0:
                contractions.append(
                    Contraction(
                        high_date=str(base["time"].iloc[hi_idx]),
                        low_date=str(base["time"].iloc[lo_idx]),
                        depth_pct=round(depth, 1),
                    )
                )
    contractions = contractions[-4:]  # tối đa 4 sóng gần nhất

    # Điều kiện co thắt dần + sóng cuối đủ chặt
    tightening = (
        len(contractions) >= 2
        and all(
            contractions[i].depth_pct > contractions[i + 1].depth_pct
            for i in range(len(contractions) - 1)
        )
    )
    final_tight = bool(contractions) and contractions[-1].depth_pct <= 12.0

    # Volume dry-up: TB 10 phiên cuối < 70% TB 50 phiên
    avg50 = float(df["volume"].tail(50).mean())
    avg10 = float(df["volume"].tail(10).mean())
    dry_up = avg10 < avg50 * 0.7 if avg50 else False

    is_vcp = trend.in_stage2 and tightening and final_tight

    # Pivot = swing high cuối cùng trong nền
    last_highs = [p for p in swings if p[1] == "H"]
    pivot = last_highs[-1][2] if last_highs else float(base["high"].max())
    last_close = float(df["close"].iloc[-1])
    last_volume = float(df["volume"].iloc[-1])

    breakout = last_close > pivot
    volume_confirm = last_volume > avg50 * 1.5 if avg50 else False
    buy_signal = is_vcp and breakout and volume_confirm

    # Stop loss: dưới đáy sóng cuối nhưng không quá 8% dưới giá mua (pivot)
    last_lows = [p for p in swings if p[1] == "L"]
    swing_low = last_lows[-1][2] if last_lows else pivot * 0.92
    stop_loss = max(swing_low, pivot * (1 - settings.max_stop_loss_pct))

    if not trend.in_stage2:
        notes.append(
            f"Chưa đạt Trend Template ({trend.passed_count}/8) — không giao dịch ngược Giai đoạn 2"
        )
    if is_vcp and not breakout:
        notes.append(f"VCP hợp lệ, chờ giá vượt pivot {pivot:,.0f} với volume > 1.5x TB50")
    if breakout and not volume_confirm and is_vcp:
        notes.append("Giá vượt pivot nhưng volume chưa xác nhận — cẩn trọng breakout giả")
    if dry_up:
        notes.append("Volume cạn dần đúng đặc tính VCP (supply đã được hấp thụ)")

    potential = _potential_score(
        trend, contractions, tightening, dry_up, last_close, pivot
    )

    return VCPResult(
        symbol=symbol,
        trend=trend,
        contractions=contractions,
        is_vcp=is_vcp,
        pivot=round(pivot, 2),
        buy_signal=buy_signal,
        buy_zone=(round(pivot, 2), round(pivot * 1.05, 2)),
        stop_loss=round(stop_loss, 2),
        volume_dry_up=dry_up,
        last_close=last_close,
        last_volume=last_volume,
        avg_volume_50=avg50,
        potential_score=potential,
        notes=notes,
    )


def _potential_score(
    trend: TrendTemplate,
    contractions: list[Contraction],
    tightening: bool,
    dry_up: bool,
    last_close: float,
    pivot: float,
) -> int:
    """Chấm 0-100 mức độ TIỆM CẬN setup Minervini — dùng để lọc ứng viên
    'gần đủ tiêu chí' chứ không thay thế tín hiệu mua chính thức.

    Trọng số: Trend Template 40 + sóng co thắt 20 + độ chặt sóng cuối 15
    + volume dry-up 15 + giá đang bám sát pivot 10.
    """
    score = trend.passed_count / 8 * 40
    if len(contractions) >= 2:
        score += 20 if tightening else 8
    if contractions:
        d = contractions[-1].depth_pct
        score += 15 if d <= 8 else (10 if d <= 12 else 3)
    if dry_up:
        score += 15
    if pivot > 0 and 0.95 * pivot <= last_close <= 1.05 * pivot:
        score += 10
    return round(min(score, 100))
