"""Unit test cho logic quyết định khuyến nghị (app/services/recommender._decide).

Đây là phần chịu trách nhiệm "chống hallucination" cuối cùng: dù dữ liệu vào
đúng, quyết định sai thì khuyến nghị vẫn sai. Test dùng dataclass giả lập trực
tiếp (không gọi mạng/vnstock/Gemini) để khoá chặt 5 nhánh hành động.

Chạy: python -m unittest discover -s tests -v   (từ thư mục midas/)
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.ai_analyst import MeaningAssessment
from app.services.four_m import BigFive, FourMResult
from app.services.recommender import _decide
from app.services.vcp import Contraction, TrendTemplate, VCPResult


def make_four_m(*, is_wonderful=True, on_sale=False, moat=85, mgmt=70,
                 current_price=20000.0, mos_price=15000.0, sticker_price=30000.0,
                 data_reliability=100, data_warnings=None) -> FourMResult:
    return FourMResult(
        symbol="TEST",
        big_five=BigFive(roic_avg=15.0, revenue_growth=12.0, eps_growth=11.0,
                          bvps_growth=10.5, fcf_growth=13.0),
        moat_score=moat,
        management_score=mgmt,
        sticker_price=sticker_price,
        mos_price=mos_price,
        current_price=current_price,
        upside_pct=25.0,
        is_wonderful=is_wonderful,
        on_sale=on_sale,
        growth_rate_used=12.0,
        pe_used=18.0,
        data_reliability=data_reliability,
        data_warnings=data_warnings or [],
    )


def make_trend(*, passed_count=8, in_stage2=True, rs_rating=90) -> TrendTemplate:
    return TrendTemplate(
        criteria={f"c{i}": True for i in range(passed_count)},
        rs_rating=rs_rating, passed_count=passed_count, in_stage2=in_stage2,
    )


def make_vcp(*, is_vcp=True, buy_signal=True, trend=None, pivot=21000.0,
             last_volume=3_000_000.0, avg_volume_50=1_500_000.0,
             stop_loss=19_500.0) -> VCPResult:
    return VCPResult(
        symbol="TEST",
        trend=trend or make_trend(),
        contractions=[Contraction(high_date="2026-01-01", low_date="2026-01-10", depth_pct=8.0)],
        is_vcp=is_vcp,
        pivot=pivot,
        buy_signal=buy_signal,
        buy_zone=(pivot, pivot * 1.05),
        stop_loss=stop_loss,
        volume_dry_up=True,
        last_close=pivot * 1.01 if buy_signal else pivot * 0.98,
        last_volume=last_volume,
        avg_volume_50=avg_volume_50,
    )


def make_meaning(*, meaning_score=70, sentiment="tích cực", verification_note="") -> MeaningAssessment:
    return MeaningAssessment(
        symbol="TEST", summary="tóm tắt test", sentiment=sentiment,
        meaning_score=meaning_score, ai_powered=False,
        verification_note=verification_note,
    )


class TestDecide(unittest.TestCase):
    def test_mua_khi_dat_4m_va_breakout_co_volume(self):
        four_m = make_four_m(is_wonderful=True)
        vcp = make_vcp(is_vcp=True, buy_signal=True)
        meaning = make_meaning(meaning_score=70)

        action, conviction, reasons = _decide(four_m, vcp, meaning)

        self.assertEqual(action, "MUA")
        self.assertGreaterEqual(conviction, 55)
        self.assertLessEqual(conviction, 95)
        self.assertTrue(any("Breakout" in r for r in reasons))

    def test_cho_pivot_khi_dat_4m_vcp_hop_le_nhung_chua_breakout(self):
        four_m = make_four_m(is_wonderful=True)
        vcp = make_vcp(is_vcp=True, buy_signal=False)
        meaning = make_meaning(meaning_score=70)

        action, conviction, reasons = _decide(four_m, vcp, meaning)

        self.assertEqual(action, "CHỜ PIVOT")
        self.assertEqual(conviction, 70)
        self.assertTrue(any("Chờ giá vượt" in r for r in reasons))

    def test_tich_luy_dai_han_khi_dat_4m_on_sale_khong_setup_ky_thuat(self):
        four_m = make_four_m(is_wonderful=True, on_sale=True,
                              current_price=14000.0, mos_price=15000.0)
        vcp = make_vcp(is_vcp=False, buy_signal=False,
                        trend=make_trend(passed_count=4, in_stage2=False))
        meaning = make_meaning(meaning_score=70)

        action, conviction, reasons = _decide(four_m, vcp, meaning)

        self.assertEqual(action, "TÍCH LŨY DÀI HẠN")
        self.assertEqual(conviction, 60)
        self.assertTrue(any("Chưa có setup kỹ thuật" in r for r in reasons))

    def test_theo_doi_khi_chi_dat_1_tang_ky_thuat(self):
        # 4M KHÔNG đạt (is_wonderful=False) nhưng VCP hợp lệ -> chỉ 1 tầng
        four_m = make_four_m(is_wonderful=False, moat=40, mgmt=30)
        vcp = make_vcp(is_vcp=True, buy_signal=False)
        meaning = make_meaning(meaning_score=70)

        action, conviction, reasons = _decide(four_m, vcp, meaning)

        self.assertEqual(action, "THEO DÕI")
        self.assertEqual(conviction, 40)

    def test_theo_doi_khi_chi_dat_1_tang_co_ban(self):
        # 4M đạt nhưng meaning_score < 40 -> fundamental_ok False; VCP cũng
        # không đạt, nhưng four_m.is_wonderful True vẫn tính là "đạt 1 tầng"
        # theo điều kiện `fundamental_ok or technical_setup or in_stage2`
        four_m = make_four_m(is_wonderful=True, on_sale=False)
        vcp = make_vcp(is_vcp=False, buy_signal=False,
                        trend=make_trend(passed_count=7, in_stage2=True))
        meaning = make_meaning(meaning_score=20)  # kéo fundamental_ok xuống False

        action, conviction, reasons = _decide(four_m, vcp, meaning)

        self.assertEqual(action, "THEO DÕI")

    def test_dung_ngoai_khi_khong_dat_ca_hai_tang(self):
        four_m = make_four_m(is_wonderful=False, moat=20, mgmt=25, on_sale=False)
        vcp = make_vcp(is_vcp=False, buy_signal=False,
                        trend=make_trend(passed_count=2, in_stage2=False))
        meaning = make_meaning(meaning_score=50)

        action, conviction, reasons = _decide(four_m, vcp, meaning)

        self.assertEqual(action, "ĐỨNG NGOÀI")
        self.assertEqual(conviction, 15)
        self.assertTrue(any("Không đạt 4M" in r for r in reasons))

    def test_ghi_chu_do_tin_cay_du_lieu_thap_xuat_hien_trong_reasons(self):
        four_m = make_four_m(is_wonderful=True, data_reliability=55,
                              data_warnings=["KBS chỉ có 4 năm BCTC"])
        vcp = make_vcp(is_vcp=True, buy_signal=True)
        meaning = make_meaning()

        _, _, reasons = _decide(four_m, vcp, meaning)

        self.assertTrue(any("Độ tin cậy dữ liệu" in r and "55/100" in r for r in reasons))

    def test_conviction_khong_bao_gio_vuot_95(self):
        four_m = make_four_m(is_wonderful=True, moat=100, mgmt=100)
        vcp = make_vcp(is_vcp=True, buy_signal=True)
        vcp = VCPResult(**{**vcp.__dict__, "trend": make_trend(passed_count=8)})
        meaning = make_meaning(meaning_score=100)

        _, conviction, _ = _decide(four_m, vcp, meaning)

        self.assertLessEqual(conviction, 95)


if __name__ == "__main__":
    unittest.main()
