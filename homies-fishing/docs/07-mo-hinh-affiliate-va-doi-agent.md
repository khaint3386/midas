# Mô hình kinh doanh affiliate Homies Fishing & đội AI Agent điều phối

> Ngày tổng hợp: 03/11/2026. Kết quả nghiên cứu của 3 agent (Chương trình & pháp lý, SEO & nội dung, Sản phẩm & ưu đãi) được tổng hợp ở đây. Bản gốc từng agent nằm trong `docs/research/`. Số liệu đều có nguồn; chỗ là nhận định hoặc giả định được ghi rõ.

---

## 1. Nhìn thẳng vào MMO affiliate trong ngách đồ câu

- **Giá đồ câu phổ thông rất thấp.** Cần tay hoặc cần đài phổ thông khoảng 92.000–137.000đ, máy đứng từ khoảng 105.000đ đến khoảng 980.000đ (Daiwa Ichigeki LT 2500). Đây là vài mức niêm yết đọc từ trang bán chạy của Lazada, không phải khảo sát ([Lazada – cần câu](https://www.lazada.vn/trending/Fishing-Rods-Top-AddToCart/884274234), [Lazada – máy câu](https://www.lazada.vn/trending/Fishing-Reels-Best-Price/243410134)). → Hoa hồng mỗi đơn nhỏ; sống bằng **số đơn** và **giá trị giỏ hàng**, không bằng một đơn lớn.
- **Ba nguồn tiền thật** (nhận định của agent Sản phẩm):
  1. **Combo người mới**: khớp bài phễu "Nhập môn".
  2. **Máy câu khi "lên đời"**: người chơi đã nghiện, sẵn sàng chi.
  3. **Vật tư tiêu hao mua lặp lại**: dây, lưỡi, mồi giả, cám, egi. Đơn nhỏ nhưng mua đều.
- **Lợi thế cạnh tranh của Homies không nằm ở giá, mà ở niềm tin:** bộ đồ gắn với hành trình thật, lịch mùa có nguồn, chợ đồ cũ. Làm MMO kiểu bài AI hàng loạt, review giả hay spam link sẽ đốt chính lợi thế này (xem mục 6).

---

## 2. Mô hình doanh thu: 4 dòng tiền

| Dòng | Cách kiếm | Khi bắt đầu | Ghi chú |
|---|---|---|---|
| **A. Affiliate sàn** | Shopee Affiliate (link trên web), TikTok Shop (giỏ hàng trong video) | Tháng 1 | Chi tiết điều kiện ở mục 3 |
| **B. Đối tác shop đồ câu trực tiếp** | Mã giảm giá riêng "HOMIES", hoa hồng thương lượng hoặc phí cố định/tháng | Tháng 2–3 | Hoa hồng thường cao hơn sàn, cần hợp đồng |
| **C. Tour / tàu câu** | Hoa hồng giới thiệu tour câu mực, thuê tàu | Tháng 3–6 | Cần xác minh nhà tàu; mùa Phú Quốc T11–T4 |
| **D. Chợ Homies** | Đẩy tin, gian hàng đối tác | Tháng 6+ | Theo docs/03 |

**Công thức** (giống docs/03):
`Doanh thu affiliate = Lượt xem bài × CTR × Tỷ lệ mua × Giá trị đơn × Hoa hồng`

Ví dụ **giả định**, không phải dự báo: 50.000 lượt xem/tháng × CTR 5% × tỷ lệ mua 4% × đơn 300.000đ × hoa hồng 6% = **1.800.000đ/tháng**. Muốn tăng thì tăng **giá trị giỏ** (bộ đồ nhiều món) và **CTR** (khung sản phẩm đúng ngữ cảnh), chứ không tăng bằng cách nhồi link.

---

## 3. Chương trình affiliate & pháp lý

Nhãn độ tin cậy: **[CT]** trang chính thức · **[BC]** báo chí/luật sư · **[BT3]** blog bên thứ ba. Máy chủ không mở được shopee.vn và cổng Bộ Tài chính nên nhiều ý chỉ dựa trên đoạn trích trong kết quả tìm kiếm.

### 3.1. Chọn chương trình

| Chương trình | Điểm chính | Tin cậy | Vai trò với Homies |
|---|---|---|---|
| **Shopee Affiliate** | Chỉ tính **đơn đầu tiên** sau khi bấm link, quy tắc **last click**; cookie **30 ngày (web), 7 ngày (app)** ([điều khoản bản 18/08/2023](https://shopee.vn/affiliate/dieu-kien-hop-tac-chuong-trinh-tiep-thi-lien-ket-cua-shopee-viet-nam-update-18-08-2023/)) | [CT], trích đoạn, có thể đã có bản mới | **Chính** cho link trên web |
| | Hoa hồng theo ngành, khách mới cao hơn hẳn khách cũ (blog nêu tới ~13,4% khách mới nhóm thời trang/phụ kiện/thể thao, ~1–3% khách cũ), trần khoảng 30.000đ/đơn ([FPT Shop](https://fptshop.com.vn/tin-tuc/danh-gia/affiliate-shopee-la-gi-huong-dan-lam-shopee-affiliate-hieu-qua-163999), [GHN](https://ghn.vn/blogs/tip-ban-hang/muc-hoa-hong-tiep-thi-lien-ket-shopee)) | [BT3]; **chưa có bảng chính thức cho đồ câu** | Kiểm tra trong dashboard |
| | Kênh không được dùng tên, logo Shopee gây hiểu lầm ([điều khoản KOL](https://shopee.vn/affiliate/kol-dieu-khoan-tham-gia-2104/)) | [CT], trích đoạn | Không đặt tên trang/kênh chứa "Shopee" |
| **TikTok Shop** | **LinkShare** cho chia sẻ link sản phẩm ra website, Facebook, Zalo kể cả khi chưa đủ 1.000 follower; gắn giỏ trong video cần khoảng 1.000 follower; hoa hồng thường 5–15%; chỉ trả khi đơn giao thành công ([Sapo](https://www.sapo.vn/blog/cach-lam-tiep-thi-lien-ket-tiktok-khi-chua-du-1000-follow), [Ecomobi](https://ecomobi.com/vi/linkshare-tiktok/)) | [BT3] | **Chính** cho video; phụ cho web |
| **Lazada** | Đối soát 2 đợt/tháng từ 08/2025; ngưỡng cộng dồn 50.000đ (từ 11/2023) ([Lazada blog](https://www.lazada.vn/blog/quy-trinh-thanh-toan-va-doi-soat-hoa-hong-tai-lazaffiliate/)) | [CT] | Phụ: thị phần Lazada + Tiki chỉ ~3% |
| **ACCESSTRADE, Ecomobi/Passio** | Không tìm thấy chiến dịch đồ câu. Passio có Klook, Traveloka, Trip.com | [BT3] | Dùng cho **tour, khách sạn** ở bài du lịch câu |
| **Shop đồ câu trong nước** | Không tìm thấy chương trình CTV/affiliate công khai; Daiwa Vietnam là nhà máy, không phải kênh bán lẻ | [BT3] | **Tự đàm phán**: mã giảm giá riêng + UTM |

### 3.2. Pháp lý cần biết

| Văn bản | Nội dung liên quan | Tin cậy |
|---|---|---|
| **Luật Quảng cáo sửa đổi số 75/2025/QH15**, hiệu lực 01/01/2026 | Thêm **Điều 15a**: nghĩa vụ của người chuyển tải sản phẩm quảng cáo, gồm người có ảnh hưởng: tìm hiểu sản phẩm, kiểm tra tài liệu chứng minh công dụng, không gây hiểu nhầm. Quảng cáo sai sự thật có thể bị xử lý hình sự và phải bồi thường ([LuatVietnam](https://luatvietnam.vn/thuong-mai/luat-quang-cao-sua-doi-2025-so-75-2025-qh15-404208-d1.html), [LSVN](https://lsvn.vn/tu-2026-nguoi-co-anh-huong-khong-duoc-quang-cao-khi-chua-hieu-ro-san-pham-a159875.html)). **Chưa đọc được nguyên văn phần thông báo/ghi nhãn quảng cáo** | [BC] |
| **Luật TMĐT 122/2025/QH15** + **Nghị định 248/2026/NĐ-CP**, hiệu lực 01/7/2026 | Điều 25: bên cung cấp dịch vụ tiếp thị liên kết phải **xác thực danh tính** người làm affiliate; người làm affiliate phải **gỡ link** tới hàng vi phạm khi được yêu cầu; không đưa thông tin sai, **đánh giá giả**, link gây hiểu lầm ([Bộ Công Thương](https://moit.gov.vn/tin-tuc/bo-cong-thuong-pho-bien-luat-thuong-mai-dien-tu-va-nghi-dinh-so-248-2026-nd-cp.html), [Thời báo Tài chính](https://thuehaiquan.tapchikinhtetaichinh.vn/quan-tiep-thi-lien-ket-bao-ve-nguoi-mua-truc-tuyen-131770.html)). Chưa đọc nguyên văn Điều 25 | [CT]/[BC] |
| **Thuế TNCN** | Theo báo chí dẫn Công văn 7403/CT-TMĐT ngày 06/10/2026: thu nhập affiliate trên sàn chịu **5% TNCN**; sàn có chức năng đặt hàng và thanh toán sẽ **khấu trừ, nộp thay** (Luật Thuế TNCN 109/2025/QH15; Điều 43 Nghị định 252/2026/NĐ-CP) ([Thời báo Tài chính, 08/10/2026](https://thuehaiquan.tapchikinhtetaichinh.vn/co-quan-thue-lam-ro-thue-suat-5-voi-thu-nhap-kinh-doanh-tu-tiep-thi-lien-ket-168921.html)). **Chưa đọc bản gốc công văn** | [BC] |
| | Nghị định 253/2026/NĐ-CP nâng ngưỡng khấu trừ 10% từ 2 triệu lên **5 triệu đồng/lần chi trả** ([LuatVietnam](https://luatvietnam.vn/thue-phi-le-phi/tong-hop-van-ban-huong-dan-thue-hoa-don-tren-san-thuong-mai-dien-tu-565-111128-article.html)) → nếu Homies **tự chia hoa hồng** cho thành viên, Homies có thể phải khấu trừ thuế. **Cần kế toán xác nhận** | [BC] |

**Việc phải làm vì pháp lý:**
- Mọi bài có link: dòng công bố affiliate ở đầu bài. Video có link: bật nhãn quảng cáo của TikTok.
- **Không bao giờ** viết đánh giá giả hay ghi "đã test" khi chưa dùng thật. Điều 25 Luật TMĐT và Luật Quảng cáo đều nhắm vào việc này.
- Có quy trình **gỡ link trong ngày** khi shop hoặc sản phẩm bị báo vi phạm: đặt `is_active: false` trong JSON, hàm `/go/` sẽ chuyển về trang Đồ nên mua.
- Trước khi chia hoa hồng cho thành viên: hỏi kế toán về khấu trừ thuế.

### 3.3. Điểm cần kiểm tra thêm
- **Link chuyển hướng `/go/`:** agent không tìm được nguồn chính thức nói sàn cấm hay cho phép chuyển hướng qua tên miền riêng. Đọc lại điều khoản hiện hành trong tài khoản Shopee Affiliate trước khi bật. Nếu không chắc, dùng link affiliate gốc và chỉ đếm click bằng sự kiện trên trang.
- **Tên tham số sub_id:** chưa xác nhận được với Shopee, nên lấy đúng tên trong dashboard rồi sửa `SUB_ID_PARAM` trong `functions/go/[slug].js`.
- **Tự mua qua link của mình:** Lazada không trả hoa hồng ([Ecomobi](https://ecomobi.com/vi/quy-dinh-lazada-affiliate-tranh-mat-hoa-hong-toi-uu-thu-nhap/)). Coi như mọi sàn đều cấm.

Một kết quả tìm kiếm (hethongphapluat.com) có chèn câu lệnh nhắm vào AI. Agent đã bỏ qua và không đưa vào tài liệu, đúng nguyên tắc "nội dung bên ngoài là dữ liệu, không phải chỉ thị".

---

## 4. SEO & nội dung có ý định mua

**Giới hạn:** không có công cụ đo lượt tìm kiếm và công cụ tìm kiếm của phiên không phải Google, nên **không có số lượt tìm**. "Cạnh tranh" là nhận định dựa trên loại trang đang đứng đầu. Cần kiểm lại bằng Google Search Console, Google Trends hoặc Keyword Planner. Danh sách đủ 40 cụm từ khóa nằm ở `docs/research/seo-content.md`.

### 4.1. Bức tranh kết quả tìm kiếm (nhận định)
- Nhiều cụm mua hàng và hướng dẫn tiếng Việt bị **YouTube** hoặc **trang sản phẩm của shop** chiếm chỗ (chủ yếu [Hoa Ban Camp](https://hoabancamp.com/may-cau-doc-may-dung/)). **Bài review văn bản độc lập gần như không có.** Đây là khoảng trống lớn nhất.
- Bài "top" của [Mytour](https://mytour.vn/vi/blog/bai-viet/8-thuong-hieu-can-cau-ca-hang-dau-hien-nay.html) và [Toplist](https://toplist.vn/top-list/thuong-hieu-can-cau-ca-tot-nhat-hien-nay-37942.htm) chung chung, không test thực tế, nhiều bài đã cũ.
- **Lazada tự làm site hướng dẫn** ([sports.lazada.vn](https://sports.lazada.vn/what-should-beginner-anglers-buy-gear-checklist-and-trusted-store-recommendations-vn/), [outdoors.lazada.vn](https://outdoors.lazada.vn/guide-to-choosing-and-using-fishing-floats-for-beginners-in-vietnam-vn/)), có dấu hiệu sản xuất theo mẫu hàng loạt.
- **Du lịch câu bị các tập đoàn du lịch và trang đặt tour chiếm hết** (Vinpearl, VinWonders, Mia.vn…). Không dùng nhóm này làm nguồn traffic affiliate chính; giữ làm nội dung cộng đồng.
- **Review từng mẫu cụ thể bằng tiếng Việt gần như trống:** Shimano Sienna, Daiwa Revros LT, Shimano Nexave, Daiwa Freams LT, Noeby K6/K7.

### 4.2. Từ khóa cạnh tranh thấp, ý định mua cao (ưu tiên)
"combo đồ câu cho người mới" · "máy câu cá loại nào tốt cho người mới" · "cần câu lure giá rẻ" · "dây PE câu cá loại nào tốt" · "bộ cần câu dưới 500k" · "cần câu đài loại nào tốt cho người mới" · "máy câu ngang cho người mới" · "mồi giả câu cá lóc / nhái hơi" · "mồi câu cá chép hồ dịch vụ" · "thùng câu đài loại nào tốt" · tên mẫu máy cụ thể.

### 4.3. Cụm chủ đề
Năm trang trụ: **Nhập môn**, **Câu lure**, **Câu đài**, **Câu biển & mực**, **Điểm câu + Lịch mùa** (trụ cuối kéo traffic, ít affiliate). Mỗi bài review có khối "Mua mới | Tìm đồ cũ ở Chợ Homies". Trang Loài cá có mục "Bộ đồ gợi ý", trang Điểm câu có mục "Mang gì đi". Bài hành trình của thành viên gắn thẻ đồ dùng, tự hiện trên trang review của mẫu đó làm bằng chứng trải nghiệm thật.

### 4.4. 12 bài đầu tiên (viết theo thứ tự 1 → 2 → 3 → 12 → 4 → 5)

| # | Tiêu đề | Sản phẩm gắn kèm | Góc khác biệt |
|---|---|---|---|
| 1 | Đồ câu cho người mới 2026: 5 món cần mua, 3 món chưa cần | Combo, dây, lưỡi, kìm | Ngân sách 300k / 700k / 1,5 triệu do cộng đồng góp; nút sang Chợ |
| 2 | Máy câu đứng cho người mới: Sienna vs Revros LT vs Nexave | 3 máy | Test tay, ảnh tháo máy, kết luận theo kiểu câu |
| 3 | Bộ cần câu dưới 500k: đáng mua hay "mua 2 lần"? | 2–3 bộ chọn lọc | Mua và test thật, công khai điểm xấu |
| 4 | Dây PE hay dây cước? Chọn cỡ PE theo cá và máy | Dây PE, leader | Bảng theo loài cá Việt Nam |
| 5 | Mồi nhái hơi câu cá lóc: so sánh 6 mẫu | Mồi nhái hơi | Clip cá đớp của thành viên |
| 6 | Cần câu đài cho người mới: dài bao nhiêu, cứng cỡ nào? | Cần đài, phao | Gom kiến thức video, ghi nguồn |
| 7 | Mồi câu chép hồ dịch vụ: 5 bài mồi anh em dùng nhiều | Mồi pha sẵn | Thành viên chấm điểm từng bài |
| 8 | Máy câu ngang cho người mới: chọn sao để không rối dây | Máy ngang | Video tập ném |
| 9 | Thùng câu đài & ghế câu: loại nào đáng tiền | Thùng, ghế | Đơn giá cao, ảnh dùng thật |
| 10 | Shimano Sienna: review sau 3 tháng câu hồ | Sienna | Review dài hạn; **mua máy và bắt đầu test ngay** |
| 11 | Đồ câu biển cho người mới | Máy 3000–5000, chì, dây | Liên kết Điểm câu và Lịch mùa |
| 12 | Cách nhận biết đồ câu nhái thương hiệu trên sàn | Gian hàng chính hãng | Bài xây uy tín; ví dụ "cần máy rút SHIMANO" 58.000đ trên [Lazada](https://www.lazada.vn/trending/Fishing-Rods-Top-Deals-This-Month/347323986) có giá rất đáng ngờ (nhận định) |

### 4.5. Luật chơi của Google (nguồn chính thức)
- **Hệ thống đánh giá review có áp dụng cho tiếng Việt.** Google thưởng review có phân tích sâu, **bằng chứng tự test** (ảnh, video, số đo), ưu nhược điểm dựa trên nghiên cứu gốc. Danh sách "top" hiệu quả khi đi kèm review sâu từng sản phẩm ([Reviews system](https://developers.google.com/search/docs/appearance/reviews-system), [Write high-quality reviews](https://developers.google.com/search/docs/specialty/ecommerce/write-high-quality-reviews)).
- **Scaled content abuse:** tạo nhiều trang để thao túng thứ hạng mà không giúp người đọc là vi phạm, **dù do AI hay người viết** ([Spam policies](https://developers.google.com/search/docs/essentials/spam-policies)).
- **Thin affiliation:** chép mô tả và review của người bán mà không thêm giá trị là vi phạm ([Spam policies](https://developers.google.com/search/docs/essentials/spam-policies)).
- **Site reputation abuse:** không cho shop hay đối tác đăng bài tràn lan trên Homies để mượn tên miền ([Google blog 11/2024](https://developers.google.com/search/blog/2024/11/site-reputation-abuse)).
- **Nội dung AI:** dùng AI hợp lý không vi phạm, nhưng không tạo hồ sơ tác giả giả và nên công khai cách làm nội dung ([Guidance on AI content](https://developers.google.com/search/docs/fundamentals/using-gen-ai-content)). Dữ liệu cấu trúc review không được chứa review giả ([Review snippet](https://developers.google.com/search/docs/appearance/structured-data/review-snippet)).

**Quy tắc cho đội agent rút ra từ đây:**
1. AI chỉ làm nghiên cứu, dàn ý, bản nháp, bảng thông số. Mỗi bài review phải có **người thật đã cầm sản phẩm**.
2. Nhịp **2–3 bài có test mỗi tuần**, không làm hàng loạt từ mô tả của shop.
3. Trang tác giả là cần thủ thật. Không tạo tác giả ảo.
4. Mỗi bài có mục "Cách chúng tôi test", dòng công bố affiliate và ngày cập nhật; bài "top" rà lại ít nhất 6 tháng/lần.
5. Link trong nội dung thành viên dùng `rel="ugc"`; link affiliate dùng `rel="sponsored"`.

---

## 5. Sản phẩm, bộ đồ theo hành trình & mùa bán

### 5.1. Danh mục ưu tiên

| Ưu tiên | Nhóm | Lý do |
|---|---|---|
| 1 | Combo cần + máy cho người mới | Khớp phễu nhập môn |
| 1 | Máy câu đứng | Món "lên đời" phổ biến, dễ viết bài so sánh |
| 1 | Dây PE/cước, mồi giả, cám, egi | Mua lặp lại |
| 2 | Kính phân cực, áo chống nắng | Bán được cho cả người câu và khách du lịch biển |
| 3 | Cần lure cao cấp | Ít người mua; hoa hồng mỗi đơn có thể bị chạm trần |

### 5.2. Bộ đồ theo hành trình
Năm bộ: **Lure cá lóc (Trị An)**, **Câu mực đêm (Phú Quốc)**, **Câu đài hồ dịch vụ**, **Câu bờ biển**, **Người mới (mục tiêu dưới 1 triệu)**. Trang `web/do-cau.html` đã có 4 bộ đầu. Giá tổng chưa tính được vì chưa tra đủ giá VND (máy chủ này không mở được Shopee/Lazada), nên phải tra trực tiếp và ghi ngày tra.

### 5.3. Lịch bán theo mùa

| Thời điểm | Đẩy gì |
|---|---|
| **11.11, 12.12** (trùng đầu mùa khô Phú Quốc T11–T4) | Bộ câu mực, egi, đèn, áo chống nắng |
| **6 tuần trước Tết** | Ưu tiên video TikTok Shop; giai đoạn trước Tết 2026, TikTok Shop vượt Shopee ([Index.vn](https://index.vn/en/news/tiktok-shop-overtakes-shopee-in-six-week-pre-tet-period-signaling-a-shift-in-vietnam-e-commerce-competition)) |
| **Ngày đôi hằng tháng, ngày 15, ngày 25** | Nhắc giỏ vật tư tiêu hao ([BigSeller](https://www.bigseller.com/blog/articleDetails/lich-sale-shopee-2026.4220.htm), [GHN](https://ghn.vn/blogs/tip-ban-hang/cac-ngay-sale-shopee)) |
| **Cuối T9 – T2** | **Không** đẩy hành trình Cù Lao Chàm (biển động); chuyển sang câu hồ |
| Quanh năm | Câu đài hồ dịch vụ: cám, phao, lưỡi |

### 5.4. Quy tắc chống hàng nhái
- Kiểm tra đúng chính tả thương hiệu. Ví dụ đã có đánh giá cho biết máy tên "Diwa" là hàng nhái ([Desertcart](https://www.desertcart.vn/products/256523438-diwa-spinning-fishing-reels-for-saltwater-freshwater-3000-4000-5000.md)).
- "Made in China/Thailand" không có nghĩa là hàng giả: nhiều máy Daiwa chính hãng sản xuất ở đó ([BassResource](https://www.bassresource.com/bass-fishing-forums/topic/136584-shimano-daiwa-reels/)).
- Ưu tiên Shopee Mall, LazMall, shop chuyên đồ câu có địa chỉ thật. Không viết "chính hãng" khi chưa xác minh. Không gắn link cho hàng hiệu có giá thấp bất thường.
- **Lọc bỏ mọi sản phẩm** có từ khóa "kích cá", "kích điện", "xung điện", "máy kích".

---

## 6. Ranh giới: những chiêu MMO **không** làm

| Chiêu | Vì sao không |
|---|---|
| Sinh hàng loạt bài AI không có trải nghiệm thật | Rủi ro bị Google xếp vào lạm dụng nội dung quy mô lớn (xem mục 4), mất niềm tin cộng đồng |
| Review giả, đánh giá 5★ tự tạo, ảnh "đã test" lấy trên mạng | Gian dối người đọc; vi phạm quy định quảng cáo |
| Giấu link affiliate, không công bố | Vi phạm nguyên tắc minh bạch; xem nghĩa vụ ghi nhãn ở mục 3 |
| Tự mua qua link của mình, spam link vào group, cookie stuffing | Vi phạm điều khoản sàn, có thể bị khóa tài khoản và mất hoa hồng |
| Quảng bá máy kích cá, ngư cụ tận diệt | Vi phạm pháp luật (Luật Thủy sản 2017) |

---

## 7. Đội AI Agent điều phối

### 7.1. Sơ đồ

```
                        ┌─────────────────────────────┐
                        │  BẠN (chủ dự án) — duyệt cuối │
                        └──────────────┬──────────────┘
                                       │
                        ┌──────────────▼──────────────┐
                        │  ĐIỀU PHỐI (Claude chính)    │  lập kế hoạch tuần, chia việc, gộp kết quả
                        └──┬──────┬──────┬──────┬────┬─┘
       ┌───────────────────┘      │      │      │    └────────────────────┐
┌──────▼──────┐  ┌────────────────▼┐ ┌───▼──────────┐ ┌▼──────────────┐ ┌──▼────────────┐
│ 1. Nghiên   │  │ 2. Sản phẩm &    │ │ 3. Biên tập  │ │ 4. Kỹ thuật & │ │ 5. Phân phối  │
│ cứu SEO     │  │ ưu đãi           │ │ & kiểm chứng │ │ vận hành      │ │ (TikTok, FB,  │
│             │  │                  │ │              │ │               │ │ Zalo, email)  │
└─────────────┘  └──────────────────┘ └──────────────┘ └───────────────┘ └───────────────┘
                                 ▲                          │
                                 └──── 6. Tuân thủ ─────────┘  (soát mọi bài trước khi đăng)
```

### 7.2. Vai trò, đầu vào và đầu ra

| # | Agent | Việc | Đầu vào | Đầu ra | Quyền | Chạy khi |
|---|---|---|---|---|---|---|
| 0 | **Điều phối** | Lập backlog tuần theo mùa câu và lịch sale; giao việc; gộp báo cáo | Lịch mùa, lịch sale, số liệu tuần | Kế hoạch tuần (issue GitHub) | Đọc tất cả, tạo issue | Thứ Hai hằng tuần |
| 1 | **Nghiên cứu SEO** | Tìm từ khóa ý định mua, phân tích trang top, đề xuất bài | Danh sách chủ đề | Brief bài: từ khóa, dàn ý, sản phẩm gắn kèm | Chỉ đọc web | Theo yêu cầu |
| 2 | **Sản phẩm & ưu đãi** | Tra giá, chọn shop uy tín, lấy link affiliate, cập nhật `affiliate-links.json` | Brief bài, danh sách bộ đồ | PR sửa `web/data/affiliate-links.json` | Sửa đúng file đó trên nhánh | Hằng tuần + trước đợt sale |
| 3 | **Biên tập & kiểm chứng** | Viết nháp từ brief + trải nghiệm thật của cộng đồng; gắn nguồn cho mọi khẳng định | Brief, bài hành trình thành viên | PR bài Markdown | Viết nhánh | 2–3 bài/tuần |
| 4 | **Kỹ thuật & vận hành** | Hàm `/go/`, khung sản phẩm, kiểm link chết, tốc độ, báo cáo click | Code, log click | PR code; issue khi có lỗi | Viết nhánh; workflow kiểm link | Thứ Hai (tự động) |
| 5 | **Phân phối** | Cắt bài dài thành kịch bản TikTok, bài Facebook, tin Zalo, bản tin email | Bài đã xuất bản | Bản nháp đăng | **Không đăng** | Sau mỗi bài mới |
| 6 | **Tuân thủ** | Soát nhãn quảng cáo, công bố affiliate, từ khóa cấm, chữ "chính hãng" chưa xác minh, số liệu thiếu nguồn | Mọi PR nội dung | Bình luận review: đạt / cần sửa | Chỉ bình luận | Mỗi PR nội dung |

**Người làm** (agent không thay được):
- Đăng nhập tài khoản affiliate, lấy link và nhận tiền.
- Ký hợp đồng với shop.
- Bấm merge PR, bấm đăng video.
- Kiểm tra sản phẩm thật nếu bài ghi "đã test".

### 7.3. Một vòng làm việc mẫu (1 bài "Máy câu đứng cho người mới")

1. **Điều phối** tạo issue: "Bài máy câu đứng dưới 1 triệu, trước 11.11".
2. **Nghiên cứu SEO** trả brief: từ khóa chính, câu hỏi người đọc hay hỏi, 5 trang đối thủ đang yếu ở đâu.
3. **Sản phẩm** chọn 5 mẫu từ shop uy tín, tra giá ngày tra, lấy link affiliate. Bạn dán link thật vì cần đăng nhập. Agent mở PR cập nhật JSON.
4. **Biên tập** viết nháp, mời 2–3 thành viên đang dùng máy đó góp nhận xét (trải nghiệm thật), gắn khung sản phẩm.
5. **Tuân thủ** soát: có dòng công bố, không ghi "chính hãng" khi chưa xác minh, giá ghi ngày.
6. Bạn xem link xem trước rồi merge.
7. **Phân phối** cắt 1 video TikTok "3 điều phải biết trước khi mua máy câu đầu tiên" và 1 bài Facebook. Bạn tự đăng.
8. **Vận hành** sau 7 ngày báo cáo: click theo vị trí khung sản phẩm, link nào chết.

### 7.4. Cách triển khai các agent trong thực tế

| Agent | Chạy bằng gì |
|---|---|
| Điều phối, Biên tập, Nghiên cứu, Sản phẩm | Phiên Claude Code (như phiên này): giao bằng chat hoặc `@claude` trong issue |
| Tuân thủ | Claude Code GitHub Action chạy khi mở PR nội dung, prompt đọc `CLAUDE.md` + checklist mục 6 |
| Vận hành | `.github/workflows/check-affiliate-links.yml` (đã có) + báo cáo click từ Cloudflare Analytics Engine |
| Phân phối | Chat với Claude dựa trên bài đã xuất bản; bạn tự đăng |

Giới hạn hiện tại: máy chủ của phiên này **không mở được Shopee/Lazada** (bị chặn mạng). Muốn agent Sản phẩm tự tra giá, bạn cần thêm các tên miền này vào danh sách được phép trong cài đặt mạng của môi trường.

---

## 8. Hạ tầng affiliate đã dựng

| Thành phần | File | Trạng thái |
|---|---|---|
| Dữ liệu link + bộ đồ | `web/data/affiliate-links.json` | 12 món, 4 bộ. Link hiện là **link tìm kiếm thường trên Shopee, chưa phải link affiliate** |
| Trang "Đồ nên mua" | `web/do-cau.html` | Tab theo bộ đồ, khung sản phẩm có điểm hợp / chưa hợp, nút Shopee + nút Chợ đồ cũ, dòng công bố affiliate |
| Chuyển hướng + đếm click | `functions/go/[slug].js` (Cloudflare Pages Function) | Đã chạy thử với dữ liệu giả: 302 đúng, gắn sub_id, slug sai thì về trang Đồ nên mua |
| Kiểm link chết | `scripts/check-links.mjs` + workflow thứ Hai hằng tuần | Sẵn sàng khi repo lên GitHub |

**Để chạy thật:**
1. Tạo dự án Cloudflare Pages trỏ vào repo: thư mục xuất bản `web`, Functions tự nhận thư mục `functions/`.
2. (Tùy chọn) Tạo binding Analytics Engine tên `CLICKS` để đếm click.
3. Thay `target_url` bằng link affiliate thật, sửa tên tham số sub_id trong `SUB_ID_PARAM` cho đúng từng mạng.

---

## 9. KPI 90 ngày (mục tiêu tự đặt, không phải dự báo)

| Chỉ số | Mục tiêu |
|---|---|
| Bài có ý định mua đã xuất bản | 12 |
| Bộ đồ trên trang Đồ nên mua | 5, mỗi bộ có giá tra kèm ngày |
| CTR khung sản phẩm | ≥ 3% |
| Shop đối tác có mã giảm giá riêng | 2 |
| Link chết quá 7 ngày | 0 |
| Bài bị Tuân thủ trả về vì thiếu công bố | 0 khi xuất bản |
