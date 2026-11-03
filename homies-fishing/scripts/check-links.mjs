// Kiểm tra link affiliate chết: node scripts/check-links.mjs
// Thoát mã 1 nếu có link lỗi (để GitHub Actions báo đỏ).
import { readFile } from "node:fs/promises";

const file = new URL("../web/data/affiliate-links.json", import.meta.url);
const { links } = JSON.parse(await readFile(file, "utf8"));

const results = await Promise.all(
  links.map(async (l) => {
    try {
      const r = await fetch(l.target_url, {
        redirect: "follow",
        signal: AbortSignal.timeout(15000),
        headers: { "User-Agent": "HomiesFishingLinkCheck/1.0" },
      });
      return { slug: l.slug, ok: r.status < 400, status: r.status };
    } catch (e) {
      return { slug: l.slug, ok: false, status: e.name };
    }
  }),
);

const bad = results.filter((r) => !r.ok);
for (const r of results) console.log(`${r.ok ? "OK  " : "LỖI "} ${r.status}\t${r.slug}`);
console.log(`\n${results.length - bad.length}/${results.length} link hoạt động.`);
if (bad.length) process.exit(1);
