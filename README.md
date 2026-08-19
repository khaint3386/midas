# MIDAS 3.0 — Chạm vào đâu, vàng ở đó

Công cụ khuyến nghị đầu tư dài hạn cho chứng khoán Việt Nam, kết hợp hai trường phái:

- **4M — Phil Town (Rule #1 Investing):** chọn lọc "wonderful company" qua Meaning (AI đọc tin tức), Moat (Big Five: ROIC + tăng trưởng Doanh thu/EPS/BVPS/FCF ≥ 10%/năm), Management (ROE, D/E), Margin of Safety (sticker price chiết khấu 15%/năm, giá mua an toàn = 50% sticker).
- **VCP — Mark Minervini (SEPA):** xác định điểm mua/bán qua Trend Template 8 tiêu chí (Giai đoạn 2), phát hiện mẫu hình co thắt biến động (sóng điều chỉnh co dần, volume dry-up), pivot breakout kèm volume, stop loss tối đa 8%.

**Logic khuyến nghị:** MUA (4M đạt + VCP breakout) → CHỜ PIVOT (4M đạt + VCP chưa breakout) → TÍCH LŨY DÀI HẠN (4M đạt + giá dưới MOS) → THEO DÕI (đạt 1 tầng) → ĐỨNG NGOÀI.

## Chạy ứng dụng

```
# Cách 1: double-click start_midas.bat (tự tạo venv + cài dependencies)
# Cách 2: thủ công
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt
.venv\Scripts\python run.py
```

Mở http://127.0.0.1:8386 — bấm **QUÉT WATCHLIST**.

## Cấu hình

Sao chép `.env.example` → `.env`:

- `GEMINI_API_KEY`: key Gemini (bắt buộc dùng key MỚI — key cũ của Midas v2 đã lộ và phải thu hồi). Không có key hệ thống vẫn chạy, phần Meaning chuyển sang rule-based.
- `MIDAS_DEMO=1`: chạy demo với dữ liệu tổng hợp (mã HPG được cấy sẵn kịch bản VCP chuẩn để xem thử toàn bộ tính năng, không cần mạng).

## Kiểm chứng dữ liệu (chống tin giả / dữ liệu sai)

Mọi khuyến nghị đi qua vòng lặp tự kiểm chứng trước khi chấm điểm:

1. **BCTC**: đọc đúng định dạng vnstock 4.x (bảng xoay ngang, gọi limit 12 năm thay vì 4 mặc định), sắp xếp năm tăng dần, chuẩn hóa đơn vị (%, nghìn đồng), sanity check PE hàm ý 1–200.
2. **Đối chiếu chéo 2 nguồn**: EPS từ VCI so với KBS; lệch >20% → cảnh báo, trừ điểm tin cậy.
3. **Điểm tin cậy dữ liệu 0–100** (`data_quality.py`): thiếu chuỗi, ít năm, nghi sai đơn vị, chưa đối chiếu đều bị trừ minh bạch. Dưới 55 → mã bị **loại khỏi lọc tự động** và không được xếp "wonderful". Thiếu dữ liệu được ghi chú rõ thay vì chấm 0 oan.
4. **Tin tức**: chỉ đọc RSS whitelist (CafeF, VnEconomy, Vietstock, VnExpress — URL đã xác minh), khớp mã theo từ nguyên, khử trùng lặp; sentiment chỉ giữ nguyên khi ≥2 nguồn độc lập cùng đưa tin, ngược lại kéo về trung lập.
5. **RS Rating**: percentile thật 1–99 trong nhóm quét (chuẩn IBD/Minervini); phân tích mã lẻ dùng fallback tanh — không còn hiện tượng mã nào cũng RS 99.

## Lọc tuần tự động — TOP 12

Mỗi tuần (hoặc bấm nút **LỌC VN100 → TOP 12** trên giao diện) hệ thống quét VN100 hai giai đoạn: (1) kỹ thuật toàn nhóm + RS percentile, (2) 4M đầy đủ cho top 30 ứng viên. Điểm xếp hạng: **60% 4M + 40% VCP**, trong đó 4M = 40% Moat + 30% Management + 30% Định giá. Watchlist được **thay hoàn toàn** bằng 12 mã điểm cao nhất (mã dữ liệu kém tin cậy bị loại, ghi rõ trong báo cáo `data/bao_cao_loc_tuan_*.md`; lịch sử lưu ở `data/watchlist_history.json`).

- Chạy tay: `loc_tuan.bat` hoặc `.venv\Scripts\python loc_tuan.py VN100`
- Đặt lịch thứ 7 hàng tuần 08:00: chạy `dat_lich_quet_tuan.bat` (quyền Admin)

## Kiến trúc

```
run.py                  điểm khởi động (uvicorn, port 8386)
loc_tuan.py             lọc tuần TOP 12 (CLI, được Task Scheduler gọi)
app/
  __init__.py           create_app() — FastAPI factory
  config.py             Settings bất biến (.env)
  routers/api.py        REST API (thin router; /watchlist/rebuild chạy nền)
  services/
    market_data.py      vnstock 4.x: giá OHLCV + BCTC 12 năm, VCI + đối chiếu KBS
    data_quality.py     vòng lặp kiểm chứng: sanity check, cross-check, điểm tin cậy
    news_feed.py        RSS whitelist + khớp từ nguyên + đối chiếu chéo nguồn
    four_m.py           engine 4M Phil Town (nhận biết thiếu dữ liệu)
    vcp.py              engine Trend Template + VCP + RS percentile Minervini
    ai_analyst.py       Gemini đánh giá Meaning (fallback rule-based) + hạ trọng số tin đơn nguồn
    recommender.py      hợp nhất 2 tầng → khuyến nghị
    watchlist_builder.py lọc tuần 2 giai đoạn → TOP 12
web/index.html          dashboard dark-luxury (lightweight-charts)
data/watchlist.json     danh mục theo dõi (tự thay mỗi tuần)
```

## Lộ trình

- [x] Giai đoạn 1: Chứng khoán Việt Nam (vnstock) — hoàn thành
- [x] Giai đoạn 1.5: Tầng kiểm chứng dữ liệu + lọc tuần TOP 12 — hoàn thành
- [ ] Giai đoạn 2: Hàng hóa quốc tế qua MT5 (thêm `services/mt5_data.py` cùng interface với `market_data.py`, engine VCP dùng lại nguyên vẹn)

## Giới hạn tần suất vnstock (quan trọng)

Gói free của vnstock bị vnai giới hạn **20 request/phút** và khi vượt sẽ gọi `sys.exit()` làm chết tiến trình. Midas xử lý bằng: bộ điều tiết chủ động 15 request/phút (`_vn_call` trong market_data), bắt `SystemExit` chuyển thành lỗi thường + tự chờ 65s thử lại 1 lần, cache giá 15 phút và cache BCTC 24h (`data/cache_fundamentals.json`). Hệ quả: quét 12 mã lần đầu trong ngày mất ~5–8 phút, các lần sau nhanh hơn nhiều; lọc tuần VN100 lần đầu ~25–35 phút (chạy nền, có thanh tiến trình).

## Trạng thái kiểm định (05/07/2026)

- py_compile toàn bộ: 0 lỗi. Test demo mode: 12/12 mã, 5 nhánh logic đúng, HPG = MUA conviction 91, JSON serialize sạch NaN (hết lỗi HTTP 500 của /scan).
- Test tầng kiểm chứng: trích xuất định dạng vnstock 4.x, sắp năm tăng dần, chuẩn hóa ROE 0.18→18%, cross-check EPS (lệch 0.4% pass / 40% fail), quality gate loại mã thiếu 3/5 chỉ số, RS percentile trải đều 3→97 (hết bão hòa 99), khớp tin theo từ nguyên (CTD không khớp "ACTDX"), corroboration ≥2 nguồn. Bộ lọc tuần demo: chọn đúng top theo composite, ghi watchlist + báo cáo + lịch sử.
- Đã xác minh mã nguồn vnstock 4.0.2 trong `.venv` của máy anh (định dạng bảng, giới hạn 4 năm, nguồn KBS) và 2 URL RSS mới (VnEconomy, Vietstock) đang hoạt động.
- Đã kiểm chứng LIVE trên máy thật (05/07): giá FPT tải OK, BCTC tự chuyển nguồn KBS khi VCI lỗi (EPS 3 năm cuối 5.471→6.021, quality 55/100 vì KBS chỉ có 4 năm và thiếu ROIC), tin tức xác nhận 2 nguồn. Tìm ra gốc rễ HTTP 500 hàng loạt: vnai `sys.exit()` khi vượt 20 request/phút — đã vá bằng throttle + bắt SystemExit + cache (test mock pass).
- Lưu ý dữ liệu: nguồn KBS chỉ có 4 năm BCTC — chưa đủ chuẩn 10 năm Phil Town, hệ thống tự trừ điểm tin cậy và ghi chú. Khi VCI hoạt động lại sẽ tự có 10-12 năm.

> ⚠️ Midas cung cấp thông tin hỗ trợ quyết định dựa trên phương pháp công khai của Phil Town và Mark Minervini. Đây không phải lời khuyên đầu tư; quyết định và rủi ro thuộc về nhà đầu tư.
