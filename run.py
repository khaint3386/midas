"""Điểm khởi động Midas 3.0: python run.py

Tự kiểm tra cổng 8386 trước khi chạy — nếu một phiên Midas cũ còn chiếm
cổng, server mới sẽ KHÔNG khởi động được ([Errno 10048]) và trình duyệt
sẽ nói chuyện với code CŨ (gây lỗi khó hiểu như Method Not Allowed).
"""

from __future__ import annotations

import socket
import sys

import uvicorn

from app import create_app

PORT = 8386

app = create_app()


def _port_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(("127.0.0.1", port)) != 0


if __name__ == "__main__":
    if not _port_free(PORT):
        print("=" * 60)
        print(f"[LOI] Cong {PORT} dang bi mot tien trinh khac chiem!")
        print("Thuong la mot cua so Midas CU van dang chay ngam.")
        print()
        print("Cach xu ly: dong cua so Midas cu, hoac chay lenh:")
        print(f'  for /f "tokens=5" %p in (\'netstat -ano ^| findstr :{PORT}\')'
              " do taskkill /F /PID %p")
        print()
        print("Roi chay lai start_midas.bat. (start_midas.bat moi da tu lam viec nay)")
        print("=" * 60)
        sys.exit(1)
    uvicorn.run("run:app", host="127.0.0.1", port=PORT, reload=False)
