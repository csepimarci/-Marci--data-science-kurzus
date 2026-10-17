import unittest
from datetime import date

from gas_price_visualization import (
    load_rows,
    percent_change,
    render_svg,
    summarize,
)


class GasPriceVisualizationTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {
                "date": date(2021, month, 1),
                "price_usd_per_mmbtu": float(price),
            }
            for month, price in enumerate(
                (5, 7, 9, 11, 13, 15, 17, 19, 21, 23, 25, 27),
                start=1,
            )
        ]
        self.rows.extend(
            [
                {
                    "date": date(2022, 1, 1),
                    "price_usd_per_mmbtu": 30,
                },
                {
                    "date": date(2022, 2, 1),
                    "price_usd_per_mmbtu": 35,
                },
                {
                    "date": date(2022, 3, 1),
                    "price_usd_per_mmbtu": 45,
                },
                {
                    "date": date(2022, 8, 1),
                    "price_usd_per_mmbtu": 70,
                },
            ]
        )

    def test_percent_change(self):
        self.assertAlmostEqual(percent_change(20, 30), 50)

    def test_summary_uses_2021_average_and_post_invasion_peak(self):
        summary = summarize(self.rows)
        self.assertEqual(summary["baseline_average"], 16)
        self.assertEqual(summary["peak_date"], date(2022, 8, 1))
        self.assertEqual(summary["peak_price"], 70)
        self.assertAlmostEqual(summary["peak_vs_baseline"], 337.5)
        self.assertAlmostEqual(summary["february_to_march_change"], 28.5714286)

    def test_chart_marks_invasion_and_europe_ttf_benchmark(self):
        svg = render_svg(summarize(load_rows()))
        self.assertIn("Europe’s gas shock", svg)
        self.assertIn("24 FEB 2022", svg)
        self.assertIn("2021 average", svg)
        self.assertIn("Aug 2022 PEAK", svg)
        self.assertIn("Natural Gas, Europe (Netherlands TTF", svg)
        self.assertIn("not proof", svg)
        self.assertIn('fill="#47c9d0"', svg)

    def test_snapshot_has_expected_period_and_invasion_era_peak(self):
        rows = load_rows()
        summary = summarize(rows)
        self.assertEqual(summary["first_date"], date(2017, 1, 1))
        self.assertEqual(summary["latest_date"], date(2024, 12, 1))
        self.assertEqual(summary["peak_date"], date(2022, 8, 1))
        self.assertAlmostEqual(summary["peak_price"], 70.0436398, places=6)
        self.assertAlmostEqual(
            summary["baseline_average"], 16.11587795, places=6
        )
        self.assertAlmostEqual(
            summary["february_to_march_change"], 55.6864, places=3
        )


if __name__ == "__main__":
    unittest.main()
