"""API routers — giữ thin theo chuẩn fastapi.md, logic nằm ở services."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import market_data
from app.services.recommender import analyze_symbol, scan_watchlist

router = APIRouter(prefix="/api/v1")
_executor = ThreadPoolExecutor(max_workers=4)


class WatchlistUpdate(BaseModel):
    symbol: str


class HealthResponse(BaseModel):
    status: str
    demo_mode: bool
    watchlist_size: int


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    from app.config import settings

    return HealthResponse(
        status="ok",
        demo_mode=settings.demo_mode,
        watchlist_size=len(market_data.load_watchlist()),
    )


@router.get("/diagnose")
def diagnose() -> dict:
    """Tự kiểm tra môi trường — giúp chẩn đoán khi quét lỗi."""
    import importlib
    import sys

    from app.config import settings

    checks: dict[str, dict] = {}

    def check_module(name: str, required_for: str) -> None:
        try:
            mod = importlib.import_module(name)
            checks[name] = {
                "ok": True,
                "version": getattr(mod, "__version__", "?"),
                "required_for": required_for,
            }
        except ImportError as exc:
            checks[name] = {"ok": False, "error": str(exc), "required_for": required_for}

    check_module("vnstock", "dữ liệu giá + BCTC (bắt buộc khi không demo)")
    check_module("feedparser", "tin tức RSS")
    check_module("pandas", "xử lý dữ liệu (bắt buộc)")

    # Thử pipeline thật từng bước (1 mã) nếu không demo — trả traceback
    # đầy đủ để biết chính xác hỏng ở khâu nào: giá, BCTC hay tin tức
    import traceback

    data_test: dict = {"ok": None, "detail": "bỏ qua (demo mode)"}
    fund_test: dict = {"ok": None, "detail": "bỏ qua (demo mode)"}
    news_test: dict = {"ok": None, "detail": "bỏ qua (demo mode)"}
    if not settings.demo_mode and checks.get("vnstock", {}).get("ok"):
        try:
            df = market_data.get_price_history("FPT", days=10)
            data_test = {"ok": len(df) > 0, "detail": f"tải được {len(df)} phiên FPT"}
        except Exception:  # noqa: BLE001
            data_test = {"ok": False, "traceback": traceback.format_exc()[-1500:]}
        try:
            snap = market_data.get_fundamentals("FPT")
            fund_test = {
                "ok": bool(snap.years),
                "years": snap.years,
                "eps_3_nam_cuoi": snap.eps[-3:],
                "roe_3_nam_cuoi": snap.roe[-3:],
                "quality": snap.quality.to_dict() if snap.quality else None,
            }
        except Exception:  # noqa: BLE001
            fund_test = {"ok": False, "traceback": traceback.format_exc()[-1500:]}
        try:
            from app.services.news_feed import fetch_news

            items = fetch_news("FPT", limit=5)
            news_test = {"ok": True, "so_tin": len(items)}
        except Exception:  # noqa: BLE001
            news_test = {"ok": False, "traceback": traceback.format_exc()[-800:]}

    from app.services.watchlist_builder import BUILD_STATE

    from app.services.telegram_alert import is_configured as telegram_configured

    return _json_safe({
        "python": sys.version.split()[0],
        "demo_mode": settings.demo_mode,
        "gemini_key_configured": bool(settings.gemini_api_key),
        "telegram_configured": telegram_configured(),
        "watchlist": market_data.load_watchlist(),
        "modules": checks,
        "live_data_test": data_test,
        "fundamentals_test": fund_test,
        "news_test": news_test,
        "rebuild_state": dict(BUILD_STATE),
    })


@router.get("/watchlist")
def get_watchlist() -> dict:
    return {"watchlist": market_data.load_watchlist()}


@router.post("/watchlist")
def add_symbol(body: WatchlistUpdate) -> dict:
    symbols = market_data.load_watchlist()
    symbol = body.symbol.upper().strip()
    if not symbol.isalnum() or len(symbol) > 10:
        raise HTTPException(status_code=422, detail="Mã không hợp lệ")
    if symbol not in symbols:
        symbols.append(symbol)
        market_data.save_watchlist(symbols)
    return {"watchlist": market_data.load_watchlist()}


@router.delete("/watchlist/{symbol}")
def remove_symbol(symbol: str) -> dict:
    symbols = [s for s in market_data.load_watchlist() if s != symbol.upper()]
    market_data.save_watchlist(symbols)
    return {"watchlist": symbols}


@router.post("/watchlist/rebuild")
def rebuild_watchlist(group: str = "VN100") -> dict:
    """Kích hoạt lọc tuần: quét nhóm, chọn TOP 12 thay watchlist (chạy nền)."""
    from app.services import watchlist_builder

    started = watchlist_builder.start_background_build(group)
    if not started:
        raise HTTPException(status_code=409, detail="Đang có phiên lọc chạy")
    return {"started": True, "group": group}


@router.get("/watchlist/rebuild/status")
def rebuild_status() -> dict:
    from app.services.watchlist_builder import BUILD_STATE

    return _json_safe(dict(BUILD_STATE))


@router.get("/scan")
def scan() -> dict:
    """Quét toàn watchlist — trả khuyến nghị đã xếp hạng.

    _json_safe bắt buộc: một giá trị NaN lọt qua là serialize sập -> HTTP 500.
    """
    recs = scan_watchlist()
    from app.services.telegram_alert import notify_new_buy_signals

    alerted = notify_new_buy_signals(recs)
    return _json_safe(
        {
            "count": len(recs),
            "recommendations": [r.to_dict() for r in recs],
            "telegram_alerted": alerted,
        }
    )


def _json_safe(obj):
    """Thay float không hữu hạn (NaN/inf) bằng None — JSON không chấp nhận."""
    import math as _m

    if isinstance(obj, float):
        return obj if _m.isfinite(obj) else None
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(x) for x in obj]
    return obj


@router.get("/analysis/{symbol}")
def analysis(symbol: str) -> dict:
    try:
        return _json_safe(analyze_symbol(symbol).to_dict())
    # SystemExit: vnai (vnstock) gọi sys.exit khi vượt rate-limit — nếu chỉ
    # bắt Exception thì endpoint sập thành HTTP 500 không kèm thông báo
    except (Exception, SystemExit) as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Không phân tích được {symbol}: {exc}")


@router.get("/chart/{symbol}")
def chart(symbol: str, days: int = 260) -> dict:
    try:
        df = market_data.get_price_history(symbol.upper(), days=days)
        return {"symbol": symbol.upper(), "candles": _json_safe(df.to_dict(orient="records"))}
    except (Exception, SystemExit) as exc:  # noqa: BLE001
        raise HTTPException(status_code=502, detail=f"Không tải được biểu đồ {symbol}: {exc}")
