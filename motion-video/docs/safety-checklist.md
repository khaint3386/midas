# Checklist an toàn trước khi cài một skill

Skill là chỉ dẫn Claude sẽ làm theo, nhiều skill kèm script chạy trên máy bạn.

1. Đọc `SKILL.md` và README: skill yêu cầu Claude làm gì, có tải gì từ internet không.
2. Xem các script đi kèm: nếu có lệnh xoá file, gửi dữ liệu ra ngoài, hoặc đọc thư mục ngoài dự án thì bỏ qua.
   Chạy `scripts/vet_skill.sh <thư-mục>` để quét nhanh. Script chỉ gợi ý chỗ cần đọc, **không** thay cho việc đọc.
3. Xem license: MIT/Apache dùng thương mại thoải mái; không ghi license hoặc điều khoản riêng (Remotion) thì đọc kỹ.
4. Xem lần cập nhật gần nhất: repo lâu không cập nhật có thể không chạy với Claude Code mới.
5. Thử trong thư mục riêng, không cài thẳng vào dự án đang chạy.

Có thể nhờ Claude: "Cài skill từ github.com/<tác-giả>/<repo>. Trước khi cài, đọc README và script, tóm tắt skill sẽ làm gì trên máy. Mình đồng ý mới cài, rồi chạy thử một ví dụ ngắn."
