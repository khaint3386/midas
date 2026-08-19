"""Cấu hình trung tâm cho Midas 3.0."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
WEB_DIR = BASE_DIR / "web"


@dataclass(frozen=True)
class Settings:
    """Thiết lập ứng dụng — bất biến sau khi khởi tạo."""

    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = field(
        default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    )
    demo_mode: bool = field(
        default_factory=lambda: os.getenv("MIDAS_DEMO", "0") == "1"
    )
    telegram_bot_token: str = field(
        default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", "")
    )
    telegram_chat_id: str = field(
        default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", "")
    )
    # Rule #1 (Phil Town): tỷ suất hoàn vốn tối thiểu 15%/năm
    marr: float = 0.15
    # Biên an toàn 50% trên sticker price
    margin_of_safety: float = 0.50
    # Minervini: cắt lỗ tối đa 8%
    max_stop_loss_pct: float = 0.08
    # RS rating tối thiểu cho Trend Template
    min_rs_rating: int = 70

    @property
    def watchlist_path(self) -> Path:
        return DATA_DIR / "watchlist.json"

    @property
    def alerted_buys_path(self) -> Path:
        return DATA_DIR / "alerted_buys.json"


settings = Settings()
