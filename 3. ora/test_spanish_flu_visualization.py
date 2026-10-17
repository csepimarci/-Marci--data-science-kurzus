import unittest

from spanish_flu_visualization import render_svg, summarize


class SpanishFluVisualizationTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {"year": 1916, "life_expectancy_years": 51.7},
            {"year": 1917, "life_expectancy_years": 50.9},
            {"year": 1918, "life_expectancy_years": 39.1},
            {"year": 1919, "life_expectancy_years": 54.7},
            {"year": 1920, "life_expectancy_years": 54.1},
        ]

    def test_summary_calculates_drop_and_rebound(self):
        summary = summarize(self.rows)
        self.assertAlmostEqual(summary["drop_years"], 11.8)
        self.assertAlmostEqual(summary["drop_percent"], -23.1827112)
        self.assertAlmostEqual(summary["rebound_years"], 15.6)
        self.assertAlmostEqual(summary["recovery_vs_1917"], 3.8)

    def test_summary_requires_all_event_years(self):
        with self.assertRaisesRegex(ValueError, "missing values"):
            summarize(self.rows[:-2])

    def test_chart_highlights_1918_in_dark_red_theme(self):
        summary = summarize(self.rows)
        svg = render_svg(self.rows, summary)
        self.assertIn("The year life expectancy fell 11.8 years", svg)
        self.assertIn("1918 · PANDEMIC YEAR", svg)
        self.assertIn("−11.8 years", svg)
        self.assertIn("+15.6 from 1918", svg)
        self.assertIn('fill="#111114"', svg)
        self.assertIn('stroke="#ff5263"', svg)
        self.assertIn("not the average age of people who died", svg)
        self.assertIn("<svg", svg)


if __name__ == "__main__":
    unittest.main()
