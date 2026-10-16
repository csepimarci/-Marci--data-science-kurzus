"""Visualize sourced bread-price observations and Hungary's 1945–46 inflation."""

import csv
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BREAD_DATA_PATH = ROOT / "data" / "hungary_bread_prices.csv"
PRICE_LEVEL_DATA_PATH = ROOT / "data" / "hungary_price_level_1938_base.csv"
CHART_PATH = ROOT / "hungary_bread_prices.svg"


def load_csv(path, expected_fields):
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != expected_fields:
            raise ValueError(
                f"Expected CSV columns: {','.join(expected_fields)}."
            )
        rows = list(reader)
    for row_number, row in enumerate(rows, start=2):
        if None in row or any(value is None for value in row.values()):
            raise ValueError(f"CSV row {row_number} has an unexpected number of fields.")
    return rows


def load_bread_prices(path=BREAD_DATA_PATH):
    rows = load_csv(path, ["date", "price_per_kg", "currency", "source"])
    observations = []
    for row in rows:
        observation_date = date.fromisoformat(row["date"])
        try:
            price = float(row["price_per_kg"])
        except ValueError as exc:
            raise ValueError(f"Invalid bread price on {observation_date}.") from exc
        if not math.isfinite(price) or price <= 0:
            raise ValueError(
                f"Bread price must be positive and finite on {observation_date}."
            )
        currency = row["currency"]
        if currency not in ("pengo", "forint"):
            raise ValueError(f"Unexpected bread-price currency {currency!r}.")
        observations.append(
            {
                "date": observation_date,
                "price_per_kg": price,
                "currency": currency,
                "source": row["source"],
            }
        )
    if not observations:
        raise ValueError("The bread-price dataset is empty.")
    if observations != sorted(observations, key=lambda row: row["date"]):
        raise ValueError("Bread-price observations must be in date order.")
    if len({row["date"] for row in observations}) != len(observations):
        raise ValueError("Bread-price observation dates must be unique.")
    return observations


def load_price_level(path=PRICE_LEVEL_DATA_PATH):
    rows = load_csv(path, ["date", "price_level_multiple", "source"])
    observations = []
    for row in rows:
        observation_date = date.fromisoformat(row["date"])
        try:
            multiple = float(row["price_level_multiple"])
        except ValueError as exc:
            raise ValueError(
                f"Invalid price-level multiple on {observation_date}."
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
        raise ValueError("The price-level dataset is empty.")
    if observations != sorted(observations, key=lambda row: row["date"]):
        raise ValueError("Price-level observations must be in date order.")
    return observations


def render_svg(bread_rows, price_level_rows):
    if not bread_rows or not price_level_rows:
        raise ValueError("Both bread-price and price-level observations are required.")

    width, height = 1200, 820
    left, right = 140, 1130
    timeline_y = 340
    panel_top, panel_bottom = 485, 720
    start_date, end_date = date(1938, 1, 1), date(1953, 1, 1)
    start_day, end_day = start_date.toordinal(), end_date.toordinal()

    def x_position(observation_date):
        return left + (
            (observation_date.toordinal() - start_day)
            / (end_day - start_day)
            * (right - left)
        )

    max_multiple = max(row["price_level_multiple"] for row in price_level_rows)
    max_exponent = math.ceil(math.log10(max_multiple))

    def y_position(multiple):
        return panel_bottom - math.log10(multiple) / max_exponent * (
            panel_bottom - panel_top
        )

    hyperinflation_start = date(1945, 8, 1)
    hyperinflation_end = date(1946, 8, 1)
    hyper_x_start = x_position(hyperinflation_start)
    hyper_x_end = x_position(hyperinflation_end)

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title description" viewBox="0 0 {width} {height}">',
        '<title id="title">Bread prices and hyperinflation in Hungary, 1938–1952</title>',
        (
            '<desc id="description">A timeline of nine sourced bread-price observations '
            "per kilogram in pengő before the 1946 currency reform and forint after it. "
            "A second panel shows the 1938 reference base and four published general "
            "price-level multiples relative to 1938 on a logarithmic scale. "
            "No bread prices are plotted for the peak "
            "hyperinflation because the source series has no observations then."
            "</desc>"
        ),
        '<rect width="100%" height="100%" fill="#fbf8f1"/>',
        '<text x="72" y="55" fill="#273b32" font-family="Arial, sans-serif" '
        'font-size="30" font-weight="700">What did bread cost in Hungary?</text>',
        '<text x="74" y="85" fill="#5c685f" font-family="Arial, sans-serif" '
        'font-size="15">Observed retail prices before and after the 1945–46 hyperinflation</text>',
        '<rect x="72" y="105" width="1058" height="55" rx="5" fill="#f0e6d4"/>',
        '<text x="91" y="128" fill="#7d4a2f" font-family="Arial, sans-serif" '
        'font-size="14" font-weight="700">HYPERINFLATION PEAK · JULY 1946</text>',
        '<text x="91" y="148" fill="#273b32" font-family="Arial, sans-serif" '
        'font-size="14">Monthly inflation reached 4.19 × 10¹⁶%; prices doubled about every 15 hours (Hanke–Krus).</text>',
        '<text x="74" y="202" fill="#273b32" font-family="Arial, sans-serif" '
        'font-size="19" font-weight="700">Bread price observations · per kilogram</text>',
        '<text x="74" y="224" fill="#5c685f" font-family="Arial, sans-serif" '
        'font-size="13">Timeline only: pengő before the currency change; forint after. Amounts across currencies are not directly comparable.</text>',
        f'<rect x="{hyper_x_start:.2f}" y="245" width="{hyper_x_end - hyper_x_start:.2f}" '
        'height="180" fill="#f8e5dd"/>',
        f'<text x="{(hyper_x_start + hyper_x_end) / 2:.2f}" y="265" '
        'text-anchor="middle" fill="#a44d39" font-family="Arial, sans-serif" '
        'font-size="12" font-weight="700">HYPERINFLATION · NO BREAD-PRICE OBSERVATIONS IN THIS SOURCE</text>',
        f'<line x1="{left}" y1="{timeline_y}" x2="{right}" y2="{timeline_y}" '
        'stroke="#a8ada4" stroke-width="2"/>',
    ]

    for year in (1938, 1940, 1942, 1944, 1946, 1948, 1950, 1952):
        x = x_position(date(year, 1, 1))
        elements.extend(
            [
                f'<line x1="{x:.2f}" y1="{timeline_y - 5}" x2="{x:.2f}" '
                f'y2="{timeline_y + 6}" stroke="#818b82" stroke-width="1"/>',
                f'<text x="{x:.2f}" y="{timeline_y + 24}" text-anchor="middle" '
                'fill="#5c685f" font-family="Arial, sans-serif" font-size="12">'
                f"{year}</text>",
            ]
        )

    prewar = next((row for row in bread_rows if row["currency"] == "pengo"), None)
    if prewar:
        x = x_position(prewar["date"])
        elements.extend(
            [
                f'<circle cx="{x:.2f}" cy="{timeline_y}" r="7" fill="#c77d35" '
                'stroke="#fffdf7" stroke-width="2"/>',
                f'<text x="{x + 10:.2f}" y="{timeline_y - 34}" fill="#7d4a2f" '
                'font-family="Arial, sans-serif" font-size="14" font-weight="700">'
                f'31 Aug 1939 · {prewar["price_per_kg"]:.2f} pengő/kg</text>',
            ]
        )

    post_reform = [row for row in bread_rows if row["currency"] == "forint"]
    for row in post_reform:
        x = x_position(row["date"])
        elements.append(
            f'<circle cx="{x:.2f}" cy="{timeline_y}" r="5.5" fill="#4e8b57" '
            'stroke="#fffdf7" stroke-width="1.5"/>'
        )

    repeated = [
        row for row in post_reform if abs(row["price_per_kg"] - 0.92) < 1e-9
    ]
    if repeated:
        first_x = x_position(repeated[0]["date"])
        last_x = x_position(repeated[-1]["date"])
        elements.extend(
            [
                f'<line x1="{first_x:.2f}" y1="{timeline_y - 10}" '
                f'x2="{last_x:.2f}" y2="{timeline_y - 10}" stroke="#4e8b57" '
                'stroke-width="2"/>',
                f'<text x="{(first_x + last_x) / 2:.2f}" y="{timeline_y - 30}" '
                'text-anchor="middle" fill="#356a3c" '
                'font-family="Arial, sans-serif" font-size="13" font-weight="700">'
                "0.92 Ft/kg on six dates · Aug 1946–Apr 1948</text>",
            ]
        )

    for row in post_reform:
        if row["price_per_kg"] <= 0.92:
            continue
        x = x_position(row["date"])
        is_latest = row is post_reform[-1]
        y_label = timeline_y - 36 if is_latest else timeline_y + 58
        text_anchor = "end" if is_latest else "middle"
        elements.append(
            f'<text x="{x - 8 if is_latest else x:.2f}" y="{y_label}" '
            f'text-anchor="{text_anchor}" fill="#356a3c" '
            'font-family="Arial, sans-serif" font-size="13" font-weight="700">'
            f'{row["date"].strftime("%d %b %Y")} · {row["price_per_kg"]:.2f} Ft/kg</text>'
        )

    elements.extend(
        [
            '<text x="74" y="454" fill="#273b32" font-family="Arial, sans-serif" '
            'font-size="19" font-weight="700">Overall price level · 1938 = 1</text>',
            '<text x="74" y="475" fill="#5c685f" font-family="Arial, sans-serif" '
            'font-size="13">Published historical multiples, not a bread-price series · logarithmic scale</text>',
            f'<rect x="{left}" y="{panel_top}" width="{right - left}" '
            f'height="{panel_bottom - panel_top}" fill="#f3efe6" '
            'stroke="#ded7ca" stroke-width="1"/>',
            f'<rect x="{hyper_x_start:.2f}" y="{panel_top}" '
            f'width="{hyper_x_end - hyper_x_start:.2f}" '
            f'height="{panel_bottom - panel_top}" fill="#f4ddd3" opacity="0.75"/>',
        ]
    )

    for exponent in range(max_exponent + 1):
        multiple = 10**exponent
        y = y_position(multiple)
        elements.extend(
            [
                f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
                'stroke="#d9d2c6" stroke-width="1"/>',
                f'<text x="{left - 12}" y="{y + 4:.2f}" text-anchor="end" '
                'fill="#657067" font-family="Arial, sans-serif" font-size="12">'
                f"10^{exponent}×</text>",
            ]
        )

    for row in price_level_rows:
        x = x_position(row["date"])
        y = y_position(row["price_level_multiple"])
        elements.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6.5" fill="#bf5c43" '
            'stroke="#fffdf7" stroke-width="2"/>'
        )

    label_specs = (
        (0, "1938 base · 1×"),
        (1, "Jul 1945 · 105×"),
        (2, "Dec 1945 · 41,478×"),
        (3, "Apr 1946 · 35.8 million×"),
        (4, "31 Jul 1946 · 399,623 quadrillion×"),
    )
    for index, label in label_specs:
        row = price_level_rows[index]
        x = x_position(row["date"])
        y = y_position(row["price_level_multiple"])
        label_y = max(panel_top + 17, y - 13)
        text_anchor = "start" if x < right - 240 else "end"
        label_x = x + 9 if text_anchor == "start" else x - 9
        elements.append(
            f'<text x="{label_x:.2f}" y="{label_y:.2f}" text-anchor="{text_anchor}" '
            'fill="#843f31" font-family="Arial, sans-serif" font-size="12" '
            f'font-weight="700">{label}</text>'
        )

    for year in (1938, 1940, 1942, 1944, 1946, 1948, 1950, 1952):
        x = x_position(date(year, 1, 1))
        elements.append(
            f'<text x="{x:.2f}" y="{panel_bottom + 21}" text-anchor="middle" '
            'fill="#5c685f" font-family="Arial, sans-serif" font-size="12">'
            f"{year}</text>"
        )

    elements.extend(
        [
            '<text x="74" y="778" fill="#5c685f" font-family="Arial, sans-serif" '
            'font-size="12">Bread observations: contemporary retail-price tables. '
            'Red points: Pénzportál historical price-index multiples.</text>',
            '<text x="74" y="798" fill="#5c685f" font-family="Arial, sans-serif" '
            'font-size="12">No bread prices are estimated or interpolated for the missing hyperinflation period.</text>',
            "</svg>",
        ]
    )
    return "\n".join(elements)


def main():
    bread_rows = load_bread_prices()
    price_level_rows = load_price_level()
    CHART_PATH.write_text(render_svg(bread_rows, price_level_rows), encoding="utf-8")
    print(f"Loaded {len(bread_rows)} observed bread prices.")
    print(f"Loaded {len(price_level_rows)} general price-level observations.")
    print(f"Saved chart to {CHART_PATH}.")


if __name__ == "__main__":
    main()
