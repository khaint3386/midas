"""Midas 3.0 — công cụ khuyến nghị đầu tư 4M (Phil Town) + VCP (Minervini)."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from fastapi import FastAPI


def create_app() -> "FastAPI":
    # Import trễ để app.services dùng được độc lập (test engine không cần fastapi)
    from fastapi import FastAPI
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles

    from app.config import WEB_DIR
    from app.routers.api import router

    app = FastAPI(
        title="Midas 3.0",
        description=(
            "Khuyến nghị dài hạn cho chứng khoán Việt Nam: chọn lọc cổ phiếu "
            "theo 4M của Phil Town, xác định điểm mua/bán theo VCP của Mark Minervini. "
            "Thông tin hỗ trợ quyết định — không phải lời khuyên đầu tư."
        ),
        version="3.0.0",
    )
    app.include_router(router)
    app.mount("/static", StaticFiles(directory=str(WEB_DIR)), name="static")

    @app.get("/", include_in_schema=False)
    def index() -> FileResponse:
        return FileResponse(WEB_DIR / "index.html")

    return app
