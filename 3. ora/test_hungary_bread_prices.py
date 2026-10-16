import unittest
from datetime import date

from hungary_bread_prices import (
    load_bread_prices,
    load_price_level,
    render_svg,
)


class HungaryBreadPriceTests(unittest.TestCase):
    def test_bread_prices_keep_currency_and_observed_dates(self):
        rows = load_bread_prices()
        self.assertEqual(len(rows), 9)
        self.assertEqual(rows[0]["date"], date(1939, 8, 31))
        self.assertEqual(rows[0]["price_per_kg"], 0.38)
        self.assertEqual(rows[0]["currency"], "pengo")
        self.assertEqual(rows[1]["date"], date(1946, 8, 31))
        self.assertEqual(rows[1]["price_per_kg"], 0.92)
        self.assertEqual(rows[1]["currency"], "forint")
        self.assertEqual(rows[1]["source"], "CIA economic statistics report, p. 18")
        self.assertEqual(rows[-1]["price_per_kg"], 2.8)

    def test_price_level_series_keeps_peak_scale(self):
        rows = load_price_level()
        self.assertEqual(len(rows), 5)
        self.assertEqual(rows[0]["date"], date(1938, 1, 1))
        self.assertEqual(rows[0]["price_level_multiple"], 1)
        self.assertEqual(rows[-1]["date"], date(1946, 7, 31))
        self.assertEqual(rows[-1]["price_level_multiple"], 3.99623e20)

    def test_chart_discloses_currency_change_and_missing_bread_data(self):
        svg = render_svg(load_bread_prices(), load_price_level())
        self.assertIn("Amounts across currencies are not directly comparable", svg)
        self.assertIn("NO BREAD-PRICE OBSERVATIONS IN THIS SOURCE", svg)
        self.assertIn("399,623 quadrillion×", svg)
        self.assertEqual(svg.count('fill="#bf5c43"'), 5)

    def test_chart_never_draws_a_fabricated_bread_price_line(self):
        svg = render_svg(load_bread_prices(), load_price_level())
        self.assertNotIn("<polyline", svg)


if __name__ == "__main__":
    unittest.main()
