# Homies Fishing — nghiên cứu & thiết kế

Website cộng đồng câu cá: hành trình du câu, điểm câu, loài cá, mồi, và chợ mua bán/trao đổi đồ câu.

| Bước | Tài liệu |
|---|---|
| 1. Thị trường, đối thủ, truyền thông, thiết kế web | [docs/01-nghien-cuu-thi-truong-va-thiet-ke.md](docs/01-nghien-cuu-thi-truong-va-thiet-ke.md) |
| 2. Nguồn thông tin du lịch câu cá VN, bài mô tả, bài phễu | [docs/02-noi-dung-va-bai-pheu.md](docs/02-noi-dung-va-bai-pheu.md) |
| 3. Affiliate & thương mại điện tử | [docs/03-affiliate-va-thuong-mai-dien-tu.md](docs/03-affiliate-va-thuong-mai-dien-tu.md) |
| Kế hoạch video TikTok 30 ngày | [docs/04-ke-hoach-tiktok-30-ngay.md](docs/04-ke-hoach-tiktok-30-ngay.md) |
| Chữ đăng 7 video TikTok tuần 1 | [docs/05-tiktok-tuan-1-kich-ban.md](docs/05-tiktok-tuan-1-kich-ban.md) |
| Thiết kế & quản trị web với AI Agent | [docs/06-thiet-ke-va-quan-tri-web-voi-ai-agent.md](docs/06-thiet-ke-va-quan-tri-web-voi-ai-agent.md) |
| Mô hình affiliate & đội AI Agent | [docs/07-mo-hinh-affiliate-va-doi-agent.md](docs/07-mo-hinh-affiliate-va-doi-agent.md) (nghiên cứu gốc: [docs/research/](docs/research/)) |
| Trang chủ mẫu (HTML tĩnh, dữ liệu minh họa) | [web/index.html](web/index.html), trang Đồ nên mua [web/do-cau.html](web/do-cau.html) |

Số liệu có ghi nguồn; mục chưa kiểm chứng được ghi rõ. Phần pháp lý chỉ để định hướng, cần luật sư xác nhận.

`CLAUDE.md` là bộ nhớ dự án cho AI agent. `.github/workflows/claude.yml` cho phép gõ `@claude` trong issue/PR để giao việc (cần cài Claude GitHub App và thêm secret).

Hạ tầng affiliate: dữ liệu link `web/data/affiliate-links.json`, chuyển hướng + đếm click `functions/go/[slug].js` (Cloudflare Pages Function), kiểm link chết `scripts/check-links.mjs` (chạy tự động sáng thứ Hai qua `.github/workflows/check-affiliate-links.yml`).

Xem thử trên máy: `cd web && python -m http.server 8000` rồi mở http://localhost:8000 (trang Đồ nên mua cần máy chủ web để tải dữ liệu JSON).
