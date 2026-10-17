import unittest

from global_ev_adoption import (
    load_rows,
    rank_countries,
    render_svg,
    summarize,
)


class GlobalEVAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"country_code": "NOR", "year": 2024, "ev_sales_share_percent": 92},
            {"country_code": "NOR", "year": 2025, "ev_sales_share_percent": 97},
            {"country_code": "CHN", "year": 2024, "ev_sales_share_percent": 48},
            {"country_code": "CHN", "year": 2025, "ev_sales_share_percent": 53},
            {"country_code": "WLD", "year": 2024, "ev_sales_share_percent": 22},
            {"country_code": "WLD", "year": 2025, "ev_sales_share_percent": 25},
        ]

    def test_latest_year_ranking_excludes_world_benchmark(self):
        ranking = rank_countries(self.rows)
        self.assertEqual(
            [(item["country"], item["share"]) for item in ranking],
            [("Norway", 97), ("China", 53)],
        )

    def test_summary_uses_latest_global_observation(self):
        summary = summarize(self.rows)
        self.assertEqual(summary["first_year"], 2024)
        self.assertEqual(summary["latest_year"], 2025)
        self.assertEqual(summary["world_share"], 25)

    def test_chart_explains_share_measure_and_policy_context(self):
        svg = render_svg(self.rows, summarize(self.rows))
        self.assertIn("Where electric cars took hold first", svg)
        self.assertIn("Share of new car sales (%)", svg)
        self.assertIn("World average: 25%", svg)
        self.assertIn("POLICY MILESTONES", svg)
        self.assertIn("Netherlands", svg)
        self.assertIn("not proof of cause", svg)
        self.assertIn("<svg", svg)

    def test_snapshot_ranks_expected_2025_leaders(self):
        rows = load_rows()
        summary = summarize(rows)
        self.assertEqual(summary["latest_year"], 2025)
        self.assertEqual(
            [item["country_code"] for item in summary["ranked_countries"]],
            ["NOR", "DNK", "NPL", "ISL", "SWE", "NLD", "FIN", "CHN"],
        )
        self.assertEqual(summary["world_share"], 25)


if __name__ == "__main__":
    unittest.main()
