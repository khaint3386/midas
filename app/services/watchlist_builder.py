"""Bộ lọc tuần — tự động chọn TOP 12 mã cho watchlist.

Quy trình 2 giai đoạn (đúng tinh thần SEPA của Minervini):
  GĐ1 — KỸ THUẬT toàn nhóm (VN100): tải giá, tính RS Rating percentile
        THẬT trong nhóm (chuẩn IBD), chấm điểm VCP tiềm năng.
  GĐ2 — CƠ BẢN cho top ứng viên kỹ thuật: 4M Phil Town + tin tức đã
        kiểm chứng chéo. Mã có độ tin cậy dữ liệu < ngưỡng bị LOẠI khỏi
        lọc tự động (ghi rõ trong báo cáo, không âm thầm bỏ).

Điểm tổng hợp xếp hạng (đã chốt với người dùng):
  composite = 60% điểm 4M + 40% điểm VCP
  điểm 4M   = 40% Moat + 30% Management + 30% Định giá
              (định giá: 100 nếu đang on-sale dưới MOS, ngược lại = upside% chặn 0-100)

Kết quả: watchlist.json được THAY HOÀN TOÀN bằng top 12,
báo cáo markdown + lịch sử lưu trong data/.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from dataclasses import asdict, dataclass, field
from datetime import datetime

from app.config import DATA_DIR, settings
from app.services import market_data
from app.services.data_quality import MIN_QUALITY_FOR_AUTO
from app.services.four_m import FourMResult, analyze_4m
from app.services.vcp import (
    VCPResult,
    compute_rs_percentiles,
    detect_vcp,
    weighted_performance,
)

logger = logging.getLogger(__name__)

WATCHLIST_SIZE = 12
STAGE2_CANDIDATES = 30          # số ứng viên kỹ thuật được phân tích 4M đầy đủ
DELAY_BETWEEN_CALLS = 0.8       # giây — tránh rate-limit VCI
W_FOUR_M, W_VCP = 0.60, 0.40    # tỉ trọng composite


@dataclass
class CandidateScore:
    symbol: str
    vcp_score: int = 0
    rs_rating: int = 0
    trend_passed: int = 0
    four_m_score: float = 0.0
    moat: int = 0
    management: int = 0
    valuation: float = 0.0
    composite: float = 0.0
    data_reliability: int = 0
    excluded_reason: str = ""    # lý do loại (nếu có) — minh bạch
    notes: list[str] = field(default_factory=list)


# Trạng thái tiến trình cho API/UI theo dõi (module-level, 1 job tại 1 thời điểm)
BUILD_STATE: dict = {
    "running": False, "stage": "", "done": 0, "total": 0,
    "started_at": None, "finished_at": None, "error": None,
    "selected": [], "report_path": None,
}
_LOCK = threading.Lock()


def get_universe(group: str = "VN100") -> list[str]:
    if settings.demo_mode:
        return market_data.load_watchlist()
    from vnstock import Listing

    symbols = Listing().symbols_by_group(group)
    return [str(s).upper() for s in list(symbols) if len(str(s)) == 3]


def _four_m_composite(m: FourMResult) -> tuple[float, float]:
    """(điểm 4M 0-100, điểm định giá 0-100)."""
    valuation = 100.0 if m.on_sale else max(0.0, min(100.0, m.upside_pct))
    score = 0.40 * m.moat_score + 0.30 * m.management_score + 0.30 * valuation
    return round(score, 1), round(valuation, 1)


def build_weekly_watchlist(
    group: str = "VN100", size: int = WATCHLIST_SIZE
) -> list[CandidateScore]:
    """Chạy toàn bộ pipeline lọc tuần. Trả về danh sách đã xếp hạng."""
    with _LOCK:
        if BUILD_STATE["running"]:
            raise RuntimeError("Đang có phiên lọc chạy — chờ xong rồi chạy lại")
        BUILD_STATE.update(
            running=True, stage="Lấy danh sách nhóm", done=0, total=0,
            started_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            finished_at=None, error=None, selected=[], report_path=None,
        )
    try:
        result = _build(group, size)
        BUILD_STATE.update(
            selected=[c.symbol for c in result if not c.excluded_reason][:size]
        )
        return result
    # SystemExit: vnai (vnstock) gọi sys.exit khi vượt rate-limit — nếu không
    # bắt, thread chết im lặng với error=null như đã xảy ra
    except (Exception, SystemExit) as exc:
        BUILD_STATE.update(error=str(exc)[:200])
        raise RuntimeError(str(exc)) from exc
    finally:
        BUILD_STATE.update(
            running=False, finished_at=datetime.now().strftime("%Y-%m-%d %H:%M")
        )


def _build(group: str, size: int) -> list[CandidateScore]:
    symbols = get_universe(group)
    index_df = market_data.get_index_history()

    # ---------- GĐ1: kỹ thuật toàn nhóm ----------
    BUILD_STATE.update(stage=f"GĐ1: quét kỹ thuật {len(symbols)} mã {group}",
                       total=len(symbols), done=0)
    price_cache: dict[str, object] = {}
    perf: dict[str, float] = {}
    failed: list[tuple[str, str]] = []
    for i, sym in enumerate(symbols, 1):
        try:
            df = market_data.get_price_history(sym)
            if len(df) < 60:
                raise RuntimeError(f"chỉ {len(df)} phiên dữ liệu")
            price_cache[sym] = df
            perf[sym] = weighted_performance(df["close"])
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - kể cả rate-limit
            failed.append((sym, str(exc)[:80]))
        BUILD_STATE["done"] = i
        if not settings.demo_mode:
            time.sleep(DELAY_BETWEEN_CALLS)

    # RS Rating percentile THẬT trong nhóm — cách duy nhất đúng chuẩn IBD
    rs_map = compute_rs_percentiles(perf)

    vcp_results: dict[str, VCPResult] = {}
    for sym, df in price_cache.items():
        try:
            vcp_results[sym] = detect_vcp(sym, df, index_df, rs_override=rs_map[sym])
        except Exception as exc:  # noqa: BLE001
            failed.append((sym, f"VCP: {str(exc)[:60]}"))

    stage1 = sorted(
        vcp_results.values(), key=lambda v: -v.potential_score
    )[:STAGE2_CANDIDATES]

    # ---------- GĐ2: 4M + kiểm chứng dữ liệu cho top ứng viên ----------
    BUILD_STATE.update(stage=f"GĐ2: phân tích 4M {len(stage1)} ứng viên",
                       total=len(stage1), done=0)
    candidates: list[CandidateScore] = []
    for i, v in enumerate(stage1, 1):
        c = CandidateScore(
            symbol=v.symbol, vcp_score=v.potential_score,
            rs_rating=v.trend.rs_rating, trend_passed=v.trend.passed_count,
        )
        try:
            snap = market_data.get_fundamentals(v.symbol)
            m = analyze_4m(snap)
            c.moat, c.management = m.moat_score, m.management_score
            c.four_m_score, c.valuation = _four_m_composite(m)
            c.data_reliability = m.data_reliability
            c.notes = m.notes[:3]
            if snap.quality and not snap.quality.reliable:
                c.excluded_reason = (
                    f"Độ tin cậy dữ liệu {m.data_reliability}/100 "
                    f"< ngưỡng {MIN_QUALITY_FOR_AUTO} — cần kiểm chứng thủ công"
                )
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - kể cả rate-limit
            c.excluded_reason = f"Không lấy được BCTC: {str(exc)[:60]}"
        c.composite = round(W_FOUR_M * c.four_m_score + W_VCP * c.vcp_score, 1)
        candidates.append(c)
        BUILD_STATE["done"] = i
        if not settings.demo_mode:
            time.sleep(DELAY_BETWEEN_CALLS)

    eligible = [c for c in candidates if not c.excluded_reason]
    excluded = [c for c in candidates if c.excluded_reason]
    ranked = sorted(eligible, key=lambda c: -c.composite)
    selected = ranked[:size]

    # ---------- Ghi kết quả ----------
    if selected:
        market_data.save_watchlist([c.symbol for c in selected])
    report_path = _write_report(group, selected, ranked, excluded, failed, rs_map)
    _append_history(group, selected)
    BUILD_STATE["report_path"] = str(report_path)
    return ranked + excluded


def _write_report(group, selected, ranked, excluded, failed, rs_map) -> str:
    now = datetime.now()
    lines = [
        f"# Lọc Tuần Tự Động — TOP {len(selected)} Watchlist",
        f"*{now:%d/%m/%Y %H:%M} · nhóm {group} · điểm = 60% 4M + 40% VCP · "
        f"RS Rating percentile thật trên {len(rs_map)} mã*",
        "",
        "## Watchlist mới (thay hoàn toàn)",
        "",
        "| # | Mã | Composite | 4M | VCP | Moat | Mgmt | Định giá | RS | Trend | Tin cậy DL |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, c in enumerate(selected, 1):
        lines.append(
            f"| {i} | **{c.symbol}** | {c.composite} | {c.four_m_score} | {c.vcp_score} "
            f"| {c.moat} | {c.management} | {c.valuation} | {c.rs_rating} "
            f"| {c.trend_passed}/8 | {c.data_reliability}/100 |"
        )
    runner_up = [c for c in ranked if c not in selected][:8]
    if runner_up:
        lines += ["", "## Sát nút (theo dõi thêm)", ""]
        lines += [
            f"- {c.symbol}: composite {c.composite} (4M {c.four_m_score} · VCP {c.vcp_score})"
            for c in runner_up
        ]
    if excluded:
        lines += ["", "## Bị loại vì dữ liệu chưa kiểm chứng được", ""]
        lines += [f"- {c.symbol}: {c.excluded_reason}" for c in excluded]
    if failed:
        lines += ["", "## Mã lỗi khi tải dữ liệu", ""]
        lines += [f"- {s}: {e}" for s, e in failed[:20]]
    lines += [
        "",
        "---",
        "*Lọc tự động theo phương pháp công khai của Phil Town và Mark Minervini. "
        "Thông tin hỗ trợ quyết định — không phải lời khuyên đầu tư.*",
    ]
    path = DATA_DIR / f"bao_cao_loc_tuan_{now:%Y%m%d_%H%M}.md"
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _append_history(group: str, selected: list[CandidateScore]) -> None:
    """Lưu lịch sử các lần lọc — đối chiếu hiệu quả bộ lọc theo thời gian."""
    hist_path = DATA_DIR / "watchlist_history.json"
    try:
        history = json.loads(hist_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        history = []
    history.append(
        {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "group": group,
            "selection": [asdict(c) for c in selected],
        }
    )
    hist_path.write_text(
        json.dumps(history[-52:], ensure_ascii=False, indent=1), encoding="utf-8"
    )


def start_background_build(group: str = "VN100") -> bool:
    """Chạy lọc tuần trong thread nền (cho API). False nếu đang chạy."""
    if BUILD_STATE["running"]:
        return False
    threading.Thread(
        target=lambda: _run_safe(group), daemon=True, name="midas-weekly-filter"
    ).start()
    return True


def _run_safe(group: str) -> None:
    try:
        build_weekly_watchlist(group)
    except BaseException:  # noqa: BLE001 - thread nền không được chết im lặng
        logger.exception("Lọc tuần thất bại")
