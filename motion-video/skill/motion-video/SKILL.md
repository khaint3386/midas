---
name: motion-video
description: Điều phối quy trình làm video motion graphics bằng code (HyperFrames, Remotion hoặc HTML+Playwright+ffmpeg): brief, storyboard, render nháp, xem lại khung hình, sửa, xuất MP4. Dùng khi người dùng muốn làm video giới thiệu sản phẩm, reel, Shorts, B-roll hoặc motion graphics bằng code.
---

# Quy trình video motion graphics bằng code

Bạn điều phối vòng lặp: brief → storyboard → render nháp → xem lại → sửa → bản cuối. Skill gốc của bên thứ ba (nếu đã cài) lo "gu" chuyển động; skill này lo thứ tự công việc và các điểm dừng xin duyệt.

## Nguyên tắc

- Nói tiếng Việt với người dùng. Không bịa tính năng của repo/skill nào; chưa đọc được thì nói là chưa đọc.
- Không cài skill/gói của bên thứ ba khi chưa tóm tắt nó làm gì và chưa được đồng ý (xem `docs/safety-checklist.md`).
- Làm trong thư mục riêng (ví dụ `video-projects/<tên-video>/`), không đụng code ứng dụng khác.
- Dừng xin duyệt ở: brief, storyboard, bản nháp, bản cuối.

## Các bước

1. **Brief.** Hỏi những mục còn thiếu theo `templates/brief.md` (mục tiêu, độ dài, tỉ lệ, FPS, tài sản, âm thanh, mục đích thương mại). Hỏi tối đa vài câu một lượt.
2. **Chọn engine.** Mặc định HyperFrames nếu người dùng không quen React; Remotion nếu dự án đã dùng React (nhắc kiểm tra license thương mại); HTML + Playwright + ffmpeg nếu muốn ít phụ thuộc nhất. Nêu lý do ngắn.
3. **Kiểm tra môi trường.** Chạy `motion-video/scripts/check_env.sh`. Thiếu gì thì đề xuất lệnh cài, chờ đồng ý.
4. **Skill ngoài (tuỳ chọn).** Nếu người dùng muốn thêm skill từ danh mục `docs/repo-catalog.md`, clone vào thư mục tạm, chạy `scripts/vet_skill.sh`, đọc `SKILL.md`/script, tóm tắt rủi ro và license, rồi mới cài.
5. **Storyboard.** Điền `templates/storyboard.md`: cảnh, thời lượng, chữ, camera, chuyển cảnh, âm thanh, nhịp. Chờ duyệt.
6. **Dựng.** Viết code theo engine đã chọn, bám storyboard. Chữ/số liệu phải đúng nội dung người dùng đưa; không tự thêm số liệu.
7. **Render nháp** độ phân giải thấp, FPS thấp để nhanh. Trích một số khung hình quan trọng (đầu, giữa mỗi cảnh, cuối) bằng ffmpeg và **xem lại từng ảnh**: chữ bị cắt/chồng, tương phản, bố cục, chuyển cảnh giật. Liệt kê lỗi thật sự thấy, sửa, render lại. Tối đa vài vòng, nêu rõ còn lỗi nào chưa sửa được.
8. **Bản cuối.** Render đủ chất lượng, kiểm tra bằng `ffprobe` (độ dài, độ phân giải, FPS, có luồng âm thanh nếu cần). Báo cáo đúng kết quả kiểm tra, không khẳng định "đẹp" khi chưa xem khung hình.
9. **Bàn giao.** Đường dẫn file MP4, mã nguồn, lệnh render lại, và ghi chú license của engine/skill đã dùng.

## Khi không render được

Nếu thiếu Node/ffmpeg/Chromium hoặc môi trường không cho cài, dừng ở storyboard + mã nguồn đã dựng, nói rõ chưa render được và vì sao. Với Claude Cowork thiếu công cụ, gợi ý chuyển sang Claude Code để render.
