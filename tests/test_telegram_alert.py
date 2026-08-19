"""Smoke test cho app/services/telegram_alert.py — chỉ test đường dry-run
(chưa cấu hình token/chat_id), không gọi mạng thật.
"""

from __future__ import annotations

import sys
import unittest
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.config import settings
from app.services import telegram_alert


@dataclass
class FakeVCP:
    last_close: float = 21000.0
    pivot: float = 20500.0
    stop_loss: float = 19000.0


@dataclass
class FakeRec:
    symbol: str
    action: str
    conviction: int = 80
    vcp: FakeVCP = field(default_factory=FakeVCP)
    reasons: list = field(default_factory=lambda: ["Breakout pivot với volume 2.0x TB50"])


class TestTelegramDryRun(unittest.TestCase):
    def setUp(self):
        # Đảm bảo môi trường test không có token thật -> ép dry-run
        object.__setattr__(settings, "telegram_bot_token", "")
        object.__setattr__(settings, "telegram_chat_id", "")
        if settings.alerted_buys_path.exists():
            settings.alerted_buys_path.unlink()

    def tearDown(self):
        if settings.alerted_buys_path.exists():
            settings.alerted_buys_path.unlink()

    def test_chua_cau_hinh_thi_khong_gui_that(self):
        self.assertFalse(telegram_alert.is_configured())
        self.assertFalse(telegram_alert.send_message("test"))

    def test_khong_crash_khi_thieu_config_va_van_ghi_nhan_da_xu_ly(self):
        recs = [FakeRec(symbol="HPG", action="MUA"), FakeRec(symbol="FPT", action="THEO DÕI")]
        alerted = telegram_alert.notify_new_buy_signals(recs)
        self.assertEqual(alerted, ["HPG"])  # chỉ mã MUA mới được xử lý

    def test_khong_bao_lai_ma_da_alert(self):
        recs = [FakeRec(symbol="HPG", action="MUA")]
        first = telegram_alert.notify_new_buy_signals(recs)
        second = telegram_alert.notify_new_buy_signals(recs)
        self.assertEqual(first, ["HPG"])
        self.assertEqual(second, [])  # đã báo rồi, không báo lại

    def test_format_buy_alert_khong_loi(self):
        rec = FakeRec(symbol="HPG", action="MUA")
        text = telegram_alert.format_buy_alert(rec)
        self.assertIn("HPG", text)
        self.assertIn("Conviction", text)


if __name__ == "__main__":
    unittest.main()
