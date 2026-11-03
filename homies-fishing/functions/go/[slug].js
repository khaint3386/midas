// Cloudflare Pages Function: /go/{slug}?a={bài}&p={vị trí}
// Tra slug trong web/data/affiliate-links.json, ghi một lượt bấm (nếu có binding
// Analytics Engine tên CLICKS) rồi chuyển hướng 302 tới link affiliate.
// Link có "is_active": false được coi như đã gỡ: chuyển về trang Đồ nên mua.
// Không lưu IP hay dữ liệu cá nhân.

const SUB_ID_PARAM = {
  shopee: "sub_id",     // đổi theo tên tham số thật của từng mạng affiliate
  accesstrade: "sub1",
  partner: "utm_content",
};

export async function onRequestGet({ params, request, env }) {
  const url = new URL(request.url);
  const res = await env.ASSETS.fetch(new URL("/data/affiliate-links.json", url));
  if (!res.ok) return Response.redirect(new URL("/do-cau.html", url), 302);

  const { links = [] } = await res.json();
  const link = links.find((l) => l.slug === params.slug && l.is_active !== false);
  if (!link) return Response.redirect(new URL("/do-cau.html", url), 302);

  const article = (url.searchParams.get("a") || "").slice(0, 64);
  const placement = (url.searchParams.get("p") || "unknown").slice(0, 32);

  env.CLICKS?.writeDataPoint({
    blobs: [link.slug, link.network, article, placement],
    indexes: [link.slug],
  });

  const target = new URL(link.target_url);
  const param = SUB_ID_PARAM[link.network];
  if (param && article) target.searchParams.set(param, `${article}-${placement}`);

  return new Response(null, {
    status: 302,
    headers: {
      Location: target.toString(),
      "Cache-Control": "no-store",
      "X-Robots-Tag": "noindex, nofollow",
    },
  });
}
