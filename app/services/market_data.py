"""Tầng dữ liệu thị trường: giá OHLCV và báo cáo tài chính.

Nguồn thật: vnstock 4.x — nguồn chính VCI, đối chiếu chéo KBS.
Định dạng BCTC vnstock 4.x đã XOAY NGANG: mỗi HÀNG là một chỉ tiêu
(cột item/item_en/item_id), mỗi CỘT là một năm ("2025", "2024", ...).
Mặc định API chỉ trả 4 năm -> phải gọi với limit cao hơn cho chuẩn
Phil Town 10 năm. Mọi chuỗi đều được sắp xếp năm TĂNG DẦN trước khi
tính CAGR, và đi qua tầng kiểm chứng data_quality trước khi chấm điểm.

Demo mode: dữ liệu tổng hợp có chủ đích (một mã có mẫu hình VCP chuẩn)
để test offline và demo UI.
"""

from __future__ import annotations

import json
import logging
import math
import random
import re
import threading
import time as time_mod
from collections import deque
from dataclasses import asdict as dc_asdict, dataclass, field
from datetime import date, timedelta
from typing import Any, Callable

import pandas as pd

from app.config import DATA_DIR, settings
from app.services.data_quality import (
    DataQuality,
    cross_check_eps,
    sanity_check,
    score_quality,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Điều tiết tần suất gọi vnstock — gói free bị vnai giới hạn 20 request/PHÚT
# và khi vượt, vnai gọi sys.exit() (SystemExit — KHÔNG phải Exception) làm
# endpoint sập 500 và thread quét chết im lặng. Hai lớp phòng thủ:
#   1. _vn_call: chủ động giãn nhịp để không bao giờ chạm trần
#   2. Nếu vẫn dính SystemExit: chờ 65s thử lại 1 lần, thất bại nữa thì
#      chuyển thành RuntimeError để các tầng trên xử lý như lỗi thường
# ---------------------------------------------------------------------------

_MAX_CALLS_PER_MIN = 15          # dưới trần 20/phút của vnai để an toàn
_CALL_TIMES: deque[float] = deque()
_THROTTLE_LOCK = threading.Lock()


def _throttle() -> None:
    with _THROTTLE_LOCK:
        while True:
            now = time_mod.monotonic()
            while _CALL_TIMES and now - _CALL_TIMES[0] > 60.0:
                _CALL_TIMES.popleft()
            if len(_CALL_TIMES) < _MAX_CALLS_PER_MIN:
                _CALL_TIMES.append(now)
                return
            wait = 60.0 - (now - _CALL_TIMES[0]) + 0.5
            logger.info("Điều tiết vnstock: chờ %.1fs (tránh rate-limit)", wait)
            time_mod.sleep(max(wait, 0.5))


def _vn_call(fn: Callable, *args: Any, **kwargs: Any) -> Any:
    """Gọi hàm vnstock với điều tiết tần suất + chuyển SystemExit thành lỗi thường."""
    _throttle()
    try:
        return fn(*args, **kwargs)
    except SystemExit as exc:  # vnai sys.exit khi vượt hạn mức
        logger.warning("vnai chặn tần suất (%s) — chờ 65s rồi thử lại", exc)
        time_mod.sleep(65)
        _throttle()
        try:
            return fn(*args, **kwargs)
        except SystemExit as exc2:
            raise RuntimeError(
                f"vnstock chặn tần suất (rate limit): {str(exc2)[:150]}"
            ) from exc2


@dataclass(frozen=True)
class FundamentalSnapshot:
    """Chuỗi chỉ số cơ bản nhiều năm của một mã — đầu vào cho engine 4M."""

    symbol: str
    years: list[int]
    revenue: list[float]          # doanh thu thuần (tỷ VND)
    eps: list[float]              # EPS (VND)
    bvps: list[float]             # giá trị sổ sách / cp (VND)
    fcf: list[float]              # dòng tiền tự do (tỷ VND)
    roic: list[float]             # ROIC (%)
    roe: list[float]              # ROE (%)
    debt_to_equity: float         # D/E kỳ gần nhất
    pe_history: list[float]       # P/E các năm
    current_price: float          # giá hiện tại (VND)
    industry: str = ""
    quality: DataQuality | None = field(default=None, compare=False)


def load_watchlist() -> list[str]:
    try:
        raw = settings.watchlist_path.read_text(encoding="utf-8")
        return list(json.loads(raw))
    except (OSError, json.JSONDecodeError):
        logger.warning("Không đọc được watchlist, dùng danh sách trống")
        return []


def save_watchlist(symbols: list[str]) -> None:
    settings.watchlist_path.write_text(
        json.dumps(sorted(set(s.upper() for s in symbols))), encoding="utf-8"
    )


# ---------------------------------------------------------------------------
# Giá lịch sử (OHLCV)
# ---------------------------------------------------------------------------

def get_price_history(symbol: str, days: int = 420) -> pd.DataFrame:
    """Trả về DataFrame cột: time, open, high, low, close, volume (ngày)."""
    if settings.demo_mode:
        return _demo_price_history(symbol, days)
    return _vnstock_price_history(symbol, days)


_PRICE_CACHE: dict[tuple[str, int], tuple[float, pd.DataFrame]] = {}
_PRICE_CACHE_TTL = 900.0  # 15 phút — quét rồi lọc tuần không tải lại giá


def _vnstock_price_history(symbol: str, days: int) -> pd.DataFrame:
    import time as _time

    from vnstock import Vnstock  # import trễ: chỉ cần khi chạy thật

    cached = _PRICE_CACHE.get((symbol, days))
    if cached and time_mod.monotonic() - cached[0] < _PRICE_CACHE_TTL:
        return cached[1]

    end = date.today()
    start = end - timedelta(days=int(days * 1.6))  # bù ngày nghỉ
    last_err: Exception | None = None
    for attempt in range(3):  # retry khi mạng chập chờn
        try:
            stock = Vnstock().stock(symbol=symbol, source="VCI")
            df = _vn_call(
                stock.quote.history,
                start=start.isoformat(), end=end.isoformat(), interval="1D",
            )
            break
        except Exception as exc:  # noqa: BLE001
            last_err = exc
            _time.sleep(1.5 * (attempt + 1))
    else:
        raise RuntimeError(f"vnstock không tải được {symbol}: {last_err}")

    df = df.rename(columns=str.lower)
    df["time"] = pd.to_datetime(df["time"]).dt.date.astype(str)
    df = df[["time", "open", "high", "low", "close", "volume"]]
    # Sắp phiên TĂNG DẦN theo ngày — mọi tính toán MA/RS giả định thứ tự này
    df = df.sort_values("time").reset_index(drop=True)
    # Làm sạch: bỏ phiên thiếu giá, volume NaN -> 0 (NaN làm JSON sập)
    df = df.dropna(subset=["open", "high", "low", "close"])
    df["volume"] = df["volume"].fillna(0)
    # Chuẩn hóa đơn vị: VCI trả giá theo NGHÌN đồng (vd 26.5) trong khi
    # EPS/BVPS tính bằng đồng -> quy hết về đồng để định giá 4M đúng
    if float(df["close"].median()) < 500:
        for c in ("open", "high", "low", "close"):
            df[c] = df[c] * 1000.0
    df = df.tail(days).reset_index(drop=True)
    _PRICE_CACHE[(symbol, days)] = (time_mod.monotonic(), df)
    return df


_INDEX_CACHE: dict[int, tuple[float, pd.DataFrame]] = {}
_INDEX_CACHE_TTL = 900.0  # 15 phút


def get_index_history(days: int = 420) -> pd.DataFrame:
    """VNINDEX — dùng làm chuẩn tính RS rating. Cache 15 phút để quét
    watchlist không tải lại index cho từng mã."""
    import time

    now = time.monotonic()
    cached = _INDEX_CACHE.get(days)
    if cached and now - cached[0] < _INDEX_CACHE_TTL:
        return cached[1]
    if settings.demo_mode:
        df = _demo_price_history("VNINDEX", days, base=1280.0, drift=0.0002)
    else:
        df = _vnstock_price_history("VNINDEX", days)
    _INDEX_CACHE[days] = (now, df)
    return df


# ---------------------------------------------------------------------------
# Báo cáo tài chính
# ---------------------------------------------------------------------------

_FUND_CACHE_PATH = DATA_DIR / "cache_fundamentals.json"
_FUND_CACHE_LOCK = threading.Lock()


def _fund_cache_get(symbol: str) -> FundamentalSnapshot | None:
    """BCTC là dữ liệu năm/quý — cache 1 ngày để tiết kiệm ~70% request."""
    try:
        with _FUND_CACHE_LOCK:
            cache = json.loads(_FUND_CACHE_PATH.read_text(encoding="utf-8"))
        ent = cache.get(symbol)
        if not ent or ent.get("date") != date.today().isoformat():
            return None
        d = dict(ent["snapshot"])
        q = d.pop("quality", None)
        return FundamentalSnapshot(
            **d, quality=DataQuality(**q) if q else None
        )
    except Exception:  # noqa: BLE001 - cache hỏng thì tải lại, không chặn
        return None


def _fund_cache_put(symbol: str, snap: FundamentalSnapshot) -> None:
    try:
        with _FUND_CACHE_LOCK:
            try:
                cache = json.loads(_FUND_CACHE_PATH.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                cache = {}
            cache[symbol] = {
                "date": date.today().isoformat(),
                "snapshot": dc_asdict(snap),
            }
            _FUND_CACHE_PATH.write_text(
                json.dumps(cache, ensure_ascii=False), encoding="utf-8"
            )
    except Exception:  # noqa: BLE001
        logger.debug("Không ghi được cache BCTC %s", symbol)


def get_fundamentals(symbol: str) -> FundamentalSnapshot:
    if settings.demo_mode:
        return _demo_fundamentals(symbol)
    cached = _fund_cache_get(symbol)
    if cached is not None:
        return cached
    snap = _vnstock_fundamentals(symbol)
    _fund_cache_put(symbol, snap)
    return snap


# Số năm BCTC yêu cầu (Phil Town: Big Five 10 năm; vnstock 4.x mặc định chỉ 4)
FUND_YEARS = 12


def _fetch_year_report(stock: Any, report_type: str) -> pd.DataFrame:
    """Lấy báo cáo khung NĂM với nhiều năm nhất có thể.

    vnstock 4.0.2: API public (ratio/income_statement/cash_flow) khóa cứng
    4 kỳ; _get_financial_report nhận limit — dùng nó trước, fallback public.
    """
    fin = stock.finance  # chú ý: khởi tạo Finance cũng tốn request (handshake)
    try:
        df = _vn_call(
            fin._get_financial_report,  # noqa: SLF001 - đã kiểm chứng trong 4.0.2
            report_type, period="year", lang="vi", limit=FUND_YEARS,
        )
        if isinstance(df, pd.DataFrame) and not df.empty:
            return df
    except (Exception,) as exc:  # noqa: BLE001 - API nội bộ đổi giữa các version
        if isinstance(exc, RuntimeError) and "rate limit" in str(exc):
            raise
        logger.debug("Fallback API public cho %s/%s", stock, report_type)
    method = getattr(fin, report_type)
    try:
        return _vn_call(method, period="year", lang="vi")
    except TypeError:  # nguồn khác (KBS...) có thể không nhận lang
        return _vn_call(method, period="year")


_YEAR_RE = re.compile(r"^(19|20)\d{2}$")


def _year_columns(df: pd.DataFrame) -> list[str]:
    """Các cột dạng năm ('2025', '2024'...) trong khung xoay ngang 4.x."""
    return [c for c in df.columns if _YEAR_RE.match(str(c).strip())]


def _scalar(v: Any) -> float:
    """Ép mọi kiểu giá trị (Series do cột trùng tên, None, chuỗi...) về float."""
    if isinstance(v, pd.Series):
        v = v.dropna()
        v = v.iloc[0] if len(v) else None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return float("nan")
    return f


def _extract_metric(
    df: pd.DataFrame, *patterns: str, exclude: tuple[str, ...] = ()
) -> dict[int, float]:
    """Tìm chỉ tiêu theo pattern (không phân biệt hoa thường) và trả {năm: giá trị}.

    Hỗ trợ cả 2 định dạng vnstock:
      - 4.x xoay ngang: hàng = chỉ tiêu (item/item_en/item_id), cột = năm
      - 3.x cũ: hàng = năm, cột = chỉ tiêu
    """
    if df is None or df.empty:
        return {}
    year_cols = _year_columns(df)
    label_cols = [c for c in ("item", "item_en", "item_id") if c in df.columns]

    if year_cols and label_cols:  # ---- định dạng 4.x xoay ngang
        labels = (
            df[label_cols].astype(str).agg(" | ".join, axis=1).str.lower()
        )
        for pat in patterns:
            mask = labels.str.contains(pat.lower(), regex=False)
            for ex in exclude:
                mask &= ~labels.str.contains(ex.lower(), regex=False)
            hit = df[mask]
            if hit.empty:
                continue
            row = hit.iloc[0]
            out: dict[int, float] = {}
            # Cột năm có thể TRÙNG TÊN (VCI trộn hàng quý/năm cùng nhãn
            # "2025") -> row[yc] trả Series thay vì scalar; lấy giá trị
            # hợp lệ đầu tiên, năm đã có thì không ghi đè
            for yc in year_cols:
                v = _scalar(row[yc])
                y = int(str(yc).strip())
                if not math.isnan(v) and y not in out:
                    out[y] = v
            if out:
                return out
        return {}

    # ---- định dạng cũ: hàng = năm
    flat = {str(c).lower(): c for c in df.columns}
    year_col = next(
        (flat[k] for k in flat if k in ("năm", "year", "yearreport", "period")), None
    )
    if year_col is None:
        return {}
    years = pd.to_numeric(df[year_col], errors="coerce")
    for pat in patterns:
        for k, c in flat.items():
            if pat.lower() in k and not any(e.lower() in k for e in exclude):
                vals = pd.to_numeric(df[c], errors="coerce")
                return {
                    int(y): float(v)
                    for y, v in zip(years, vals)
                    if not (math.isnan(y) or math.isnan(v))
                }
    return {}


def _align_years(
    metrics: dict[str, dict[int, float]], max_years: int = 10
) -> tuple[list[int], dict[str, list[float]]]:
    """Hợp nhất các chỉ tiêu về cùng trục năm TĂNG DẦN (loại lỗi đảo thứ tự)."""
    all_years = sorted({y for m in metrics.values() for y in m})[-max_years:]
    aligned = {
        name: [m.get(y, float("nan")) for y in all_years]
        for name, m in metrics.items()
    }
    return all_years, aligned


def _normalize_pct(values: list[float]) -> list[float]:
    """ROIC/ROE: nguồn trả tỷ lệ (0.18) hay phần trăm (18) tùy phiên bản —
    chuẩn hóa về phần trăm dựa trên median toàn chuỗi."""
    clean = [v for v in values if not math.isnan(v)]
    if not clean:
        return values
    med = sorted(abs(v) for v in clean)[len(clean) // 2]
    if med < 3:
        return [v * 100 if not math.isnan(v) else v for v in values]
    return values


def _collect_metrics(stock: Any) -> dict[str, dict[int, float]]:
    """Trích toàn bộ chỉ tiêu 4M từ một nguồn vnstock (VCI hoặc KBS)."""
    ratio = _fetch_year_report(stock, "ratio")
    income = _fetch_year_report(stock, "income_statement")
    cash = _fetch_year_report(stock, "cash_flow")

    ocf = _extract_metric(
        cash,
        "lưu chuyển tiền thuần từ hoạt động kinh doanh",
        "net cash inflows/outflows from operating",
        "net cash flows from operating",
    )
    capex = _extract_metric(
        cash,
        "mua sắm, xây dựng tscđ",
        "mua sắm tscđ",
        "purchase of fixed assets",
        "purchases of fixed assets",
    )
    fcf = {y: ocf[y] - abs(capex.get(y, 0.0)) for y in ocf}

    return {
        "fcf": fcf,
        "revenue": _extract_metric(
            income, "doanh thu thuần", "net revenue", "net sales", "revenue"
        ),
        "eps": _extract_metric(ratio, "eps", exclude=("pha loãng", "diluted")),
        "bvps": _extract_metric(ratio, "bvps", "giá trị sổ sách", "book value"),
        "roic": _extract_metric(ratio, "roic"),
        "roe": _extract_metric(ratio, "roe"),
        "pe": _extract_metric(ratio, "p/e", exclude=("p/e pha loãng",)),
        "de": _extract_metric(
            ratio, "nợ/vcsh", "debt/equity", "nợ trên vốn chủ", "(nợ+thuê"
        ),
    }


def _vnstock_fundamentals(symbol: str) -> FundamentalSnapshot:
    """Chuỗi chỉ số năm — nguồn chính VCI, tự kiểm chứng + đối chiếu KBS.

    Vòng lặp kiểm chứng:
      1. Trích chỉ tiêu từ VCI, chuẩn hóa năm tăng dần + đơn vị
      2. Sanity check (PE hàm ý, độ phủ, vùng giá trị hợp lệ)
      3. Đối chiếu EPS với nguồn KBS độc lập (best-effort)
      4. Chấm điểm tin cậy — điểm thấp sẽ bị loại khỏi lọc tự động
    """
    from vnstock import Vnstock

    def collect(source: str) -> tuple[dict, int]:
        stock = Vnstock().stock(symbol=symbol, source=source)
        m = _collect_metrics(stock)
        coverage = sum(1 for k in ("revenue", "eps", "roe") if m.get(k))
        return m, coverage

    # Nguồn chính VCI; hỏng hoặc thiếu nặng -> tự chuyển KBS làm nguồn chính
    primary, primary_err = "VCI", None
    try:
        metrics, coverage = collect("VCI")
    except Exception as exc:  # noqa: BLE001 - API ngoài
        metrics, coverage, primary_err = {}, 0, exc
        logger.warning("VCI lỗi BCTC %s: %s", symbol, exc)
    if coverage < 2:
        try:
            metrics2, coverage2 = collect("KBS")
            if coverage2 > coverage:
                metrics, coverage, primary = metrics2, coverage2, "KBS"
                logger.info("%s: dùng KBS làm nguồn chính (VCI thiếu/lỗi)", symbol)
        except Exception as exc:  # noqa: BLE001
            logger.warning("KBS cũng lỗi BCTC %s: %s", symbol, exc)
    if not metrics or coverage == 0:
        raise RuntimeError(
            f"Không lấy được BCTC {symbol} từ cả VCI lẫn KBS"
            + (f" (VCI: {str(primary_err)[:120]})" if primary_err else "")
        )
    sources = [primary]

    # Vòng lặp kiểm chứng bước 3: nguồn độc lập thứ hai (không chặn khi lỗi)
    cross_checked, cross_ok, cross_diff = False, None, None
    second = "KBS" if primary == "VCI" else "VCI"
    try:
        stock2 = Vnstock().stock(symbol=symbol, source=second)
        eps2 = _extract_metric(
            _fetch_year_report(stock2, "ratio"),
            "eps", exclude=("pha loãng", "diluted"),
        )
        if eps2 and metrics.get("eps"):
            _, aligned2 = _align_years({"eps": eps2})
            _, aligned1 = _align_years({"eps": metrics["eps"]})
            cross_ok, cross_diff = cross_check_eps(aligned1["eps"], aligned2["eps"])
            cross_checked = cross_diff is not None
            if cross_checked:
                sources.append(second)
    except Exception:  # noqa: BLE001 - nguồn 2 chỉ để đối chiếu, không bắt buộc
        logger.info("Không đối chiếu được %s cho %s", second, symbol)

    years, series = _align_years(metrics)
    series["roic"] = _normalize_pct(series.get("roic", []))
    series["roe"] = _normalize_pct(series.get("roe", []))

    price_df = get_price_history(symbol, days=5)
    current_price = float(price_df["close"].iloc[-1]) if len(price_df) else 0.0

    def clean(name: str) -> list[float]:
        return [
            float(x) if not math.isnan(x) else 0.0 for x in series.get(name, [])
        ]

    eps_clean = clean("eps")
    eps_now = next((x for x in reversed(eps_clean) if x > 0), 0.0)

    missing, warnings = sanity_check(
        years=years,
        series_map=series,
        eps_now=eps_now,
        current_price=current_price,
    )
    if cross_checked and cross_ok is False:
        warnings.append(
            f"EPS lệch {cross_diff}% giữa VCI và KBS — cần xem lại BCTC gốc"
        )
    quality = DataQuality(
        score=score_quality(
            n_years=len(years),
            missing=missing,
            warnings=warnings,
            cross_checked=cross_checked,
            cross_check_ok=cross_ok,
        ),
        sources=sources,
        cross_checked=cross_checked,
        cross_check_diff_pct=cross_diff,
        n_years=len(years),
        missing=missing,
        warnings=warnings,
    )

    de_series = [x for x in series.get("de", []) if not math.isnan(x)]
    de_last = de_series[-1] if de_series else 0.0
    if de_last > 10:  # nguồn (KBS...) trả D/E theo % (vd 101.5) -> quy về tỷ lệ
        de_last = de_last / 100.0
    return FundamentalSnapshot(
        symbol=symbol,
        years=years,
        revenue=clean("revenue"),
        eps=eps_clean,
        bvps=clean("bvps"),
        fcf=clean("fcf"),
        roic=clean("roic"),
        roe=clean("roe"),
        debt_to_equity=de_last,
        pe_history=clean("pe"),
        current_price=current_price,
        quality=quality,
    )


# ---------------------------------------------------------------------------
# Demo mode — dữ liệu tổng hợp có kiểm soát
# ---------------------------------------------------------------------------

def _demo_price_history(
    symbol: str, days: int, base: float = 0.0, drift: float = 0.0
) -> pd.DataFrame:
    """Sinh chuỗi giá deterministic theo symbol.

    Mã 'HPG' được cấy kịch bản Minervini hoàn chỉnh: uptrend Giai đoạn 2
    mạnh (~300 phiên đầu), sau đó nền VCP 60 phiên với 3 sóng co thắt
    18% → 10% → 5%, volume cạn dần, breakout kèm volume ở phiên cuối.
    """
    rng = random.Random(symbol)  # deterministic theo mã
    p0 = base or rng.uniform(15_000, 90_000)
    drift = drift or rng.uniform(0.0004, 0.0012)
    vcp = symbol == "HPG"

    # Đường giá mục tiêu (multiplier so với p0) — điều khiển hoàn toàn
    path: list[tuple[float, float]] = []  # (multiplier, volume)
    if vcp:
        up_len = days - 60
        for i in range(up_len):  # uptrend +75% có nhịp
            trend = 1.0 + 0.75 * i / up_len
            wobble = 1 + 0.03 * math.sin(i / 9)
            path.append((trend * wobble, rng.uniform(1.2e6, 2.6e6)))
        top = path[-1][0]
        waves = [(24, 0.18, 1.8e6), (18, 0.10, 1.1e6), (14, 0.05, 0.65e6)]
        for length, depth, vol in waves:  # 3 sóng co thắt
            for k in range(length):
                m = top * (1 - depth * math.sin(math.pi * k / length))
                path.append((m, vol * rng.uniform(0.85, 1.15)))
        for _ in range(3):  # nền chặt sát pivot, volume kiệt
            path.append((top * 0.995, rng.uniform(0.4e6, 0.55e6)))
        path.append((top * 1.04, 4.5e6))  # breakout + volume bùng nổ
    else:
        m = 1.0
        for _ in range(days):
            m *= 1 + drift + rng.gauss(0, 0.014)
            path.append((m, rng.uniform(0.8e6, 2.5e6)))

    rows: list[dict[str, Any]] = []
    d = date.today() - timedelta(days=int(days * 1.55))
    for mult, vol in path[:days]:
        d += timedelta(days=1)
        while d.weekday() >= 5:
            d += timedelta(days=1)
        price = p0 * mult * (1 + rng.gauss(0, 0.002))
        o = price * (1 + rng.gauss(0, 0.003))
        h = max(o, price) * (1 + abs(rng.gauss(0, 0.004)))
        low = min(o, price) * (1 - abs(rng.gauss(0, 0.004)))
        rows.append(
            {
                "time": d.isoformat(),
                "open": round(o, 2),
                "high": round(h, 2),
                "low": round(low, 2),
                "close": round(price, 2),
                "volume": int(vol),
            }
        )
    return pd.DataFrame(rows)


def _demo_fundamentals(symbol: str) -> FundamentalSnapshot:
    """Sinh chuỗi 4M deterministic, EPS calibrate theo giá demo để định giá
    Rule #1 cho kết quả thực tế: HPG rẻ (on sale), FPT/MWG quanh fair value.
    """
    rng = random.Random(symbol + "-fund")
    strong = symbol in {"HPG", "FPT", "MWG"}
    g = rng.uniform(0.16, 0.22) if strong else rng.uniform(-0.02, 0.09)
    this_year = date.today().year
    years = list(range(this_year - 9, this_year + 1))

    price_df = _demo_price_history(symbol, 260)
    current_price = float(price_df["close"].iloc[-1])
    # PE hiện tại quyết định mức "rẻ": HPG PE 7 (on sale), strong khác PE 15
    pe_now = 7.0 if symbol == "HPG" else (15.0 if strong else 22.0)
    eps_now = current_price / pe_now

    def series_to(final: float, growth: float, noise: float = 0.02) -> list[float]:
        """Chuỗi 10 năm kết thúc tại `final` với CAGR ~growth (sinh ngược)."""
        vals = [final]
        for _ in range(len(years) - 1):
            vals.append(vals[-1] / (1 + growth + rng.gauss(0, noise)))
        return [round(v, 2) for v in reversed(vals)]

    return FundamentalSnapshot(
        symbol=symbol,
        years=years,
        revenue=series_to(45_000, g),
        eps=series_to(eps_now, g),
        bvps=series_to(current_price * 0.8, g * 0.8),
        fcf=series_to(6_500, g, noise=0.06),
        roic=[round(rng.uniform(12, 22) if strong else rng.uniform(3, 9), 1) for _ in years],
        roe=[round(rng.uniform(16, 26) if strong else rng.uniform(5, 12), 1) for _ in years],
        debt_to_equity=round(rng.uniform(0.2, 0.8) if strong else rng.uniform(1.2, 2.5), 2),
        pe_history=[round(pe_now * rng.uniform(0.85, 1.25), 1) for _ in years],
        current_price=current_price,
        industry="Demo",
    )
