"""Luồng tin tức có kiểm chứng — chỉ nguồn chính thống, đối chiếu chéo.

Chống tin giả / tin thiếu xác thực:
  1. WHITELIST cứng: chỉ đọc RSS từ báo kinh tế - tài chính chính thống
     (CafeF, VnEconomy, Vietstock, VnExpress); URL đã xác minh hoạt động.
  2. Khớp mã theo TỪ NGUYÊN (word-boundary) — mã "CTD" không còn khớp nhầm
     chuỗi con trong từ khác.
  3. Khử trùng lặp tiêu đề giữa các nguồn.
  4. Đếm số NGUỒN ĐỘC LẬP nhắc tới mã: tin chỉ xuất hiện ở 1 nguồn được
     đánh dấu corroborated=False để tầng Meaning hạ trọng số.
"""

from __future__ import annotations

import logging
import re
import unicodedata
from dataclasses import dataclass

from app.config import settings

logger = logging.getLogger(__name__)

# URL đã kiểm chứng hoạt động (04/07/2026). Nguồn lỗi sẽ tự bỏ qua, không chặn.
RSS_SOURCES: dict[str, str] = {
    "CafeF Chứng khoán": "https://cafef.vn/thi-truong-chung-khoan.rss",
    "CafeF Doanh nghiệp": "https://cafef.vn/doanh-nghiep.rss",
    "VnEconomy Chứng khoán": "https://vneconomy.vn/chung-khoan.rss",
    "Vietstock Cổ phiếu": "https://vietstock.vn/830/chung-khoan/co-phieu.rss",
    "VnExpress Kinh doanh": "https://vnexpress.net/rss/kinh-doanh.rss",
}

# Domain hợp lệ — chặn trường hợp feed bị chèn link lạ
_TRUSTED_DOMAINS = ("cafef.vn", "vneconomy.vn", "vietstock.vn", "vnexpress.net")


@dataclass(frozen=True)
class NewsItem:
    title: str
    link: str
    published: str
    source: str
    summary: str = ""


@dataclass(frozen=True)
class NewsVerification:
    """Kết quả kiểm chứng chéo tin tức của một mã."""

    n_items: int
    n_sources: int          # số nguồn độc lập nhắc tới mã
    corroborated: bool      # ≥2 nguồn độc lập
    note: str


def _norm_title(title: str) -> str:
    """Chuẩn hóa tiêu đề để so trùng: bỏ dấu, thường hóa, bỏ ký tự thừa."""
    t = unicodedata.normalize("NFD", title.lower())
    t = "".join(c for c in t if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9 ]+", " ", t).strip()


def _mentions_symbol(item: NewsItem, symbol: str) -> bool:
    """Khớp mã theo từ nguyên: 'CTD' phải đứng riêng, không phải chuỗi con."""
    pattern = re.compile(rf"(?<![A-Z0-9]){re.escape(symbol)}(?![A-Z0-9])")
    return bool(
        pattern.search(item.title.upper()) or pattern.search(item.summary.upper())
    )


def _trusted(link: str) -> bool:
    return any(d in link for d in _TRUSTED_DOMAINS) or not link


_FEED_CACHE: dict[str, object] = {"ts": 0.0, "items": []}
_FEED_CACHE_TTL = 900.0  # 15 phút — quét hàng loạt không dội lại nguồn RSS


def fetch_news(symbol: str | None = None, limit: int = 30) -> list[NewsItem]:
    """Lấy tin mới nhất từ whitelist; nếu có symbol thì lọc theo từ nguyên."""
    if settings.demo_mode:
        return _demo_news(symbol, limit)

    import time

    now = time.monotonic()
    if now - float(_FEED_CACHE["ts"]) < _FEED_CACHE_TTL:
        items = list(_FEED_CACHE["items"])  # type: ignore[arg-type]
        if symbol:
            items = [i for i in items if _mentions_symbol(i, symbol.upper())]
        return items[:limit]

    import feedparser

    items: list[NewsItem] = []
    seen_titles: set[str] = set()
    for source, url in RSS_SOURCES.items():
        try:
            feed = feedparser.parse(url)
            for e in feed.entries[:40]:
                link = e.get("link", "")
                if not _trusted(link):
                    continue  # link ngoài whitelist — bỏ, không tin
                title = e.get("title", "")
                key = _norm_title(title)
                if key in seen_titles:
                    continue  # tin trùng giữa các nguồn
                seen_titles.add(key)
                items.append(
                    NewsItem(
                        title=title,
                        link=link,
                        published=e.get("published", ""),
                        source=source,
                        summary=re.sub(r"<[^>]+>", "", e.get("summary", ""))[:400],
                    )
                )
        except Exception:  # noqa: BLE001 - nguồn RSS bên ngoài, không tin cậy
            logger.warning("Không đọc được RSS %s", source)

    _FEED_CACHE["ts"], _FEED_CACHE["items"] = now, list(items)

    if symbol:
        items = [i for i in items if _mentions_symbol(i, symbol.upper())]
    return items[:limit]


def verify_news(items: list[NewsItem]) -> NewsVerification:
    """Đối chiếu chéo: tin về mã được mấy nguồn độc lập xác nhận?"""
    outlets = {i.source.split()[0] for i in items}  # CafeF x2 chuyên mục = 1 nguồn
    n_sources = len(outlets)
    corroborated = n_sources >= 2
    if not items:
        note = "Không có tin từ nguồn chính thống — Meaning chấm trung lập"
    elif corroborated:
        note = f"Tin được {n_sources} nguồn chính thống độc lập đăng tải"
    else:
        note = "Tin chỉ từ 1 nguồn — chưa đối chiếu chéo được, hạ trọng số sentiment"
    return NewsVerification(
        n_items=len(items), n_sources=n_sources, corroborated=corroborated, note=note
    )


def _demo_news(symbol: str | None, limit: int) -> list[NewsItem]:
    sym = symbol or "HPG"
    samples = [
        NewsItem(
            title=f"{sym}: Lợi nhuận quý II tăng 32% nhờ giá bán cải thiện",
            link="https://cafef.vn/demo-1",
            published="2026-07-01",
            source="CafeF Doanh nghiệp",
            summary=f"Doanh nghiệp {sym} công bố KQKD quý II với biên lợi nhuận gộp mở rộng...",
        ),
        NewsItem(
            title=f"Khối ngoại mua ròng {sym} phiên thứ 5 liên tiếp",
            link="https://vneconomy.vn/demo-2",
            published="2026-06-30",
            source="VnEconomy Chứng khoán",
            summary="Dòng tiền tổ chức duy trì trạng thái tích lũy...",
        ),
        NewsItem(
            title=f"{sym} được chấp thuận mở rộng nhà máy giai đoạn 3",
            link="https://vietstock.vn/demo-3",
            published="2026-06-28",
            source="Vietstock Cổ phiếu",
            summary="Dự án dự kiến nâng công suất thêm 40% từ 2027...",
        ),
    ]
    return samples[:limit]
