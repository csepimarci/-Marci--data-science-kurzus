import tempfile
import unittest
from datetime import date
from pathlib import Path

from hungary_inflation_visualization import (
    load_forint_cpi,
    load_historical_price_level,
    render_svg,
)


class HungaryInflationVisualizationTests(unittest.TestCase):
    def test_loads_historical_price_level_checkpoints(self):
        observations = load_historical_price_level()
        self.assertEqual(len(observations), 5)
        self.assertEqual(observations[0]["date"], date(1938, 1, 1))
        self.assertEqual(observations[0]["price_level_multiple"], 1)
        self.assertEqual(observations[-1]["date"], date(1946, 7, 31))
        self.assertEqual(observations[-1]["price_level_multiple"], 3.99623e20)

    def test_loads_long_run_forint_era_cpi(self):
        observations = load_forint_cpi()
        self.assertEqual(len(observations), 54)
        self.assertEqual(observations[0]["year"], 1972)
        self.assertEqual(observations[-1]["year"], 2025)
        self.assertAlmostEqual(observations[-1]["cpi_2010_100"], 191.983788982003)

    def test_rejects_nonconsecutive_forint_cpi_years(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "cpi.csv"
            path.write_text(
                "year,cpi_2010_100,source\n"
                "1972,2.2,test\n"
                "1974,2.4,test\n",
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "consecutive"):
                load_forint_cpi(path)

    def test_chart_separates_historical_and_forint_era_bases(self):
        svg = render_svg(load_historical_price_level(), load_forint_cpi())
        self.assertIn("Hungary’s prices before and after the crisis", svg)
        self.assertIn("Historical price level", svg)
        self.assertIn("Forint-era consumer prices", svg)
        self.assertIn("1946 forint reform", svg)
        self.assertIn("different reference bases", svg)
        self.assertIn("1972–2025", svg)
        self.assertIn("399,623 quadrillion×", svg)
        self.assertIn("doubled about every 15 hours", svg)
        self.assertEqual(svg.count("<path "), 1)
        self.assertEqual(svg.count('fill="#ff8a75" stroke="#f1f4f8"'), 5)
        self.assertEqual(svg.count("<path "), 1)


if __name__ == "__main__":
    unittest.main()
