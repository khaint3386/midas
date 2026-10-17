# Quy trình làm video motion graphics bằng code với Claude

Dựng lại từ bài "20 Repo Skill Làm Video Motion Graphics Bằng Code Với Claude Opus 5.5" (giangxai.com, cập nhật 15/10/2026).

Ý chính của bài trong một câu: **model viết code, skill lo nhịp và camera, engine render ra MP4.**

> Lưu ý trung thực: nội dung về 20 repo (chức năng, số sao, license) lấy **từ bài viết**, chưa được kiểm chứng độc lập
> (môi trường tạo tài liệu này không truy cập được các repo đó). Hãy tự mở README/license từng repo trước khi cài.
> Xem `docs/repo-catalog.md`.

## 3 tầng của stack

| Tầng | Vai trò | Ví dụ trong bài |
|---|---|---|
| Model | Viết code từng khung hình, tự lên kế hoạch và xem lại | Claude (bài khuyên Opus 5.5) |
| Skill | Hướng dẫn Claude về nhịp, chuyển cảnh, camera, "gu" | claude-motion, product-launch-motion, animate, motion-design-skill |
| Engine | Biến code thành file MP4 | HyperFrames (HTML), Remotion (React), HTML+Playwright+ffmpeg |

## Quy trình 7 bước

1. **Brief**: mục tiêu, đối tượng, độ dài, tỉ lệ khung (16:9 / 9:16), tông giọng. Dùng `templates/brief.md`.
2. **Chọn engine + skill** theo bảng "Nên bắt đầu từ đâu" bên dưới.
3. **Chuẩn bị máy**: chạy `scripts/check_env.sh` (Node ≥ 18, ffmpeg, Playwright + Chromium).
4. **Kiểm tra skill trước khi cài** (5 phút): chạy `scripts/vet_skill.sh <thư-mục-repo-đã-clone>`, rồi tự đọc `SKILL.md`, README, script đi kèm, license.
5. **Cài skill** (xem "Cách cài") vào thư mục thử riêng, không cài thẳng vào dự án đang chạy.
6. **Storyboard → render nháp → xem lại khung hình → sửa**: dùng skill `skill/motion-video/SKILL.md` trong thư mục này để Claude chạy đúng vòng lặp, có điểm dừng xin duyệt.
7. **Render bản cuối + xuất MP4**, kiểm tra âm thanh, độ dài, độ phân giải.

## Nên bắt đầu từ đâu (theo bài)

| Việc cần làm | Gợi ý |
|---|---|
| Video ra mắt sản phẩm/khoá học | HyperFrames + product-launch-motion hoặc motion-graphics-skills |
| YouTube, Shorts, video nói chuyện | HyperFrames + hyperframes-student-kit hoặc Barty-Bart/motion-graphics (B-roll từ transcript) |
| Mới bắt đầu, muốn được dẫn từng bước | animate |
| Đã quen React | Remotion + Remotion Skills |
| Animation cho website, không cần video | Motion + motion-dev-animations-skill |
| Muốn video "có gu" hơn | thêm LottieFiles/motion-design-skill bên cạnh lựa chọn trên |

Không cần cài hết 20 repo. Bài khuyên chọn 2–3 cái hợp việc hằng ngày rồi cố định thành quy trình.

## Cách cài (4 kiểu trong bài)

1. **Plugin** (repo có hỗ trợ):
   `/plugin marketplace add heygen-com/hyperframes` rồi `/plugin install hyperframes@hyperframes`
2. **`npx skills add <tác-giả>/<repo>`** (cập nhật bằng `npx skills update`).
3. **Copy thủ công**: thư mục chứa `SKILL.md` → `~/.claude/skills/` (mọi dự án) hoặc `.claude/skills/` (một dự án).
4. **Mở repo như dự án mẫu** (clone rồi làm việc trong đó).

Với Claude Cowork: Customize → Plugins (dán `tác-giả/repo`) hoặc Customize → Skills (tải lên zip có `SKILL.md` ở gốc). Skill cần render (Node, ffmpeg, Playwright) nên chạy ở Claude Code; Cowork hợp với bước kịch bản/storyboard.

## Cài skill điều phối của thư mục này

```bash
mkdir -p .claude/skills && cp -r motion-video/skill/motion-video .claude/skills/
```

Sau đó mở phiên Claude Code mới và gõ `/motion-video` hoặc mô tả video bạn muốn.

## An toàn

Skill là chỉ dẫn Claude sẽ làm theo và có thể kèm script chạy trên máy bạn. Checklist 5 điểm (đọc SKILL.md, xem script, xem license, xem ngày cập nhật, thử trong thư mục riêng) nằm ở `docs/safety-checklist.md`.

## Cấu trúc thư mục

```
motion-video/
├── README.md
├── docs/repo-catalog.md        # 20 repo theo bài, kèm vai trò/license ghi trong bài
├── docs/safety-checklist.md
├── scripts/check_env.sh        # kiểm tra Node/ffmpeg/Playwright
├── scripts/vet_skill.sh        # quét nhanh mẫu lệnh rủi ro trong một repo skill
├── templates/brief.md
├── templates/storyboard.md
└── skill/motion-video/SKILL.md # skill điều phối quy trình
```
