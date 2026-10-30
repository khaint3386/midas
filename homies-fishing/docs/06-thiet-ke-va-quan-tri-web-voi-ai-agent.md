# Thiết kế & quản trị website Homies Fishing với AI Agent

> Ngày tổng hợp: 30/10/2026. Phần về Claude Code GitHub Actions lấy từ **tài liệu chính thức** ([code.claude.com – GitHub Actions](https://code.claude.com/docs/en/github-actions)). Các phần khác chủ yếu từ blog và tài liệu của nhà cung cấp; tôi ghi nguồn từng ý và đánh dấu chỗ chưa kiểm chứng.

---

## 1. Nguyên tắc cốt lõi

1. **Agent làm, người duyệt.** Mọi thay đổi code hoặc nội dung biên tập đi qua **pull request (PR)**. Bạn xem bản xem trước rồi mới bấm merge. Tài liệu chính thức khuyến nghị: *"Grant the workflow only the permissions it needs, and review Claude's changes before merging."*
2. **Git là nguồn sự thật** cho code, thiết kế và bài biên tập (Markdown). Có lịch sử, hoàn tác được, agent đọc và sửa dễ.
3. **Nội dung cộng đồng là dữ liệu không tin cậy.** Bài hành trình, tin chợ, bình luận có thể chứa câu lệnh cài cắm nhằm điều khiển AI. Đây là lỗ hổng **LLM01 – Prompt Injection** đứng đầu OWASP Top 10 cho ứng dụng LLM 2025, dạng *gián tiếp* khi AI đọc nội dung từ người ngoài ([HackerOne](https://www.hackerone.com/blog/owasp-top-10-llms-2025-how-genai-risks-are-evolving), [OWASP LLM01 tóm tắt](https://guptadeepak.com/agent-security/threats/llm01/)). → Agent đọc nội dung cộng đồng **không được** có quyền ghi, xóa, thanh toán hay đăng bài.
4. **Quyền tối thiểu.** Mỗi agent chỉ có đúng công cụ nó cần. Agent báo cáo thì chỉ đọc. Agent kiểm duyệt chỉ chấm điểm và gắn cờ, còn quyết định gỡ hay khóa là của người.
5. **Việc có rủi ro thì luôn hỏi người:** đăng lên mạng xã hội, gửi email hàng loạt, xóa dữ liệu, hoàn tiền, khóa tài khoản.

---

## 2. Kiến trúc kỹ thuật đề xuất (thân thiện với AI Agent)

| Lớp | Đề xuất | Vì sao hợp với agent |
|---|---|---|
| Khung web | **Astro** cho trang nội dung (cẩm nang, điểm câu, loài cá); thêm đảo tương tác (React/Svelte) cho chợ & form | Code ít, cấu trúc rõ, bài viết là file Markdown agent sửa trực tiếp. Một số bài so sánh xếp Astro cho trang "để đọc", Next.js cho trang "để dùng như app" ([ContextBolt](https://contextbolt.com/blog/astro-vs-nextjs/)) |
| Dữ liệu cộng đồng | **Supabase** (Postgres + đăng nhập + lưu ảnh) | Có MCP server chính thức, hỗ trợ **chế độ chỉ đọc** `?read_only=true` và giới hạn 1 dự án bằng `project_ref` ([README Supabase MCP qua awesome.ecosyste.ms](https://awesome.ecosyste.ms/projects/github.com%2Fsupabase%2Fmcp)). Server đang ghi nhãn beta, cần kiểm tra lại |
| CMS cho ban biên tập (tùy chọn) | Markdown trong Git (đơn giản nhất) hoặc **Strapi / Sanity** khi có người biên tập không dùng Git | Strapi 5 có MCP endpoint tích hợp, Sanity có MCP server từ xa, tôn trọng quyền theo dataset ([Strapi](https://strapi.io/blog/strapi-mcp-n8n-ai-content-pipeline), [Toolradar – Sanity MCP](https://toolradar.com/tools/sanity-mcp)) |
| Hosting | **Cloudflare Pages** hoặc **Vercel** | Mỗi PR có link xem trước, nên bạn duyệt bằng mắt trước khi merge ([CoderCops](https://blog.codercops.com/blog/our-tech-stack-2026-what-we-use-why), [Vercel](https://vercel.com/i/astro-vs-next-js)). Một bài viết nói Cloudflare đã mua đội Astro tháng 1/2026 ([DEV](https://dev.to/mr_manushukla/astro-6-vs-nextjs-16-for-content-sites-in-2026-speed-hosting-cost-and-when-to-switch-2icn)) — **nguồn thứ cấp, chưa kiểm chứng** |
| Thanh toán (giai đoạn sau) | payOS / đối tác trung gian có phép | Agent **không** được gắn công cụ thanh toán |

**Phương án nhẹ hơn:** WordPress (như tài liệu Bước 1, hướng A) vẫn quản trị được bằng AI. Nhưng agent làm việc với file trong Git hiệu quả và an toàn hơn nhiều so với thao tác trong trang quản trị WordPress.

---

## 3. Đội AI Agent theo vai trò

| Agent | Việc làm | Công cụ / cách chạy | Quyền | Người duyệt |
|---|---|---|---|---|
| **Kỹ sư (Dev)** | Xây tính năng, sửa lỗi, chỉnh giao diện | Claude Code (máy bạn hoặc cloud) + `CLAUDE.md` | Sửa code trên nhánh, mở PR | Bạn merge PR |
| **Người review** | Soát lỗi mỗi PR | Claude Code GitHub Action với plugin `code-review`, hoặc tính năng Code Review tự động ([docs](https://code.claude.com/docs/en/github-actions)) | Đọc + bình luận PR | — |
| **Trợ lý theo yêu cầu** | Gõ `@claude …` trong issue/PR để giao việc | `.github/workflows/claude.yml` (đã thêm sẵn) | Viết nhánh, mở PR | Bạn |
| **QA** | Kiểm tra giao diện, lỗi tràn, khả năng truy cập | Script Playwright **cố định** chạy trong CI; agent dùng Playwright MCP để khám phá và viết test. Nguồn khuyên không để AI làm cổng kiểm tra hồi quy trong CI ([Argos](https://argos-ci.com/blog/playwright-mcp-visual-testing), [Testdino](https://testdino.com/blog/playwright-mcp-setup)) | Đọc | — |
| **Biên tập viên nội dung** | Soạn nháp bài cẩm nang, lịch mùa, kịch bản TikTok **kèm nguồn** | Claude Code, hoặc skill riêng trong `.claude/skills/` | Viết file Markdown vào nhánh | Bạn kiểm chứng nguồn rồi merge |
| **Kiểm duyệt** | Chấm điểm rủi ro bài/tin chợ (lừa đảo, hàng cấm, kích điện, vùng cấm) | Gọi Claude API từ backend, đưa **nguyên văn quy chế** vào prompt mỗi lần | **Chỉ** gắn nhãn & đưa vào hàng chờ | Ban quản trị xử lý vùng "không chắc" |
| **Vận hành (Ops)** | Kiểm link chết (cả link affiliate), ảnh lỗi, tốc độ; báo cáo tuần | GitHub Action chạy theo lịch (`schedule`) | Chỉ đọc; mở issue khi có lỗi | Bạn |
| **Marketing** | Kịch bản TikTok, caption, phân tích số liệu tuần | Claude (chat) + ảnh chụp TikTok Studio | Không đăng bài | Bạn tự đăng |

### 3.1. Mẫu kiểm duyệt tốt
- Mô hình chấm **điểm khả năng vi phạm**: điểm thấp nghĩa là mô hình tin nội dung an toàn, **vùng giữa là chỗ mô hình không chắc nên chuyển cho người** ([Grab](https://www.grab.com/sg/inside-grab/stories/how-large-language-models-help-us-make-more-precise-content-moderation-decisions/)). Đề xuất của tôi: điểm cao thì tạm ẩn và vẫn để người xác nhận trước khi khóa tài khoản.
- **Đưa văn bản quy chế vào prompt mỗi lần quyết định** để giảm việc AI "bịa luật" (Dave Willner, cựu trưởng bộ phận Trust & Safety của OpenAI, [Tech Policy Press](https://techpolicy.press/transcript-dave-willner-on-moderating-with-ai-at-the-institute-for-rebooting-social-media)).
- Ghi lại quyết định của người để chỉnh prompt và ngưỡng điểm dần dần ([Avasant](https://avasant.com/report/impact-of-generative-ai-on-content-moderation/)).
- Bọc nội dung người dùng trong thẻ rõ ràng (ví dụ `<user_post>…</user_post>`) và dặn mô hình coi đó là dữ liệu, không phải chỉ thị. Cách này chỉ **giảm** chứ không loại bỏ prompt injection, nên vẫn giữ nguyên tắc quyền tối thiểu.

---

## 4. Quy trình làm việc hằng ngày

```
Ý tưởng / lỗi ──► Issue trên GitHub (mô tả rõ, dán ảnh)
                    │  gõ "@claude làm việc này"  (hoặc mở Claude Code)
                    ▼
            Agent tạo nhánh + PR ──► CI chạy test cố định + agent review
                    │
                    ▼
        Link xem trước (Cloudflare/Vercel) ──► Bạn xem trên điện thoại
                    │ ổn
                    ▼
                 Merge ──► Tự triển khai lên web thật
```

**Lịch định kỳ gợi ý:**

| Tần suất | Việc | Ai |
|---|---|---|
| Hằng ngày | Hàng chờ kiểm duyệt (vùng không chắc) | Bạn / mod |
| Hằng tuần (thứ Hai) | Báo cáo: link chết, tin chợ bị báo cáo, bài chờ duyệt, lượt truy cập | Agent Ops → issue |
| Hằng tuần | Kịch bản TikTok tuần tới | Agent Marketing → bạn duyệt |
| Hằng tháng | Cập nhật lịch mùa câu (kèm nguồn), rà bài cũ hơn 6 tháng | Agent Biên tập → PR |
| Hằng quý | Rà quyền truy cập, xoay khóa API, cập nhật thư viện | Bạn + agent Dev |

---

## 5. Bảo mật & chi phí

- **Khóa bí mật:** không bao giờ commit API key vào repo; lưu trong GitHub Secrets (`ANTHROPIC_API_KEY` hoặc `CLAUDE_CODE_OAUTH_TOKEN`) ([docs](https://code.claude.com/docs/en/github-actions)).
- **Ai được gọi `@claude`:** mặc định chỉ người có quyền ghi repo; bot bị chặn để tránh vòng lặp (cùng nguồn). Đừng nới quyền này cho người ngoài.
- **MCP cơ sở dữ liệu:** bật chế độ chỉ đọc theo mặc định; chỉ bật ghi trong phiên làm migration có bạn theo dõi.
- **Tách môi trường:** agent thử nghiệm trên dự án Supabase *staging*, không chạm dữ liệu thật của thành viên.
- **Chi phí:** mỗi lần chạy tốn phút GitHub Actions và token; giới hạn bằng `--max-turns`, timeout, viết yêu cầu cụ thể, giữ `CLAUDE.md` ngắn ([docs](https://code.claude.com/docs/en/github-actions)). Nếu dùng token gói Claude (`CLAUDE_CODE_OAUTH_TOKEN`) thì tính vào gói thay vì API.
- **Chất lượng review:** một blog Nhật ghi nhận review mặc định có xu hướng "LGTM" quá dễ dãi, phải chỉnh tiêu chí ([Zenn](https://zenn.dev/notahotel/articles/cf90b6eff72272)). → Ghi tiêu chí review cụ thể trong `CLAUDE.md`.

---

## 6. `CLAUDE.md` — bộ nhớ dự án cho agent

Các hướng dẫn cộng đồng thống nhất: giữ **ngắn**, chỉ ghi những gì thay đổi cách agent làm việc, kèm lệnh kiểm tra cần chạy ([DEV – CLAUDE.md 2026](https://dev.to/nishilbhave/claudemd-best-practices-the-complete-2026-guide-435j), [SitePoint](https://www.sitepoint.com/claude-code-workflows-a-practical-pattern-guide/)). Tài liệu chính thức cũng khuyên dùng `CLAUDE.md` để định nghĩa quy ước và tiêu chí review. Repo đã có sẵn file `CLAUDE.md` ở thư mục gốc.

---

## 7. Lộ trình áp dụng

| Giai đoạn | Việc | Kết quả |
|---|---|---|
| **Tuần 1** | Tạo repo riêng, cài Claude GitHub App, thêm secret, thử `@claude` trên 1 issue | Giao việc qua issue được |
| **Tuần 2–3** | Chuyển trang mẫu sang Astro; nối Cloudflare Pages/Vercel để có link xem trước mỗi PR | Duyệt bằng mắt trước khi lên web |
| **Tuần 3–4** | Thêm CI: build + Playwright kiểm tra tràn ngang, ảnh lỗi, link chết | Lỗi bị chặn trước khi merge |
| **Tháng 2** | Supabase (đăng nhập, bài hành trình, tin chợ) + agent kiểm duyệt chấm điểm | Mở đóng góp cộng đồng có kiểm soát |
| **Tháng 3+** | Báo cáo định kỳ, agent biên tập theo lịch, khung phân tích TikTok | Vận hành đều với ít giờ công |

---

## 8. Việc chỉ bạn làm được
- Tạo repo GitHub và cấp quyền cho Claude (tôi không có quyền tạo repo).
- Thêm secret và cài Claude GitHub App (cần quyền admin repo).
- Đăng ký hosting, tên miền, Supabase; giữ toàn bộ mật khẩu và khóa.
- Quyết định cuối cùng về kiểm duyệt, khóa tài khoản, tiền bạc, đăng bài công khai.
