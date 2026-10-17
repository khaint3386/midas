#!/usr/bin/env bash
# Kiểm tra máy đã đủ công cụ để render video motion graphics chưa.
# Chỉ đọc, không cài gì. Thoát với mã 1 nếu thiếu mục bắt buộc.
set -u

missing=0

ok()   { printf '  [OK]    %s\n' "$1"; }
warn() { printf '  [THIẾU] %s\n' "$1"; }

echo "Kiểm tra môi trường:"

if command -v node >/dev/null 2>&1; then
  ver=$(node -v | sed 's/^v//')
  major=${ver%%.*}
  if [ "$major" -ge 18 ]; then
    ok "Node.js $ver (một số repo yêu cầu 20+)"
  else
    warn "Node.js $ver quá cũ, cần >= 18"; missing=1
  fi
else
  warn "Node.js chưa cài (cần >= 18)"; missing=1
fi

if command -v ffmpeg >/dev/null 2>&1; then
  ok "$(ffmpeg -version | head -1)"
else
  warn "ffmpeg chưa cài (ghép khung hình thành MP4)"; missing=1
fi

if command -v npx >/dev/null 2>&1; then
  ok "npx có sẵn"
else
  warn "npx chưa có (đi kèm Node.js)"; missing=1
fi

# Chromium cho các skill render bằng trình duyệt (không bắt buộc với mọi engine).
chromium_found=0
for p in "${PLAYWRIGHT_BROWSERS_PATH:-}" "$HOME/.cache/ms-playwright" "$HOME/Library/Caches/ms-playwright"; do
  if [ -n "$p" ] && ls "$p"/chromium* >/dev/null 2>&1; then chromium_found=1; break; fi
done
if [ "$chromium_found" -eq 1 ]; then
  ok "Playwright Chromium"
else
  warn "Playwright Chromium chưa thấy (chỉ cần cho skill render bằng trình duyệt): npx playwright install chromium"
fi

if [ "$missing" -ne 0 ]; then
  echo "Còn thiếu mục bắt buộc."
  exit 1
fi
echo "Đủ công cụ bắt buộc."
