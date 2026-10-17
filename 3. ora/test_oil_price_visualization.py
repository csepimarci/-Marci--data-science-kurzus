import unittest
from datetime import date

from oil_price_visualization import (
    load_rows,
    percent_change,
    render_svg,
    summarize,
)


class OilPriceVisualizationTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {
                "date": date(2021, month, 1),
                "price_usd_per_barrel": float(price),
            }
            for month, price in enumerate(
                (50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100, 105),
                start=1,
            )
        ]
        self.rows.extend(
            [
                {
                    "date": date(2022, 1, 1),
                    "price_usd_per_barrel": 110,
                },
                {
                    "date": date(2022, 2, 1),
                    "price_usd_per_barrel": 115,
                },
                {
                    "date": date(2022, 3, 1),
                    "price_usd_per_barrel": 130,
                },
            ]
        )

    def test_percent_change(self):
        self.assertAlmostEqual(percent_change(100, 125), 25)

    def test_summary_uses_2021_baseline_and_post_invasion_peak(self):
        summary = summarize(self.rows)
        self.assertEqual(summary["baseline_average"], 77.5)
        self.assertEqual(summary["peak_date"], date(2022, 3, 1))
        self.assertEqual(summary["peak_price"], 130)
        self.assertAlmostEqual(summary["peak_vs_baseline"], 67.7419355)
        self.assertAlmostEqual(summary["jan_to_march_change"], 18.1818182)

    def test_chart_marks_invasion_and_explains_benchmark(self):
        svg = render_svg(summarize(load_rows()))
        self.assertIn("Brent crude oil prices before and after Russia invaded Ukraine", svg)
        self.assertIn("24 FEB 2022", svg)
        self.assertIn("2021 average", svg)
        self.assertIn("Jun 2022 PEAK", svg)
        self.assertIn("not a single-cause estimate", svg)
        self.assertIn('fill="#e7a83e"', svg)

    def test_snapshot_contains_source_period_and_expected_peak(self):
        rows = load_rows()
        summary = summarize(rows)
        self.assertEqual(summary["first_date"], date(2017, 1, 1))
        self.assertEqual(summary["latest_date"], date(2026, 9, 1))
        self.assertEqual(summary["peak_date"], date(2022, 6, 1))
        self.assertAlmostEqual(summary["peak_price"], 122.71)
        self.assertAlmostEqual(summary["baseline_average"], 70.6775)


if __name__ == "__main__":
    unittest.main()
