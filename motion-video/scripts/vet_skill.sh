#!/usr/bin/env bash
# Quét nhanh một repo skill đã clone để tìm chỗ cần đọc kỹ. KHÔNG chạy code trong repo.
# Dùng: vet_skill.sh <thư-mục-repo>
set -u

dir="${1:-}"
if [ -z "$dir" ] || [ ! -d "$dir" ]; then
  echo "Dùng: $0 <thư-mục-repo>" >&2
  exit 2
fi

echo "== Tệp chỉ dẫn =="
find "$dir" -name 'SKILL.md' -not -path '*/.git/*' | sed 's/^/  /'
find "$dir" -maxdepth 2 -iname 'README*' -not -path '*/.git/*' | sed 's/^/  /'

echo "== License =="
lic=$(find "$dir" -maxdepth 1 -iname 'LICENSE*' -o -maxdepth 1 -iname 'COPYING*' | head -1)
if [ -n "$lic" ]; then echo "  $lic: $(grep -m1 -iE 'MIT|Apache|GPL|BSD|Creative Commons|CC0' "$lic" || echo 'không nhận ra, đọc tay')"
else echo "  KHÔNG có tệp license: hỏi tác giả trước khi dùng thương mại"; fi

echo "== Lần commit gần nhất =="
if [ -d "$dir/.git" ]; then git -C "$dir" log -1 --format='  %cd (%s)' --date=short; else echo "  (không phải git repo)"; fi

echo "== Mẫu lệnh cần đọc kỹ (có thể là false positive) =="
pattern='rm -rf|rm -r |curl |wget |Invoke-WebRequest|eval |base64|nc -|bash -c|sh -c|chmod \+x|sudo |\.ssh|\.aws|\.env|process\.env|os\.environ|child_process|subprocess|fetch\(|XMLHttpRequest'
hits=$(grep -rnIE "$pattern" "$dir" --exclude-dir=.git --exclude-dir=node_modules 2>/dev/null | head -60)
if [ -n "$hits" ]; then echo "$hits" | sed 's/^/  /'; else echo "  không thấy"; fi

echo "Xong. Kết quả chỉ là gợi ý; vẫn phải tự đọc SKILL.md và các script."
