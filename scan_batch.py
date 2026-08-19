"""Quét hàng loạt theo nhóm — lọc ứng viên VCP tiềm năng (Minervini).

Chạy:
  .venv\\Scripts\\python scan_batch.py [diem_toi_thieu] [nhom]

  nhom: WATCHLIST (mặc định) | VN30 | VN100 | HOSE | HNX30

Chiến lược 2 giai đoạn (tiết kiệm API, đúng tinh thần SEPA):
  1. Quét KỸ THUẬT toàn bộ nhóm (chỉ cần dữ liệu giá — nhẹ, nhanh)
  2. Phân tích ĐẦY ĐỦ 4M + tin tức chỉ cho các mã đạt ngưỡng điểm VCP
"""

from __future__ import annotations

import sys
import time
from datetime import datetime

from app.config import settings
from app.services import market_data
from app.services.recommender import analyze_symbol
from app.services.vcp import detect_vcp

DELAY_BETWEEN_CALLS = 0.8  # giây — tránh rate-limit VCI


def get_group_symbols(group: str) -> list[str]:
    """Lấy danh sách mã theo nhóm. Demo mode dùng watchlist."""
    group = group.upper()
    if group == "WATCHLIST" or settings.demo_mode:
        return market_data.load_watchlist()

    from vnstock import Listing

    listing = Listing()
    if group in ("VN30", "VN100", "HNX30", "VNMIDCAP", "VNSMALLCAP"):
        s = listing.symbols_by_group(group)
        return [str(x).upper() for x in list(s)]
    if group in ("HOSE", "HSX"):
        df = listing.symbols_by_exchange()
        cols = {str(c).lower(): c for c in df.columns}
        ex_col = next((cols[k] for k in cols if "exchange" in k or "san" in k), None)
        sym_col = next((cols[k] for k in cols if "symbol" in k or "ticker" in k), None)
        type_col = next((cols[k] for k in cols if "type" in k or "loai" in k), None)
        if not (ex_col and sym_col):
            raise RuntimeError(f"Không nhận diện được cột listing: {list(df.columns)}")
        mask = df[ex_col].astype(str).str.upper().isin(["HSX", "HOSE"])
        if type_col is not None:
            mask &= df[type_col].astype(str).str.upper().str.contains("STOCK", na=False)
        symbols = [str(x).upper() for x in df.loc[mask, sym_col]]
        return [s for s in symbols if len(s) == 3 and s.isalpha()]  # loại CW/ETF/trái phiếu
    raise ValueError(f"Nhóm không hỗ trợ: {group}")


def technical_scan(symbol: str) -> dict:
    """Giai đoạn 1: chỉ kỹ thuật — 1 call giá / mã (index đã cache)."""
    price_df = market_data.get_price_history(symbol)
    index_df = market_data.get_index_history()
    v = detect_vcp(symbol, price_df, index_df)
    return {
        "symbol": symbol,
        "score": v.potential_score,
        "trend": v.trend.passed_count,
        "rs": v.trend.rs_rating,
        "waves": " → ".join(f"{c.depth_pct}%" for c in v.contractions) or "—",
        "pivot": v.pivot,
        "close": v.last_close,
        "dry_up": v.volume_dry_up,
        "is_vcp": v.is_vcp,
        "buy_signal": v.buy_signal,
    }


def main(min_score: int = 60, group: str = "WATCHLIST") -> None:
    try:
        symbols = get_group_symbols(group)
    except Exception as exc:  # noqa: BLE001
        print(f"LỖI lấy danh sách {group}: {exc}")
        sys.exit(1)

    print(f"Midas 3.0 — GIAI ĐOẠN 1: quét kỹ thuật {len(symbols)} mã nhóm {group}")
    print(f"(ước tính ~{len(symbols) * (DELAY_BETWEEN_CALLS + 1.2) / 60:.0f} phút)\n")

    stage1, failed = [], []
    for i, sym in enumerate(symbols, 1):
        try:
            row = technical_scan(sym)
            stage1.append(row)
            flag = " ★" if row["score"] >= min_score else ""
            print(f"  [{i}/{len(symbols)}] {sym:6s} VCP {row['score']:3d} · Trend {row['trend']}/8{flag}")
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - kể cả rate-limit vnai
            failed.append((sym, str(exc)[:70]))
            print(f"  [{i}/{len(symbols)}] {sym:6s} LỖI: {str(exc)[:50]}")
        if not settings.demo_mode:
            time.sleep(DELAY_BETWEEN_CALLS)

    candidates = sorted(
        (r for r in stage1 if r["score"] >= min_score), key=lambda r: -r["score"]
    )
    print(f"\nGIAI ĐOẠN 2: phân tích đầy đủ 4M cho {len(candidates)} ứng viên...\n")

    full = {}
    for i, row in enumerate(candidates, 1):
        sym = row["symbol"]
        try:
            full[sym] = analyze_symbol(sym)
            print(f"  [{i}/{len(candidates)}] {sym}: {full[sym].action}")
        except (Exception, SystemExit) as exc:  # noqa: BLE001 - kể cả rate-limit vnai
            print(f"  [{i}/{len(candidates)}] {sym}: lỗi 4M ({str(exc)[:40]}) — giữ kết quả kỹ thuật")
        if not settings.demo_mode:
            time.sleep(DELAY_BETWEEN_CALLS)

    # ---- Báo cáo ----
    now = datetime.now()
    lines = [
        f"# Báo Cáo Quét {group} — Ứng Viên VCP Tiềm Năng",
        f"*{now:%d/%m/%Y %H:%M} · quét {len(stage1)}/{len(symbols)} mã · ngưỡng {min_score} điểm*",
        "",
        "## Bảng xếp hạng ứng viên",
        "",
        "| # | Mã | Điểm VCP | Trend | RS | Sóng co thắt | Pivot | Giá | Dry-up | Khuyến nghị |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for i, r in enumerate(candidates, 1):
        rec = full.get(r["symbol"])
        action = rec.action if rec else "(chỉ kỹ thuật)"
        lines.append(
            f"| {i} | **{r['symbol']}** | {r['score']} | {r['trend']}/8 | {r['rs']} "
            f"| {r['waves']} | {r['pivot']:,.0f} | {r['close']:,.0f} "
            f"| {'✓' if r['dry_up'] else '—'} | {action} |"
        )
    if not candidates:
        lines.append("*(Không mã nào đạt ngưỡng — chưa có setup, kiên nhẫn là một vị thế.)*")

    lines += ["", "## Chi tiết ứng viên (4M + kỹ thuật)", ""]
    for r in candidates:
        rec = full.get(r["symbol"])
        if not rec:
            continue
        m = rec.four_m
        lines += [
            f"### {r['symbol']} — {r['score']}/100 · {rec.action} (conviction {rec.conviction})",
            f"- Sticker {m.sticker_price:,.0f} · MOS {m.mos_price:,.0f} · Giá {m.current_price:,.0f}"
            f" · Moat {m.moat_score}/100 · Mgmt {m.management_score}/100",
        ]
        lines += [f"- {reason}" for reason in rec.reasons]
        lines.append("")

    if failed:
        lines += ["## Mã lỗi", ""] + [f"- {s}: {e}" for s, e in failed] + [""]

    lines += [
        "---",
        "*Thông tin hỗ trợ quyết định theo phương pháp công khai của Mark Minervini"
        " và Phil Town — không phải lời khuyên đầu tư.*",
    ]

    out = f"data/bao_cao_{group.lower()}_{now:%Y%m%d_%H%M}.md"
    with open(out, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"\n{'=' * 56}")
    print(f"KẾT QUẢ {group}: {len(candidates)} ứng viên VCP >= {min_score}:")
    for r in candidates[:15]:
        print(f"  {r['symbol']:6s} {r['score']:3d}/100  Trend {r['trend']}/8  RS {r['rs']}")
    print(f"\nBáo cáo: {out}")


if __name__ == "__main__":
    threshold = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    grp = sys.argv[2] if len(sys.argv) > 2 else "WATCHLIST"
    main(threshold, grp)
