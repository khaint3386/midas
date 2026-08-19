"""Lọc tuần tự động — chọn TOP 12 mã cho watchlist Midas.

Chạy:
  .venv\\Scripts\\python loc_tuan.py [nhom]     (mặc định VN100)

Được Windows Task Scheduler gọi mỗi sáng thứ 7 (xem dat_lich_quet_tuan.bat).
"""

from __future__ import annotations

import sys
import threading
import time

from app.services import watchlist_builder
from app.services.watchlist_builder import BUILD_STATE


def main(group: str = "VN100") -> None:
    print(f"Midas 3.0 — Lọc tuần nhóm {group}: 60% 4M (Phil Town) + 40% VCP (Minervini)")
    print("Watchlist sẽ được THAY HOÀN TOÀN bằng TOP 12 điểm cao nhất.\n")

    done = threading.Event()
    result: dict = {}

    def run() -> None:
        try:
            result["ranked"] = watchlist_builder.build_weekly_watchlist(group)
        except Exception as exc:  # noqa: BLE001
            result["error"] = exc
        finally:
            done.set()

    threading.Thread(target=run, daemon=True).start()
    last = ""
    while not done.wait(2.0):
        msg = f"  {BUILD_STATE['stage']} — {BUILD_STATE['done']}/{BUILD_STATE['total']}"
        if msg != last:
            print(msg)
            last = msg

    if "error" in result:
        print(f"\nLỖI: {result['error']}")
        sys.exit(1)

    ranked = result["ranked"]
    selected = [c for c in ranked if not c.excluded_reason][:12]
    print(f"\n{'=' * 60}\nWATCHLIST MỚI ({len(selected)} mã):")
    for i, c in enumerate(selected, 1):
        print(
            f"  {i:2d}. {c.symbol:6s} composite {c.composite:5.1f} "
            f"(4M {c.four_m_score:5.1f} · VCP {c.vcp_score:3d} · RS {c.rs_rating})"
        )
    print(f"\nBáo cáo: {BUILD_STATE['report_path']}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "VN100")
