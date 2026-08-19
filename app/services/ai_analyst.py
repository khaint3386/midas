"""AI Analyst — đánh giá Meaning (4M) và đọc tin tức bằng Gemini.

Không có GEMINI_API_KEY → fallback rule-based, hệ thống vẫn chạy đầy đủ.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

from app.config import settings
from app.services.news_feed import NewsItem

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class MeaningAssessment:
    symbol: str
    summary: str
    sentiment: str          # "tích cực" | "trung lập" | "tiêu cực"
    meaning_score: int      # 0-100
    ai_powered: bool
    verification_note: str = ""   # kết quả đối chiếu chéo nguồn tin
    corroborated: bool = True     # sentiment đã được ≥2 nguồn xác nhận?


_PROMPT = """Bạn là chuyên gia phân tích đầu tư theo phương pháp Rule #1 của Phil Town.
Đánh giá chữ M đầu tiên (Meaning) cho cổ phiếu {symbol} trên HOSE dựa trên các tin tức sau:

{news}

Trả lời NGẮN GỌN bằng tiếng Việt theo đúng định dạng:
SENTIMENT: [tích cực|trung lập|tiêu cực]
SCORE: [0-100, mức độ dễ hiểu và triển vọng dài hạn của ngành/doanh nghiệp]
SUMMARY: [2-3 câu: doanh nghiệp làm gì, tin tức nói lên điều gì về triển vọng dài hạn]
Chỉ dựa trên tin đã cho, không bịa thông tin."""


def assess_meaning(symbol: str, news: list[NewsItem]) -> MeaningAssessment:
    """Đánh giá Meaning kèm VÒNG KIỂM CHỨNG tin tức.

    Sentiment chỉ được giữ nguyên khi tin đã đối chiếu chéo ≥2 nguồn chính
    thống độc lập; ngược lại kéo điểm về trung lập (giảm 1/2 độ lệch so 50)
    — tránh khuyến nghị dựa trên tin đơn nguồn chưa xác thực.
    """
    from app.services.news_feed import verify_news

    if settings.gemini_api_key:
        try:
            result = _gemini_assess(symbol, news)
        except Exception:  # noqa: BLE001 - API ngoài có thể lỗi bất kỳ
            logger.exception("Gemini lỗi, chuyển sang rule-based cho %s", symbol)
            result = _rule_based_assess(symbol, news)
    else:
        result = _rule_based_assess(symbol, news)

    verification = verify_news(news)
    score = result.meaning_score
    sentiment = result.sentiment
    if not verification.corroborated and news:
        score = 50 + (score - 50) // 2  # kéo về trung lập
        if abs(score - 50) < 8:
            sentiment = "trung lập"
    elif not news:
        score, sentiment = 50, "trung lập"

    return MeaningAssessment(
        symbol=result.symbol,
        summary=result.summary,
        sentiment=sentiment,
        meaning_score=score,
        ai_powered=result.ai_powered,
        verification_note=verification.note,
        corroborated=verification.corroborated,
    )


def _gemini_assess(symbol: str, news: list[NewsItem]) -> MeaningAssessment:
    from google import genai

    client = genai.Client(api_key=settings.gemini_api_key)
    news_text = "\n".join(f"- {n.title} ({n.source}): {n.summary}" for n in news[:10])
    resp = client.models.generate_content(
        model=settings.gemini_model,
        contents=_PROMPT.format(symbol=symbol, news=news_text or "(không có tin)"),
    )
    text = resp.text or ""
    sentiment, score, summary = "trung lập", 50, text.strip()[:400]
    for line in text.splitlines():
        upper = line.upper()
        if upper.startswith("SENTIMENT:"):
            sentiment = line.split(":", 1)[1].strip().lower()
        elif upper.startswith("SCORE:"):
            digits = "".join(c for c in line.split(":", 1)[1] if c.isdigit())
            score = min(int(digits or 50), 100)
        elif upper.startswith("SUMMARY:"):
            summary = line.split(":", 1)[1].strip()
    return MeaningAssessment(
        symbol=symbol, summary=summary, sentiment=sentiment,
        meaning_score=score, ai_powered=True,
    )


_POSITIVE = ("tăng", "lãi", "kỷ lục", "mở rộng", "mua ròng", "chấp thuận", "vượt")
_NEGATIVE = ("giảm", "lỗ", "phạt", "thoái vốn", "bán ròng", "khó khăn", "rủi ro")


def _rule_based_assess(symbol: str, news: list[NewsItem]) -> MeaningAssessment:
    """Đếm từ khóa tích cực/tiêu cực trong tiêu đề — fallback khi chưa có AI."""
    pos = neg = 0
    for n in news:
        title = n.title.lower()
        pos += sum(1 for w in _POSITIVE if w in title)
        neg += sum(1 for w in _NEGATIVE if w in title)
    if pos > neg:
        sentiment, score = "tích cực", min(60 + (pos - neg) * 8, 90)
    elif neg > pos:
        sentiment, score = "tiêu cực", max(40 - (neg - pos) * 8, 10)
    else:
        sentiment, score = "trung lập", 50
    summary = (
        f"Phân tích {len(news)} tin gần nhất về {symbol} (rule-based, chưa có Gemini key): "
        f"{pos} tín hiệu tích cực, {neg} tiêu cực."
    )
    return MeaningAssessment(
        symbol=symbol, summary=summary, sentiment=sentiment,
        meaning_score=score, ai_powered=False,
    )
