"""Chart Hungary's prewar price level and long-run forint-era consumer prices."""

import csv
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
PRICE_LEVEL_DATA_PATH = ROOT / "data" / "hungary_price_level_1938_base.csv"
FORINT_CPI_DATA_PATH = ROOT / "data" / "hungary_forint_cpi.csv"
CHART_PATH = ROOT / "hungary_hyperinflation.svg"


def load_csv(path, expected_fields):
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != expected_fields:
            raise ValueError(f"Expected CSV columns: {','.join(expected_fields)}.")
        rows = list(reader)
    for row_number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(
                f"CSV row {row_number} has an unexpected number of fields."
            )
    return rows


def load_historical_price_level(path=PRICE_LEVEL_DATA_PATH):
    rows = load_csv(path, ["date", "price_level_multiple", "source"])
    observations = []
    for row in rows:
        observation_date = date.fromisoformat(row["date"])
        try:
            multiple = float(row["price_level_multiple"])
        except ValueError as exc:
            raise ValueError(
                f"Invalid historical price-level multiple on {observation_date}."
            ) from exc
        if not math.isfinite(multiple) or multiple <= 0:
            raise ValueError(
                f"Price-level multiple must be positive and finite on {observation_date}."
            )
        observations.append(
            {
                "date": observation_date,
                "price_level_multiple": multiple,
                "source": row["source"],
            }
        )
    if not observations:
        raise ValueError("The historical price-level dataset is empty.")
    if observations != sorted(observations, key=lambda row: row["date"]):
        raise ValueError("Historical price-level observations must be in date order.")
    if len({row["date"] for row in observations}) != len(observations):
        raise ValueError("Historical price-level dates must be unique.")
    return observations


def load_forint_cpi(path=FORINT_CPI_DATA_PATH):
    rows = load_csv(path, ["year", "cpi_2010_100", "source"])
    observations = []
    for row in rows:
        try:
            year = int(row["year"])
            index = float(row["cpi_2010_100"])
        except ValueError as exc:
            raise ValueError("Invalid year or CPI value in forint CPI data.") from exc
        if year < 1946:
            raise ValueError(f"Forint-era CPI year must be 1946 or later, got {year}.")
        if not math.isfinite(index) or index <= 0:
            raise ValueError(f"CPI index must be positive and finite for {year}.")
        observations.append({"year": year, "cpi_2010_100": index, "source": row["source"]})
    if not observations:
        raise ValueError("The forint-era CPI dataset is empty.")
    if observations != sorted(observations, key=lambda row: row["year"]):
        raise ValueError("Forint CPI observations must be in year order.")
    if len({row["year"] for row in observations}) != len(observations):
        raise ValueError("Forint CPI years must be unique.")
    for previous, current in zip(observations, observations[1:]):
        if current["year"] != previous["year"] + 1:
            raise ValueError("Forint CPI years must be consecutive.")
    baseline = next(
        (row for row in observations if row["year"] == 2010),
        None,
    )
    if baseline is None or not math.isclose(
        baseline["cpi_2010_100"], 100, rel_tol=0, abs_tol=1e-9
    ):
        raise ValueError("Forint CPI data must include the 2010 = 100 base year.")
    return observations


def render_svg(historical_rows, cpi_rows):
    if not historical_rows or not cpi_rows:
        raise ValueError("Historical price-level and forint CPI data are required.")

    width, height = 1280, 820
    left_bounds = (88, 600)
    right_bounds = (680, 1200)
    panel_top, panel_bottom = 280, 610
    historical_start, historical_end = date(1938, 1, 1), date(1946, 8, 1)
    historical_first_day = historical_start.toordinal()
    historical_last_day = historical_end.toordinal()
    historical_max = math.ceil(
        math.log10(max(row["price_level_multiple"] for row in historical_rows))
    )

    def history_x(observation_date):
        left, right = left_bounds
        return left + (
            (observation_date.toordinal() - historical_first_day)
            / (historical_last_day - historical_first_day)
            * (right - left)
        )

    def history_y(multiple):
        return panel_bottom - (
            math.log10(multiple) / historical_max * (panel_bottom - panel_top)
        )

    cpi_min, cpi_max = (
        cpi_rows[0]["cpi_2010_100"],
        cpi_rows[-1]["cpi_2010_100"],
    )
    cpi_min_exp = math.floor(math.log10(cpi_min))
    cpi_max_exp = math.ceil(math.log10(cpi_max))

    def cpi_x(year):
        left, right = right_bounds
        first_year, last_year = cpi_rows[0]["year"], cpi_rows[-1]["year"]
        return left + (year - first_year) / (last_year - first_year) * (right - left)

    def cpi_y(index):
        return panel_bottom - (
            (math.log10(index) - cpi_min_exp)
            / (cpi_max_exp - cpi_min_exp)
            * (panel_bottom - panel_top)
        )

    historical_points = [
        (history_x(row["date"]), history_y(row["price_level_multiple"]), row)
        for row in historical_rows
    ]
    cpi_points = [
        (cpi_x(row["year"]), cpi_y(row["cpi_2010_100"]), row)
        for row in cpi_rows
    ]
    cpi_path = " ".join(
        ("M" if index == 0 else "L") + f" {x:.2f} {y:.2f}"
        for index, (x, y, _) in enumerate(cpi_points)
    )
    hyper_start_x = history_x(date(1945, 8, 1))
    hyper_end_x = history_x(date(1946, 8, 1))
    last_cpi_x, last_cpi_y, last_cpi = cpi_points[-1]

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title description" viewBox="0 0 {width} {height}">',
        '<title id="title">Hungary’s prices before, during, and after hyperinflation</title>',
        (
            '<desc id="description">Two separate logarithmic charts. The left '
            "shows historical price-level multiples relative to 1938 from 1938 "
            "through July 1946, including the hyperinflation. The right shows "
            f"Hungary's annual consumer price index in the forint era, "
            f"{cpi_rows[0]['year']}–{cpi_rows[-1]['year']}, with 2010 equal to 100. "
            "The series use different bases and are not connected."
            "</desc>"
        ),
        '<rect width="100%" height="100%" fill="#172b4d"/>',
        '<text x="78" y="57" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="29" font-weight="700">Hungary’s prices before and after the crisis</text>',
        '<text x="80" y="88" fill="#c3cfdd" font-family="Arial, sans-serif" '
        'font-size="15">Prewar benchmark · 1945–46 catastrophe · prices in the forint era</text>',
        '<rect x="78" y="111" width="1120" height="81" rx="4" fill="#20395f"/>',
        '<text x="98" y="141" fill="#ff8a75" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">THE BREAK</text>',
        '<text x="98" y="168" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="15">At the July peak, prices doubled about every 15 hours. The forint replaced the pengő on 1 August 1946.</text>',
        f'<rect x="{left_bounds[0]}" y="{panel_top}" '
        f'width="{left_bounds[1] - left_bounds[0]}" height="{panel_bottom - panel_top}" '
        'fill="#20395f" stroke="#395174" stroke-width="1"/>',
        f'<rect x="{hyper_start_x:.2f}" y="{panel_top}" '
        f'width="{hyper_end_x - hyper_start_x:.2f}" height="{panel_bottom - panel_top}" '
        'fill="#6b343e" opacity="0.55"/>',
        f'<rect x="{right_bounds[0]}" y="{panel_top}" '
        f'width="{right_bounds[1] - right_bounds[0]}" height="{panel_bottom - panel_top}" '
        'fill="#20395f" stroke="#395174" stroke-width="1"/>',
        '<text x="88" y="231" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="17" font-weight="700">Historical price level</text>',
        '<text x="88" y="252" fill="#c3cfdd" font-family="Arial, sans-serif" '
        'font-size="12">1938 = 1 · selected published dates</text>',
        '<text x="680" y="231" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="17" font-weight="700">Forint-era consumer prices</text>',
        f'<text x="680" y="252" fill="#c3cfdd" font-family="Arial, sans-serif" '
        'font-size="12">CPI index · 2010 = 100 · annual, '
        f'{cpi_rows[0]["year"]}–{cpi_rows[-1]["year"]}</text>',
    ]

    for exponent in range(0, historical_max + 1, 5):
        y = history_y(10**exponent)
        elements.extend(
            [
                f'<line x1="{left_bounds[0]}" y1="{y:.2f}" '
                f'x2="{left_bounds[1]}" y2="{y:.2f}" stroke="#395174"/>',
                f'<text x="{left_bounds[0] - 8}" y="{y + 4:.2f}" text-anchor="end" '
                'fill="#c3cfdd" font-family="Arial, sans-serif" font-size="10">'
                f"10^{exponent}×</text>",
            ]
        )

    cpi_ticks = sorted(
        {
            value
            for exponent in range(cpi_min_exp, cpi_max_exp + 1)
            for value in (1 * 10**exponent, 2 * 10**exponent, 5 * 10**exponent)
            if cpi_min <= value <= cpi_max
        }
    )
    for tick in cpi_ticks:
        y = cpi_y(tick)
        elements.extend(
            [
                f'<line x1="{right_bounds[0]}" y1="{y:.2f}" '
                f'x2="{right_bounds[1]}" y2="{y:.2f}" stroke="#395174"/>',
                f'<text x="{right_bounds[0] - 8}" y="{y + 4:.2f}" '
                'text-anchor="end" fill="#c3cfdd" font-family="Arial, sans-serif" '
                'font-size="10">'
                f"{tick:g}</text>",
            ]
        )

    for year in (1938, 1940, 1942, 1944, 1946):
        x = history_x(date(year, 1, 1))
        elements.append(
            f'<text x="{x:.2f}" y="{panel_bottom + 24}" text-anchor="middle" '
            'fill="#c3cfdd" font-family="Arial, sans-serif" font-size="11">'
            f"{year}</text>"
        )

    for year in (1972, 1980, 1990, 2000, 2010, 2020, cpi_rows[-1]["year"]):
        if year < cpi_rows[0]["year"] or year > cpi_rows[-1]["year"]:
            continue
        x = cpi_x(year)
        elements.append(
            f'<text x="{x:.2f}" y="{panel_bottom + 24}" text-anchor="middle" '
            'fill="#c3cfdd" font-family="Arial, sans-serif" font-size="11">'
            f"{year}</text>"
        )

    historical_labels = {
        date(1938, 1, 1): "1938 base · 1×",
        date(1945, 7, 1): "Jul 1945 · 105×",
        date(1945, 12, 1): "Dec 1945 · 41,478×",
        date(1946, 4, 1): "Apr 1946 · 35.8 million×",
        date(1946, 7, 31): "Jul 1946 · 399,623 quadrillion×",
    }
    for x, y, row in historical_points:
        elements.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.5" fill="#ff8a75" '
            'stroke="#f1f4f8" stroke-width="1.4"/>'
        )
        label = historical_labels.get(row["date"])
        if label is None:
            continue
        if row["date"] == date(1938, 1, 1):
            label_x, anchor, label_y = x + 10, "start", y - 12
        elif row["date"] != date(1946, 7, 31):
            label_x, anchor, label_y = x - 8, "end", y - 10
        else:
            label_x, anchor, label_y = x - 8, "end", y + 19
        elements.append(
            f'<text x="{label_x:.2f}" y="{label_y:.2f}" text-anchor="{anchor}" '
            'fill="#f1f4f8" font-family="Arial, sans-serif" font-size="10" '
            f'font-weight="700">{label}</text>'
        )

    elements.extend(
        [
            f'<path d="{cpi_path}" fill="none" stroke="#75c2a0" stroke-width="2.5" '
            'stroke-linejoin="round" stroke-linecap="round"/>',
        ]
    )
    for x, y, _ in cpi_points:
        elements.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.2" fill="#75c2a0"/>'
        )

    first_cpi_x, first_cpi_y, first_cpi = cpi_points[0]
    baseline_row = next(row for row in cpi_rows if row["year"] == 2010)
    baseline_x, baseline_y = cpi_x(2010), cpi_y(baseline_row["cpi_2010_100"])
    elements.extend(
        [
            f'<text x="{first_cpi_x + 7:.2f}" y="{first_cpi_y - 10:.2f}" '
            'fill="#c8f1df" font-family="Arial, sans-serif" font-size="11" '
            f'font-weight="700">1972 · {first_cpi["cpi_2010_100"]:.1f}</text>',
            f'<text x="{baseline_x:.2f}" y="{baseline_y - 13:.2f}" '
            'text-anchor="middle" fill="#c8f1df" font-family="Arial, sans-serif" '
            'font-size="11" font-weight="700">2010 · 100</text>',
            f'<text x="{last_cpi_x - 7:.2f}" y="{last_cpi_y - 12:.2f}" '
            'text-anchor="end" fill="#c8f1df" font-family="Arial, sans-serif" '
            'font-size="11" font-weight="700">'
            f'{last_cpi["year"]} · {last_cpi["cpi_2010_100"]:.1f}</text>',
            '<text x="88" y="677" fill="#c3cfdd" font-family="Arial, sans-serif" '
            'font-size="12">The panels use different reference bases and are deliberately not connected or directly compared.</text>',
            '<text x="88" y="701" fill="#c3cfdd" font-family="Arial, sans-serif" '
            'font-size="12">The CPI source begins in 1972; the gap after the 1946 forint reform reflects unavailable comparable data in this series.</text>',
            '<text x="88" y="725" fill="#c3cfdd" font-family="Arial, sans-serif" '
            'font-size="12">For documented bread prices in pengő before the reform and forint after it, see the companion bread-price chart.</text>',
            '<text x="88" y="759" fill="#91a4bc" font-family="Arial, sans-serif" '
            'font-size="11">Sources: Pénzportál historical price-level table · World Bank WDI, Consumer price index (2010 = 100).</text>',
            "</svg>",
        ]
    )
    return "\n".join(elements)


def main():
    historical_rows = load_historical_price_level()
    cpi_rows = load_forint_cpi()
    CHART_PATH.write_text(render_svg(historical_rows, cpi_rows), encoding="utf-8")
    print(f"Loaded {len(historical_rows)} historical price-level observations.")
    print(
        f"Loaded {len(cpi_rows)} annual forint-era CPI observations "
        f"({cpi_rows[0]['year']}–{cpi_rows[-1]['year']})."
    )
    print(f"Saved chart to {CHART_PATH}.")


if __name__ == "__main__":
    main()
