# Bước 3 — Gắn link affiliate & bán hàng thương mại điện tử trên Homies Fishing

> Ngày tổng hợp: 26/10/2026. **Tỷ lệ hoa hồng thay đổi liên tục** và hầu hết số liệu dưới đây đến từ blog/đơn vị thứ ba, không phải bảng giá chính thức. Luôn kiểm tra trong trang quản trị của từng chương trình trước khi tính toán. Phần pháp lý là tổng hợp để định hướng, **không thay thế tư vấn của luật sư**.

---

## 1. Ba tầng kiếm tiền — đi từ dễ đến khó

| Tầng | Cách làm | Vốn/rủi ro | Khi nào |
|---|---|---|---|
| **1. Affiliate** | Gắn link sản phẩm sàn/shop vào bài hướng dẫn, review | Gần như 0 | Ngay từ ngày đầu |
| **2. Chợ rao vặt C2C** | Thành viên tự đăng – tự giao dịch; Homies thu phí đẩy tin/gian hàng | Thấp, cần kiểm duyệt | Khi có ~1.000 thành viên hoạt động |
| **3. Giao dịch qua nền tảng** | Giỏ hàng, thanh toán, giữ tiền trung gian, vận chuyển tích hợp | Cao: pháp lý, thanh toán, khiếu nại | Khi chợ đã có lượng giao dịch ổn định |

---

## 2. Các chương trình affiliate phù hợp

| Chương trình | Hoa hồng (tham khảo) | Ưu điểm | Lưu ý | Nguồn |
|---|---|---|---|---|
| **Shopee Affiliate** | Theo ngành hàng; khách **mới** cao hơn khách **cũ** rõ rệt (ví dụ một ngành: ~13,4% khách mới vs ~1–3% khách cũ); một nguồn nêu **trần ~30.000đ/đơn** | Shopee giữ ~56% doanh số TMĐT VN 2025; đồ câu bán rất nhiều trên Shopee | Một nguồn nhận định tỷ lệ tương đối thấp so với chương trình khác; bảng không chính thức | [FPT Shop](https://fptshop.com.vn/tin-tuc/danh-gia/affiliate-shopee-la-gi-huong-dan-lam-shopee-affiliate-hieu-qua-163999), [GHN](https://ghn.vn/blogs/tip-ban-hang/muc-hoa-hong-tiep-thi-lien-ket-shopee) |
| **TikTok Shop Affiliate** | ~5–15% tùy sản phẩm/thỏa thuận với người bán; cửa sổ ghi nhận thường ~30 ngày | TikTok Shop ~41% doanh số 2025; hợp với video ngắn | Chủ yếu gắn trong video/livestream/giỏ hàng TikTok, **không phải link nhúng web** là chính; yêu cầu follower (nguồn ghi ~1.000) | [Ecomobi](https://ecomobi.com/vi/tiktok-shop-affiliate-cach-kiem-20-trieu-vnd-thang-tu-dang-video), [Viettel Store](https://viettelstore.vn/tin-tuc/cach-lam-tiep-thi-lien-ket-tiktok) |
| **Mạng affiliate: ACCESSTRADE, Ecomobi…** | Một nguồn nêu chiến dịch TMĐT trên ACCESSTRADE trung bình ~10% | Một tài khoản – nhiều chiến dịch (Lazada, Tiki, thương hiệu); báo cáo tập trung | Lazada + Tiki chỉ còn ~3% thị phần 2025 → hiệu quả thấp hơn Shopee | [Advertising Vietnam](https://advertisingvietnam.com/tiem-nang-cua-cac-chien-dich-affiliate-san-tmdt-con-duong-nao-cho-newbie-p19291), [Viettel Store – Lazada](https://viettelstore.vn/tin-tuc/tiep-thi-lien-ket-lazada) |
| **Hợp tác trực tiếp với shop đồ câu** | Tự thương lượng (nhận định: 5–15% hoặc phí cố định/tháng) | Hoa hồng cao hơn, có **mã giảm giá riêng "HOMIES"**, có thể đồng tổ chức sự kiện | Phải tự theo dõi đơn (mã giảm giá, link UTM), cần hợp đồng | — |
| **Amazon Associates** | Nhóm Sports & Outdoors: các nguồn mâu thuẫn, từ ~0,75% đến ~5% (Mỹ) | Chỉ hữu ích nếu làm nội dung tiếng Anh cho khách quốc tế | Không phù hợp người mua Việt Nam | [Amazon Associates](https://affiliate-program.amazon.com/help/node/topic/G4ARBJC7Z2NK48CA) |

Số liệu thị phần: Metric.vn qua [Đại biểu Nhân dân](https://daibieunhandan.vn/thuong-mai-dien-tu-viet-nam-2025-lazada-va-tiki-tut-doc-chia-nhau-3-thi-phan-10405406.html).

**Khuyến nghị:** bắt đầu với **Shopee Affiliate** (link trên web) + **TikTok Shop Affiliate** (video ngắn) + **1–3 shop đồ câu đối tác trực tiếp**. Đăng ký thêm ACCESSTRADE để có các chiến dịch thương hiệu.

---

## 3. Cách gắn link affiliate đúng kỹ thuật

### 3.1. Nguyên tắc
1. **Không dán link thô vào bài.** Mọi link đi qua đường dẫn nội bộ `homiesfishing.vn/go/{ma-san-pham}` → máy chủ ghi nhận lượt bấm → chuyển hướng 302 tới link affiliate. Lợi ích: đổi link một chỗ áp dụng cho mọi bài; đo được bài nào ra tiền; link sàn hết hạn thì sửa nhanh.
2. **Gắn thuộc tính** `rel="sponsored nofollow noopener"` và `target="_blank"` cho link affiliate (Google khuyến nghị `sponsored` cho link được trả tiền).
3. **Sub ID / UTM theo bài:** Shopee, ACCESSTRADE đều cho gắn tham số phụ (sub_id) — dùng để biết đơn đến từ bài nào, vị trí nào (đầu bài / bảng so sánh / cuối bài).
4. **Không ghi cứng giá.** Ghi "Giá tham khảo ngày dd/mm" hoặc chỉ ghi khoảng giá, vì giá sàn đổi hằng ngày.
5. **Kiểm tra link chết** tự động mỗi tuần (gửi request tới link đích, báo lỗi nếu 404 hoặc sản phẩm hết hàng).
6. **Công bố affiliate** ở đầu mỗi bài có link + trang chính sách riêng (mẫu ở mục 6).

### 3.2. Mô hình dữ liệu tối thiểu

```sql
CREATE TABLE affiliate_links (
  id           SERIAL PRIMARY KEY,
  slug         TEXT UNIQUE NOT NULL,        -- vd: may-cau-2500-co-ban
  product_name TEXT NOT NULL,
  network      TEXT NOT NULL,               -- shopee | tiktok | accesstrade | partner
  target_url   TEXT NOT NULL,               -- link affiliate gốc
  price_note   TEXT,                        -- "Khoảng 450–600k, cập nhật 26/10"
  is_active    BOOLEAN DEFAULT TRUE,
  last_checked TIMESTAMPTZ
);

CREATE TABLE affiliate_clicks (
  id         BIGSERIAL PRIMARY KEY,
  link_id    INT REFERENCES affiliate_links(id),
  article_id INT,                           -- bài nào
  placement  TEXT,                          -- top | table | bottom
  clicked_at TIMESTAMPTZ DEFAULT now()
  -- không lưu IP thô; nếu cần chống click ảo thì lưu hash có muối và xoá sau 30 ngày
);
```

### 3.3. Ví dụ route chuyển hướng (Next.js App Router)

```ts
// app/go/[slug]/route.ts
import { NextResponse } from "next/server";
import { db } from "@/lib/db";

export async function GET(req: Request, { params }: { params: { slug: string } }) {
  const link = await db.affiliateLink.findUnique({ where: { slug: params.slug } });
  if (!link || !link.isActive) {
    return NextResponse.redirect(new URL("/do-cau", req.url), 302);
  }
  const url = new URL(req.url);
  await db.affiliateClick.create({
    data: {
      linkId: link.id,
      articleId: Number(url.searchParams.get("a")) || null,
      placement: url.searchParams.get("p") ?? "unknown",
    },
  });
  const target = new URL(link.targetUrl);
  // gắn sub_id để đối soát trên dashboard của mạng affiliate (tên tham số tùy từng mạng)
  if (url.searchParams.get("a")) target.searchParams.set("sub_id", `a${url.searchParams.get("a")}`);
  return NextResponse.redirect(target.toString(), 302);
}
```

Trong bài viết:

```html
<a href="/go/may-cau-2500-co-ban?a=128&p=table"
   rel="sponsored nofollow noopener" target="_blank">Xem giá trên Shopee</a>
```

**Nếu dùng WordPress:** plugin quản lý link (ví dụ ThirstyAffiliates, Pretty Links) làm đúng việc trên: rút gọn link, đếm click, thêm `rel="sponsored"` tự động. Lưu ý cài từ kho plugin chính thức và cập nhật thường xuyên.

### 3.4. Mẫu "hộp sản phẩm" trong bài (đặt tối đa 3–5 hộp/bài)

```
┌────────────────────────────────────────────┐
│ [ảnh]  Máy câu dọc 2500 – cho người mới      │
│        Hợp: câu lục hồ dịch vụ, câu lure nhẹ │
│        Khoảng giá: 450–600k (26/10/2026)     │
│        ✔ Nhẹ  ✔ Dễ bảo dưỡng  ✖ Không hợp biển│
│        [Xem trên Shopee]  [Tìm đồ cũ ở Chợ]   │
└────────────────────────────────────────────┘
```

Nút **"Tìm đồ cũ ở Chợ Homies"** đặt cạnh nút affiliate: vừa phục vụ người dùng muốn tiết kiệm, vừa kéo lưu lượng vào chợ.

### 3.5. Vị trí đặt affiliate hiệu quả (nhận định từ thực tiễn ngành nội dung)
- Bài **"Nhập môn / chọn đồ đầu tiên"** — ý định mua cao nhất.
- Bài **so sánh** ("Cần lure dưới 1 triệu: 5 lựa chọn").
- Cuối bài **hành trình**: "Đồ mình dùng trong chuyến này" (người viết tự chọn; nếu là bài của thành viên, có thể **chia sẻ hoa hồng** cho họ — xem mục 5.3).
- Trang **loài cá**: "Bộ đồ gợi ý để câu cá chẽm".
- **Không** đặt affiliate trong cảnh báo an toàn/pháp lý.

---

## 4. Ước tính doanh thu affiliate — công thức (số minh họa là GIẢ ĐỊNH)

```
Doanh thu = Lượt xem bài × Tỷ lệ bấm link (CTR) × Tỷ lệ mua (CR) × Giá trị đơn (AOV) × Hoa hồng
```

Ví dụ **giả định** (không phải dự báo): 50.000 lượt xem/tháng ở các bài có link × CTR 5% × CR 4% × AOV 400.000đ × hoa hồng 6% → 50.000 × 0,05 × 0,04 × 400.000 × 0,06 = **2.400.000đ/tháng**. Nếu bị chạm trần hoa hồng/đơn của sàn thì thấp hơn.

→ Affiliate một mình **chỉ đủ nuôi chi phí vận hành nhỏ** ở giai đoạn đầu; doanh thu chính về lâu dài nên đến từ chợ (đẩy tin, gian hàng) và đối tác.

---

## 5. Bán hàng / thương mại điện tử trên chính website

### 5.1. Chợ C2C (tầng 2) — thiết kế để an toàn
- **Xác minh nhiều cấp:** email → số điện thoại (OTP) → (tùy chọn) giấy tờ tùy thân cho người bán nhiều. Đây là thông lệ ở các chợ C2C ([Chop Dawg](https://www.chopdawg.com/how-to-add-identity-verification-and-trust-to-a-marketplace-app/)); Singapore còn chấm điểm an toàn các sàn dựa trên việc xác minh người bán và số vụ lừa đảo ([MHA Singapore](https://www.mha.gov.sg/e-commerce-marketplace-transaction-safety-ratings/)).
- **Đánh giá hai chiều** người mua ↔ người bán, chỉ mở khi có giao dịch được xác nhận.
- **Chuẩn tình trạng A/B/C**, ảnh bắt buộc (serial, khoen, tay quay), cấm ảnh mạng.
- **Danh sách hàng cấm:** máy kích điện/xung điện bắt cá, chất nổ, hóa chất, ngư cụ tận diệt, hàng giả nhái thương hiệu. (Kích điện bị cấm theo Luật Thủy sản 2017 — [Luật Minh Khuê](https://luatminhkhue.vn/muc-phat-dung-xung-dien-kich-dien-danh-bat-ca-thuy-san.aspx).)
- **Báo cáo + kiểm duyệt**: nút báo cáo trên mọi tin; tự động gắn cờ tin trùng ảnh, tài khoản mới đăng giá quá rẻ.
- **Chế độ "Đổi đồ"**: tin dạng *Đổi* có trường "Muốn đổi lấy…" và "Bù thêm (nếu có)" — đáp ứng đúng yêu cầu "trao đổi" của cộng đồng.

### 5.2. Giao dịch qua nền tảng (tầng 3)

| Thành phần | Lựa chọn tại Việt Nam | Ghi chú |
|---|---|---|
| Thanh toán QR chuyển khoản | **payOS** (tạo mã VietQR riêng cho từng đơn, webhook cập nhật trạng thái; có plugin WooCommerce và module Odoo) | [WordPress – payOS](https://cn.wordpress.org/plugins/payos/), [Odoo – payOS](https://apps.odoo.com/apps/modules/18.0/payment_payos). VietQR chạy trên hạ tầng Napas ([Home Credit](https://www.homecredit.vn/blog/thanh-toan-tra-sau-bang-ma-viet-qr-101)). **Tôi chưa tìm được biểu phí chính thức** — xem payos.vn |
| Cổng thẻ/ví | VNPay, MoMo, ZaloPay… | Phí và thủ tục: liên hệ trực tiếp, tôi chưa kiểm chứng được |
| Vận chuyển | GHN, GHTK, Viettel Post, J&T… (đều có API) | Cần thùng/ống bảo vệ cần câu dài — đặt quy cách đóng gói trong quy chế |
| Nền tảng bán hàng có sẵn | Sapo, Haravan (nhiều shop đồ câu đang dùng Sapo), WooCommerce | Nhanh nếu Homies tự bán hàng riêng (merch, đồ nhãn riêng) |
| **"Homies Safe" — giữ tiền đến khi nhận hàng** | **Không tự giữ tiền của người khác.** Hợp tác đơn vị trung gian thanh toán có giấy phép | Hoạt động trung gian thanh toán thuộc diện cấp phép của Ngân hàng Nhà nước (quy định về thanh toán không dùng tiền mặt, hiện là Nghị định 52/2024/NĐ-CP — **cần luật sư xác nhận phạm vi**) |

**Quy trình đề xuất cho Homies Safe:** người mua thanh toán qua đối tác → tiền tạm giữ → người bán gửi hàng (mã vận đơn) → người mua xác nhận trong 3 ngày sau khi nhận (hoặc tự xác nhận khi hết hạn) → giải ngân trừ phí. Khiếu nại trong thời hạn → tạm khóa → ban quản trị phân xử theo quy chế. (Cơ chế giữ tiền trung gian là biện pháp tin cậy cốt lõi ở chợ C2C — [Greip](https://greip.io/blog/Building-Trust-in-Online-Marketplaces-Best-Practices-for-Ensuring-Secure-Transactions-10).)

### 5.3. Chia sẻ doanh thu với cộng đồng (gắn với phễu Bước 2)
- Thành viên viết bài review/hành trình có link affiliate được nhận **một phần hoa hồng** (ví dụ 30–50%, tùy chính sách Homies) — thanh toán hằng tháng khi vượt ngưỡng tối thiểu.
- **Lưu ý thuế:** khoản chi trả này là thu nhập của cá nhân; cần kế toán tư vấn nghĩa vụ khấu trừ thuế TNCN trước khi triển khai (tôi chưa kiểm chứng mức cụ thể).

---

## 6. Pháp lý cần làm (cập nhật quan trọng 2026)

1. **Luật Thương mại điện tử số 122/2025/QH15** được Quốc hội thông qua ngày 10/12/2025, **có hiệu lực từ 01/7/2026** ([LuatVietnam](https://luatvietnam.vn/tin-van-ban-moi/da-co-luat-thuong-mai-dien-tu-2025-so-122-2025-qh15-186-106402-article.html), [Thư viện Pháp luật – bản tiếng Anh](https://thuvienphapluat.vn/van-ban/EN/Thuong-mai/Law-122-2025-QH15-Electronic-Commerce/703876/tieng-anh.aspx)). Luật siết trách nhiệm nền tảng, **định danh người bán**, livestream bán hàng (xác thực danh tính người livestream từ 01/7/2026) ([VnEconomy](https://vneconomy.vn/luat-thuong-mai-dien-tu-2025-cam-cuong-va-minh-bach-hoa-thi-truong.htm), [Cổng PBGDPL Cần Thơ](https://pbgdpl.cantho.gov.vn/trach-nhiem-cua-chu-quan-nen-tang-thuong-mai-dien-tu-trong-hoat-dong-livestream-ban-hang)). Một nguồn nhắc tới nghị định hướng dẫn có hiệu lực cùng ngày; **tôi chưa đọc được nguyên văn nghị định** — cần tra số hiệu và nội dung trên vbpl.vn/thuvienphapluat.vn.
   - Homies có chợ cho người khác đăng bán ⇒ nhiều khả năng thuộc nhóm **nền tảng thương mại điện tử trung gian** ⇒ phải có **quy chế hoạt động**, cơ chế định danh người bán, xử lý khiếu nại, gỡ hàng cấm, và thủ tục với Bộ Công Thương (online.gov.vn). **Bắt buộc nhờ luật sư xác định đúng loại hình theo luật mới trước khi mở chợ.**
   - Trước luật mới, theo Nghị định 52/2013 sửa đổi bởi Nghị định 85/2021: web bán hàng có chức năng đặt hàng thì **thông báo**; sàn giao dịch TMĐT thì **đăng ký** với Bộ Công Thương ([Luật Minh Khuê](https://luatminhkhue.vn/ca-nhan-co-duoc-lap-website-cung-cap-dich-vu-thuong-mai-dien-tu-khong.aspx), [LuatVietnam – NĐ 85/2021](https://luatvietnam.vn/doanh-nghiep/diem-moi-cua-nghi-dinh-85-2021-ve-thuong-mai-dien-tu-561-33179-article.html)). Khung này đã/đang được thay thế — chỉ dùng để hiểu bối cảnh.
2. **Pháp nhân:** nên thành lập công ty/hộ kinh doanh trước khi thu tiền đẩy tin hoặc mở thanh toán.
3. **Bảo vệ dữ liệu cá nhân:** thu thập SĐT, CCCD, vị trí ⇒ cần chính sách bảo mật, xin đồng ý rõ ràng, tối thiểu hóa dữ liệu (không lưu ảnh CCCD nếu đối tác eKYC đã xác minh).
4. **Công bố affiliate** — mẫu:
   > *"Bài viết có chứa liên kết tiếp thị. Nếu bạn mua hàng qua các liên kết này, Homies Fishing có thể nhận hoa hồng từ người bán mà bạn không phải trả thêm. Chúng tôi chỉ giới thiệu sản phẩm mà đội ngũ hoặc thành viên đã dùng hoặc tìm hiểu kỹ."*
5. **Quảng cáo trung thực:** không khẳng định "chính hãng", "tốt nhất" nếu không kiểm chứng; review của thành viên được tài trợ phải gắn nhãn "Được tài trợ".

---

## 7. Lộ trình triển khai

| Tuần | Việc |
|---|---|
| 1–2 | Đăng ký Shopee Affiliate, ACCESSTRADE; làm route `/go/`, bảng `affiliate_links`; trang Công bố affiliate |
| 3–4 | Viết 5 bài "ý định mua cao" (nhập môn, so sánh); gắn hộp sản phẩm; đặt sub_id theo bài |
| 5–8 | Mở chợ C2C bản thử (đăng tin, chat, đánh giá, báo cáo, danh sách hàng cấm); ký 1–3 shop đối tác + mã giảm giá "HOMIES" |
| 8+ | Tư vấn luật sư về Luật TMĐT 2025; thành lập pháp nhân; chọn đối tác trung gian thanh toán cho Homies Safe; tích hợp payOS + API vận chuyển |
| Hằng tháng | Báo cáo: click/đơn/hoa hồng theo bài; tỷ lệ link chết; số tin chợ bị báo cáo |

---

## 8. Checklist nhanh
- [ ] Mọi link affiliate đi qua `/go/` và có `rel="sponsored"`
- [ ] Có dòng công bố affiliate ở đầu bài + trang chính sách
- [ ] Không ghi cứng giá; ghi ngày cập nhật
- [ ] Danh sách hàng cấm ở chợ (kích điện, chất nổ, hàng giả)
- [ ] Quy chế chợ + quy trình khiếu nại công khai
- [ ] Luật sư xác nhận nghĩa vụ theo Luật TMĐT 122/2025/QH15 trước khi mở giao dịch qua nền tảng
- [ ] Không tự giữ tiền người dùng — dùng đối tác trung gian thanh toán có phép
