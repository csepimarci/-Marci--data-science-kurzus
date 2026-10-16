import tempfile
import unittest
from datetime import date
from pathlib import Path

from hungary_inflation_visualization import load_observations, render_svg


class HungaryInflationVisualizationTests(unittest.TestCase):
    def test_loads_eight_source_dates_and_index_values(self):
        observations = load_observations()
        self.assertEqual(len(observations), 8)
        self.assertEqual(observations[0]["date"], date(1946, 1, 1))
        self.assertEqual(observations[0]["index_value"], 1)
        self.assertEqual(observations[-1]["date"], date(1946, 7, 31))
        self.assertEqual(observations[-1]["index_value"], 2e21)

    def test_rejects_unsorted_and_duplicate_dates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "index.csv"
            path.write_text(
                "date,index_value\n1946-02-01,2\n1946-01-01,1\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "date order"):
                load_observations(path)
            path.write_text(
                "date,index_value\n1946-01-01,1\n1946-01-01,2\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "unique"):
                load_observations(path)

    def test_chart_has_one_logarithmic_index_story_and_marks_the_source_gap(self):
        observations = load_observations()
        svg = render_svg(observations)
        self.assertIn("Hungary’s 1946 hyperinflation", svg)
        self.assertIn("Adópengő index", svg)
        self.assertIn("logarithmic scale", svg)
        self.assertIn("4.19 × 10¹⁶%", svg)
        self.assertIn("2 × 10²¹", svg)
        self.assertIn("not daily data", svg)
        self.assertEqual(svg.count("<circle "), 8)
        self.assertEqual(svg.count("<path "), 1)
        self.assertEqual(svg.count('fill="#ff8a75" stroke="#f1f4f8"'), 8)


if __name__ == "__main__":
    unittest.main()
