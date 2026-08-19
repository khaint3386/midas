"""Unit test cho tầng kiểm chứng dữ liệu (app/services/data_quality.py).

Chạy: python -m unittest discover -s tests -v   (từ thư mục midas/)
Không cần mạng, không cần vnstock — chỉ test logic thuần.
"""

from __future__ import annotations

import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services.data_quality import (
    MIN_QUALITY_FOR_AUTO,
    cross_check_eps,
    sanity_check,
    score_quality,
)


class TestSanityCheck(unittest.TestCase):
    def _series_map(self, **overrides):
        base = {
            "revenue": [100.0, 110.0, 120.0],
            "eps": [1000.0, 1100.0, 1200.0],
            "bvps": [5000.0, 5200.0, 5400.0],
            "fcf": [50.0, 55.0, 60.0],
            "roic": [12.0, 13.0, 14.0],
            "roe": [16.0, 17.0, 18.0],
        }
        base.update(overrides)
        return base

    def test_du_lieu_day_du_khong_canh_bao_thieu(self):
        missing, warnings = sanity_check(
            years=[2022, 2023, 2024, 2025, 2026, 2027, 2028, 2029],
            series_map=self._series_map(),
            eps_now=1200.0,
            current_price=18000.0,
        )
        self.assertEqual(missing, [])
        # đủ 8 năm, PE hàm ý = 18000/1200 = 15 -> hợp lệ, không cảnh báo gì
        self.assertEqual(warnings, [])

    def test_thieu_chuoi_duoc_phat_hien(self):
        missing, _ = sanity_check(
            years=[2024, 2025],
            series_map=self._series_map(eps=[], fcf=[float("nan")]),
            eps_now=0.0,
            current_price=0.0,
        )
        self.assertIn("eps", missing)
        self.assertIn("fcf", missing)
        self.assertNotIn("revenue", missing)

    def test_it_hon_5_nam_bi_canh_bao(self):
        _, warnings = sanity_check(
            years=[2024, 2025, 2026],
            series_map=self._series_map(),
            eps_now=1200.0,
            current_price=18000.0,
        )
        self.assertTrue(any("Chỉ lấy được 3 năm" in w for w in warnings))

    def test_nam_khong_tang_dan_bi_canh_bao(self):
        _, warnings = sanity_check(
            years=[2025, 2024, 2023],
            series_map=self._series_map(),
            eps_now=1200.0,
            current_price=18000.0,
        )
        self.assertTrue(any("Thứ tự năm không tăng dần" in w for w in warnings))

    def test_pe_ham_y_bat_thuong_nghi_sai_don_vi(self):
        # giá 18 (nghìn đồng, quên nhân 1000) / EPS 1200 -> PE ảo 0.015 -> bất thường
        _, warnings = sanity_check(
            years=[2022, 2023, 2024, 2025, 2026],
            series_map=self._series_map(),
            eps_now=1200.0,
            current_price=18.0,
        )
        self.assertTrue(any("PE hàm ý" in w for w in warnings))

    def test_roic_ngoai_vung_150_bi_canh_bao_map_sai_cot(self):
        _, warnings = sanity_check(
            years=[2022, 2023, 2024, 2025, 2026],
            series_map=self._series_map(roic=[180.0, 190.0]),
            eps_now=1200.0,
            current_price=18000.0,
        )
        self.assertTrue(any("ROIC" in w and "map sai cột" in w for w in warnings))


class TestCrossCheckEps(unittest.TestCase):
    def test_lech_trong_nguong_20pct_pass(self):
        ok, diff = cross_check_eps([1000.0, 1100.0], [1000.0, 1080.0])
        self.assertTrue(ok)
        self.assertAlmostEqual(diff, 1.8, places=1)

    def test_lech_vuot_nguong_40pct_fail(self):
        ok, diff = cross_check_eps([1000.0, 1000.0], [1000.0, 600.0])
        self.assertFalse(ok)
        self.assertAlmostEqual(diff, 40.0, places=1)

    def test_thieu_du_lieu_mot_ben_tra_none(self):
        ok, diff = cross_check_eps([], [1000.0])
        self.assertFalse(ok)
        self.assertIsNone(diff)

    def test_eps_goc_bang_0_tra_none(self):
        ok, diff = cross_check_eps([0.0], [100.0])
        self.assertFalse(ok)
        self.assertIsNone(diff)


class TestScoreQuality(unittest.TestCase):
    def test_du_lieu_hoan_hao_100_diem(self):
        score = score_quality(
            n_years=10, missing=[], warnings=[],
            cross_checked=True, cross_check_ok=True,
        )
        self.assertEqual(score, 100)

    def test_thieu_chuoi_tru_15_moi_chuoi(self):
        score = score_quality(
            n_years=10, missing=["eps", "fcf"], warnings=[],
            cross_checked=True, cross_check_ok=True,
        )
        self.assertEqual(score, 100 - 15 * 2)

    def test_duoi_5_nam_tru_20(self):
        score = score_quality(
            n_years=4, missing=[], warnings=[],
            cross_checked=True, cross_check_ok=True,
        )
        self.assertEqual(score, 80)

    def test_4_nam_kbs_thuc_te_duoi_nguong_tu_dong(self):
        # Trường hợp thật đã gặp: KBS chỉ có 4 năm, chưa đối chiếu chéo -> quality 55/100
        score = score_quality(
            n_years=4, missing=["roic"], warnings=[],
            cross_checked=False, cross_check_ok=None,
        )
        # 100 - 20 (thiếu <5 năm) - 15 (thiếu roic) - 10 (chưa đối chiếu) = 55
        self.assertEqual(score, 55)
        self.assertEqual(score, MIN_QUALITY_FOR_AUTO)  # đúng ngay ngưỡng loại

    def test_lech_lon_giua_2_nguon_tru_25(self):
        score = score_quality(
            n_years=10, missing=[], warnings=[],
            cross_checked=True, cross_check_ok=False,
        )
        self.assertEqual(score, 75)

    def test_diem_khong_am_va_khong_qua_100(self):
        score = score_quality(
            n_years=1, missing=["eps", "fcf", "bvps", "roic", "roe", "revenue"],
            warnings=["nghi sai đơn vị"] * 3,
            cross_checked=False, cross_check_ok=None,
        )
        self.assertGreaterEqual(score, 0)


if __name__ == "__main__":
    unittest.main()
