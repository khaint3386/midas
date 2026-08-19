# Hướng Dẫn Cài Đặt & Xử Lý Sự Cố — Midas 3.0

## Cài đặt lần đầu (tự động)

1. Double-click **`start_midas.bat`** trong `B:\Antigravity\midas`
2. Script tự làm mọi thứ: kiểm tra Python → tạo môi trường ảo → cài thư viện (2-5 phút, chỉ lần đầu) → tạo `.env` → mở trình duyệt đúng địa chỉ
3. Trên dashboard, bấm **QUÉT WATCHLIST**

Yêu cầu duy nhất: đã cài **Python 3.10+** (https://www.python.org/downloads/ — nhớ tick *"Add Python to PATH"* khi cài).

## Cấu hình API key (Gemini — cho phần Meaning/tin tức)

1. Lấy key mới tại https://aistudio.google.com/apikey (miễn phí)
   — **KHÔNG dùng lại key cũ của Midas v2** (đã lộ, cần thu hồi tại chính trang này)
2. Mở file `.env` bằng Notepad, điền: `GEMINI_API_KEY=key_cua_ban`
3. Khởi động lại Midas

Chưa có key vẫn dùng được — phần đánh giá tin tức sẽ chạy chế độ rule-based đơn giản.

## Xử lý sự cố

**"Lỗi quét: Failed to fetch" / "Không kết nối được server"**
- Nguyên nhân thường gặp nhất: mở file `index.html` trực tiếp thay vì qua server. Cửa sổ đen `start_midas.bat` phải đang chạy, và địa chỉ trên trình duyệt phải là `http://127.0.0.1:8386`
- Nếu cửa sổ đen đã tắt/báo lỗi: đọc dòng lỗi cuối cùng trong đó, thường là thiếu thư viện → chạy lại `start_midas.bat`

**Quét được vài mã rồi báo lỗi các mã còn lại**
- Bình thường — từ bản này Midas quét từng mã một, mã lỗi sẽ được liệt kê riêng kèm gợi ý khắc phục tự động (dashboard tự gọi `/diagnose`)
- Mã lỗi thường do vnstock không có dữ liệu cho mã đó hoặc mạng chập chờn — bấm quét lại

**Muốn xem thử toàn bộ tính năng không cần mạng**
- Mở `.env`, đặt `MIDAS_DEMO=1`, khởi động lại → dữ liệu demo (mã HPG có sẵn kịch bản VCP + tín hiệu MUA để xem đủ mọi màn hình)
- Xong nhớ đặt lại `MIDAS_DEMO=0` để dùng dữ liệu thật

**Kiểm tra môi trường thủ công**
- Mở `http://127.0.0.1:8386/api/v1/diagnose` — thấy ngay module nào thiếu, dữ liệu live có tải được không, key đã cấu hình chưa

**Cài lại từ đầu**
- Xóa folder `.venv` rồi chạy lại `start_midas.bat`

## Quét rộng: VN30 / toàn sàn HOSE / hàng tuần

| File | Chức năng |
|---|---|
| `quet_vn30.bat` | Quét 30 mã VN30 ngay (ngưỡng 60 điểm, ~2-3 phút) |
| `quet_hose.bat` | Quét toàn bộ cổ phiếu sàn HOSE (~400 mã, ngưỡng 65, ~15-20 phút) |
| `dat_lich_quet_tuan.bat` | **Chạy 1 lần bằng quyền Admin** (chuột phải → Run as administrator) để đặt lịch Windows tự quét HOSE 8h sáng thứ 7 hàng tuần |

- Quét 2 giai đoạn: giai đoạn 1 chỉ kỹ thuật (nhẹ), giai đoạn 2 phân tích 4M đầy đủ cho mã đạt ngưỡng — tiết kiệm API, tránh rate-limit (đã có delay 0.8s/mã)
- Báo cáo lưu tại `data\bao_cao_<nhóm>_<ngày giờ>.md` — bảng xếp hạng ứng viên VCP + chi tiết 4M
- Tùy chỉnh: `.venv\Scripts\python scan_batch.py <ngưỡng> <nhóm>` với nhóm = WATCHLIST / VN30 / VN100 / HOSE / HNX30
- Xóa lịch tuần: `schtasks /Delete /TN Midas_Quet_HOSE_Tuan`

**Lưu ý sau khi cập nhật code:** phải TẮT HẲN cửa sổ đen của server rồi chạy lại `start_midas.bat` — server đang chạy không tự nhận code mới (dấu hiệu code cũ: badge "VCP 0", giá hiện số nhỏ như "72").

## Các địa chỉ hữu ích

| Địa chỉ | Chức năng |
|---|---|
| http://127.0.0.1:8386 | Dashboard chính |
| http://127.0.0.1:8386/docs | API docs (Swagger, tự sinh) |
| http://127.0.0.1:8386/api/v1/diagnose | Tự chẩn đoán môi trường |
