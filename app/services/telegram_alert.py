"""Cảnh báo Telegram khi có tín hiệu MUA mới.

Thiết kế tối giản, không thêm dependency (dùng urllib có sẵn trong stdlib
thay vì requests — Midas chưa khai báo requests trong requirements.txt).

Chưa cấu hình TELEGRAM_BOT_TOKEN/TELEGRAM_CHAT_ID -> dry-run: chỉ log ra
console, không gửi thật, KHÔNG làm chết luồng quét (giống hành vi
smart_alert_bot/telegram_notifier.py để nhất quán trong hệ thống).

Chống spam: chỉ gửi cảnh báo cho mã CHƯA từng được báo (lưu trong
`data/alerted_buys.json`). Muốn báo lại từ đầu, xóa file này.
"""

from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request

from app.config import settings

logger = logging.getLogger(__name__)

_API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def is_configured() -> bool:
    return bool(settings.telegram_bot_token and settings.telegram_chat_id)


def send_message(text: str) -> bool:
    """Gửi 1 tin nhắn Telegram. Trả True nếu gửi thành công (hoặc dry-run)."""
    if not is_configured():
        logger.info("[Telegram DRY-RUN — chưa cấu hình token/chat_id]\n%s", text)
        return False

    url = _API_URL.format(token=settings.telegram_bot_token)
    payload = json.dumps(
        {"chat_id": settings.telegram_chat_id, "text": text, "parse_mode": "HTML"}
    ).encode("utf-8")
    req = urllib.request.Request(
        url, data=payload, headers={"Content-Type": "application/json"}, method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return 200 <= resp.status < 300
    except (urllib.error.URLError, TimeoutError) as exc:
        logger.warning("Gửi Telegram thất bại: %s", exc)
        return False


def format_buy_alert(rec) -> str:
    """Định dạng tin nhắn cho 1 khuyến nghị MUA (nhận Recommendation)."""
    v = rec.vcp
    lines = [
        f"🟢 <b>TÍN HIỆU MUA — {rec.symbol}</b>",
        f"Conviction: {rec.conviction}/100",
        f"Giá hiện tại: {v.last_close:,.0f} VND | Pivot: {v.pivot:,.0f} | "
        f"Stop-loss: {v.stop_loss:,.0f}",
    ]
    if rec.reasons:
        lines.append("")
        lines.extend(f"• {r}" for r in rec.reasons[:4])
    lines.append("\n<i>Thông tin hỗ trợ quyết định, không phải lời khuyên đầu tư.</i>")
    return "\n".join(lines)


def _load_alerted() -> set[str]:
    try:
        return set(json.loads(settings.alerted_buys_path.read_text(encoding="utf-8")))
    except (OSError, json.JSONDecodeError):
        return set()


def _save_alerted(symbols: set[str]) -> None:
    settings.alerted_buys_path.write_text(
        json.dumps(sorted(symbols), ensure_ascii=False), encoding="utf-8"
    )


def notify_new_buy_signals(recommendations: list) -> list[str]:
    """Gửi cảnh báo cho các mã MUA CHƯA từng được báo trước đó.

    Trả về danh sách mã vừa gửi cảnh báo (rỗng nếu không có mã mới hoặc lỗi).
    Không bao giờ raise — lỗi gửi Telegram không được làm hỏng kết quả quét.
    """
    try:
        already = _load_alerted()
        new_buys = [
            r for r in recommendations
            if r.action == "MUA" and r.symbol not in already
        ]
        sent: list[str] = []
        for rec in new_buys:
            if send_message(format_buy_alert(rec)) or not is_configured():
                # Dry-run (chưa cấu hình) vẫn tính là "đã xử lý" để không log lặp
                sent.append(rec.symbol)
                already.add(rec.symbol)
        if sent:
            _save_alerted(already)
        return sent
    except Exception:  # noqa: BLE001 - cảnh báo là phụ, không được chặn /scan
        logger.exception("Lỗi khi xử lý cảnh báo Telegram")
        return []
