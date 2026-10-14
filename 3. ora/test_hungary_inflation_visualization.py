import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path

from hungary_inflation_visualization import (
    DATA_PATH,
    load_observations,
    render_svg,
)


class HungaryInflationVisualizationTests(unittest.TestCase):
    def test_source_csv_has_eight_published_observations(self):
        observations = load_observations()
        self.assertEqual(len(observations), 8)
        self.assertEqual(observations[0]["date"], date(1946, 1, 1))
        self.assertEqual(observations[-1]["date"], date(1946, 7, 31))
        self.assertEqual(
            [row["index_value"] for row in observations],
            [1, 1.7, 10, 44, 630, 160_000, 7_500_000_000, 2e21],
        )

    def test_chart_uses_logarithmic_scale_and_separates_measures(self):
        svg = render_svg(load_observations())
        self.assertIn("logarithmic scale", svg)
        self.assertIn("10^21", svg)
        self.assertIn("4.19 × 10¹⁶%", svg)
        self.assertIn("two measures are not the same series", svg)
        self.assertEqual(svg.count("<circle "), 8)
        self.assertNotIn("<polyline", svg)

    def test_loader_rejects_nonpositive_index_values(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "invalid.csv"
            with path.open("w", newline="", encoding="utf-8") as output:
                writer = csv.writer(output)
                writer.writerow(("date", "index_value"))
                writer.writerow(("1946-01-01", "1"))
                writer.writerow(("1946-02-01", "0"))
            with self.assertRaisesRegex(ValueError, "positive and finite"):
                load_observations(path)

    def test_chart_requires_positive_finite_values(self):
        observations = load_observations(DATA_PATH)
        observations[-1]["index_value"] = 0
        with self.assertRaisesRegex(ValueError, "must be positive and finite"):
            render_svg(observations)


if __name__ == "__main__":
    unittest.main()
