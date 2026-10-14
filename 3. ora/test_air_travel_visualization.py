import unittest
from datetime import date

from air_travel_visualization import event_summary, percent_change, render_svg


class AirTravelVisualizationTests(unittest.TestCase):
    def setUp(self):
        self.rows = [
            {
                "date": date(2001, 8, 1),
                "rpm_thousands": 60_000_000,
                "rpm_seasonally_adjusted_thousands": 60_000_000,
            },
            {
                "date": date(2001, 9, 1),
                "rpm_thousands": 40_000_000,
                "rpm_seasonally_adjusted_thousands": 42_000_000,
            },
            {
                "date": date(2020, 2, 1),
                "rpm_thousands": 90_000_000,
                "rpm_seasonally_adjusted_thousands": 90_000_000,
            },
            {
                "date": date(2020, 4, 1),
                "rpm_thousands": 3_000_000,
                "rpm_seasonally_adjusted_thousands": 3_000_000,
            },
        ]

    def test_percent_change(self):
        self.assertAlmostEqual(percent_change(100, 75), -25)

    def test_event_summary_uses_adjusted_series(self):
        summary = event_summary(self.rows)
        self.assertAlmostEqual(summary["sep_2001_change"], -30)
        self.assertAlmostEqual(summary["covid_change"], -96.6666667)
        self.assertAlmostEqual(summary["latest_billions"], 3)

    def test_chart_identifies_measure_and_events(self):
        summary = event_summary(self.rows)
        svg = render_svg(self.rows, summary)
        self.assertIn("U.S. airline passenger travel after 9/11 and COVID-19", svg)
        self.assertIn("SEPTEMBER 2001", svg)
        self.assertIn("COVID-19 · APRIL 2020 LOW", svg)
        self.assertIn('fill="#172b4d"', svg)
        self.assertIn('stroke="#58c4dd"', svg)
        self.assertNotIn("rx=", svg)
        self.assertIn("<svg", svg)


if __name__ == "__main__":
    unittest.main()
