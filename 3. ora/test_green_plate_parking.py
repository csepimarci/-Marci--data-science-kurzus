import unittest

from green_plate_parking import indexed_series, render_svg, summary_statistics


def make_rows():
    rows = []
    counts = {
        "Hungary": {2015: (100, 50), 2016: (180, 70), 2025: (8000, 2000)},
        "Austria": {2015: (300, 200), 2016: (400, 250), 2025: (6000, 4000)},
        "Czechia": {2015: (100, 50), 2016: (120, 70), 2025: (8000, 2000)},
        "Poland": {2015: (100, 50), 2016: (130, 70), 2025: (8000, 2000)},
        "Romania": {2015: (100, 50), 2016: (140, 70), 2025: (8000, 2000)},
        "Slovakia": {2015: (100, 50), 2016: (150, 70), 2025: (8000, 2000)},
    }
    for country, by_year in counts.items():
        for year, (bev, phev) in by_year.items():
            rows.extend(
                [
                    {
                        "country": country,
                        "year": year,
                        "fuel_type": "BEV",
                        "vehicle_count": bev,
                    },
                    {
                        "country": country,
                        "year": year,
                        "fuel_type": "PHEV",
                        "vehicle_count": phev,
                    },
                    {
                        "country": country,
                        "year": year,
                        "fuel_type": "LPG",
                        "vehicle_count": 10,
                    },
                ]
            )
    return rows


class GreenPlateParkingTests(unittest.TestCase):
    def test_indexed_series_uses_bev_and_phev_baseline(self):
        series = indexed_series(make_rows(), countries=("Hungary",))
        self.assertEqual(series["Hungary"][0], (2015, 100))
        self.assertAlmostEqual(series["Hungary"][1][1], 166.6666667)
        self.assertAlmostEqual(series["Hungary"][-1][1], 6_666.6666667)

    def test_summary_counts_latest_fleet_and_growth(self):
        summary = summary_statistics(make_rows())
        self.assertEqual(summary["baseline_count"], 150)
        self.assertEqual(summary["latest_count"], 10_000)
        self.assertEqual(summary["latest_bev"], 8_000)
        self.assertEqual(summary["latest_phev"], 2_000)
        self.assertAlmostEqual(summary["growth_multiple"], 10_000 / 150)

    def test_chart_discloses_policy_marker_and_causal_limit(self):
        svg = render_svg(make_rows())
        self.assertIn("2016 · Budapest green-plate parking", svg)
        self.assertIn("does not estimate", svg)
        self.assertIn("<polyline", svg)
        self.assertIn("#8be28b", svg)

    def test_index_requires_nonzero_base_year_value(self):
        rows = [
            {"country": "Hungary", "year": 2015, "fuel_type": "BEV", "vehicle_count": 0},
            {"country": "Hungary", "year": 2016, "fuel_type": "BEV", "vehicle_count": 5},
        ]
        with self.assertRaisesRegex(ValueError, "positive BEV\\+PHEV baseline"):
            indexed_series(rows, countries=("Hungary",))


if __name__ == "__main__":
    unittest.main()
