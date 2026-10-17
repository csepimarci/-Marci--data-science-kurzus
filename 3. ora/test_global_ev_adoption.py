import unittest

from global_ev_adoption import (
    case_study_summaries,
    load_rows,
    render_svg,
    summarize,
)


class GlobalEVAdoptionTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"country_code": "DEU", "year": 2015, "ev_sales_share_percent": 0.7},
            {"country_code": "DEU", "year": 2019, "ev_sales_share_percent": 3},
            {"country_code": "DEU", "year": 2020, "ev_sales_share_percent": 14},
            {"country_code": "DEU", "year": 2022, "ev_sales_share_percent": 31},
            {"country_code": "CHN", "year": 2018, "ev_sales_share_percent": 4.7},
            {"country_code": "CHN", "year": 2020, "ev_sales_share_percent": 5.7},
            {"country_code": "CHN", "year": 2022, "ev_sales_share_percent": 29},
            {"country_code": "FRA", "year": 2015, "ev_sales_share_percent": 1.2},
            {"country_code": "FRA", "year": 2019, "ev_sales_share_percent": 2.7},
            {"country_code": "FRA", "year": 2020, "ev_sales_share_percent": 11},
            {"country_code": "FRA", "year": 2022, "ev_sales_share_percent": 20},
        ]

    def test_case_summaries_measure_percentage_point_change(self):
        summaries = case_study_summaries(self.rows)
        self.assertEqual(
            [case["country"] for case in summaries],
            ["Germany", "China", "France"],
        )
        self.assertAlmostEqual(summaries[0]["post_change"], 28)
        self.assertAlmostEqual(summaries[1]["post_change"], 23.3)
        self.assertAlmostEqual(summaries[2]["post_change"], 17.3)

    def test_summary_retains_annual_data_bounds(self):
        summary = summarize(self.rows)
        self.assertEqual(summary["first_year"], 2015)
        self.assertEqual(summary["latest_year"], 2022)
        self.assertEqual(len(summary["case_studies"]), 3)

    def test_chart_highlights_policy_then_rising_trajectory(self):
        svg = render_svg(self.rows, summarize(self.rows))
        self.assertIn("Flat… policy change… then the EV share climbs", svg)
        self.assertIn("Germany", svg)
        self.assertIn("purchase grant doubled", svg)
        self.assertIn("+28.0 pp by 2022", svg)
        self.assertIn("POLICY · 2020", svg)
        self.assertIn("same 0–60% scale", svg)
        self.assertIn("not proof", svg)
        self.assertNotIn("LATEST-YEAR RANKING", svg)

    def test_snapshot_has_all_policy_case_observations(self):
        rows = load_rows()
        summaries = case_study_summaries(rows)
        by_country = {case["country_code"]: case for case in summaries}
        self.assertEqual(by_country["DEU"]["baseline_end_share"], 3)
        self.assertEqual(by_country["DEU"]["post_end_share"], 31)
        self.assertAlmostEqual(by_country["DEU"]["post_change"], 28)
        self.assertEqual(by_country["CHN"]["baseline_end_share"], 5.7)
        self.assertEqual(by_country["CHN"]["post_end_share"], 29)
        self.assertEqual(by_country["FRA"]["baseline_end_share"], 2.7)
        self.assertEqual(by_country["FRA"]["post_end_share"], 20)


if __name__ == "__main__":
    unittest.main()
