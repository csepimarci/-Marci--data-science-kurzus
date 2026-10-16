import tempfile
import unittest
from datetime import date
from pathlib import Path

from hungary_inflation_visualization import load_observations, render_svg


class HungaryInflationVisualizationTests(unittest.TestCase):
    def test_loads_monthly_rates_as_percentage_changes(self):
        observations = load_observations()
        self.assertEqual(len(observations), 7)
        self.assertEqual(observations[0]["period_start"], date(1946, 1, 1))
        self.assertEqual(observations[0]["period_end"], date(1946, 2, 1))
        self.assertAlmostEqual(observations[0]["inflation_percent"], 70)
        self.assertEqual(observations[-1]["period_end"], date(1946, 7, 31))
        self.assertAlmostEqual(
            observations[-1]["inflation_percent"] / 1e12,
            26.666666666566,
            places=9,
        )

    def test_rejects_noncontiguous_periods(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "inflation.csv"
            path.write_text(
                "period_start,period_end,index_value_start,index_value_end,source\n"
                "1946-01-01,1946-02-01,1,1.7,test\n"
                "1946-03-01,1946-04-01,10,44,test\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "contiguous"):
                load_observations(path)

    def test_chart_shows_monthly_rates_and_billion_pengo_period(self):
        svg = render_svg(load_observations())
        self.assertIn("Hungary’s hyperinflation, month by month", svg)
        self.assertIn("Monthly inflation implied by published index changes", svg)
        self.assertIn("BILLION-PENGŐ NOTES", svg)
        self.assertIn("from 13 May", svg)
        self.assertIn("26.7 trillion% in 30 days", svg)
        self.assertIn("historical pengő valuation index", svg)
        self.assertIn("No monthly observations", svg)
        self.assertIn("August 1945", svg)
        self.assertNotIn("Adópengő index", svg)
        self.assertEqual(svg.count("<circle "), 7)
        self.assertEqual(svg.count("<path "), 1)


if __name__ == "__main__":
    unittest.main()
