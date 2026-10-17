"""Render Brent crude prices around Russia's 2022 invasion of Ukraine."""

import csv
import html
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "brent_crude_monthly.csv"
CHART_PATH = ROOT / "brent_oil_prices_ukraine_war.svg"
INVASION_DATE = date(2022, 2, 24)
BASELINE_YEAR = 2021
PRICE_SERIES = "MCOILBRENTEU"
SOURCE_URL = (
    "https://fred.stlouisfed.org/graph/fredgraph.csv?"
    "id=MCOILBRENTEU&cosd=2017-01-01&coed=2026-09-30"
)


def load_rows(path=DATA_PATH):
    rows = []
    seen = set()
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ["date", "price_usd_per_barrel"]:
            raise ValueError(
                "Expected CSV columns date and price_usd_per_barrel."
            )
        for line_number, row in enumerate(reader, start=2):
            observation_date = date.fromisoformat(row["date"])
            price = float(row["price_usd_per_barrel"])
            if observation_date.day != 1:
                raise ValueError(
                    f"Expected a monthly observation on line {line_number}."
                )
            if (observation_date.year, observation_date.month) in seen:
                raise ValueError(
                    f"Duplicate month on CSV line {line_number}."
                )
            if not math.isfinite(price) or price < 0:
                raise ValueError(
                    f"Invalid oil price on CSV line {line_number}."
                )
            seen.add((observation_date.year, observation_date.month))
            rows.append(
                {
                    "date": observation_date,
                    "price_usd_per_barrel": price,
                }
            )
    if not rows:
        raise ValueError("The Brent monthly price dataset is empty.")
    return sorted(rows, key=lambda row: row["date"])


def percent_change(start, end):
    if start <= 0:
        raise ValueError("Cannot calculate percentage change from zero.")
    return (end / start - 1) * 100


def summarize(rows):
    baseline_rows = [
        row for row in rows if row["date"].year == BASELINE_YEAR
    ]
    if len(baseline_rows) != 12:
        raise ValueError(
            f"Expected all 12 monthly observations for {BASELINE_YEAR}."
        )
    baseline_average = sum(
        row["price_usd_per_barrel"] for row in baseline_rows
    ) / len(baseline_rows)
    post_invasion_rows = [
        row for row in rows if row["date"] >= date(2022, 3, 1)
    ]
    peak = max(
        post_invasion_rows,
        key=lambda row: row["price_usd_per_barrel"],
    )
    january_2022 = next(
        row["price_usd_per_barrel"]
        for row in rows
        if row["date"] == date(2022, 1, 1)
    )
    march_2022 = next(
        row["price_usd_per_barrel"]
        for row in rows
        if row["date"] == date(2022, 3, 1)
    )
    latest = rows[-1]
    return {
        "first_date": rows[0]["date"],
        "latest_date": latest["date"],
        "latest_price": latest["price_usd_per_barrel"],
        "baseline_average": baseline_average,
        "peak_date": peak["date"],
        "peak_price": peak["price_usd_per_barrel"],
        "peak_vs_baseline": percent_change(
            baseline_average, peak["price_usd_per_barrel"]
        ),
        "jan_2022_price": january_2022,
        "march_2022_price": march_2022,
        "jan_to_march_change": percent_change(january_2022, march_2022),
        "rows": rows,
    }


def month_index(observation_date):
    return observation_date.year * 12 + observation_date.month - 1


def x_position(observation_date, first_date, last_date, left, right):
    first_month = month_index(first_date)
    last_month = month_index(last_date)
    return left + (
        (month_index(observation_date) - first_month)
        / (last_month - first_month)
        * (right - left)
    )


def y_position(price, y_max, top, bottom):
    return bottom - price / y_max * (bottom - top)


def render_svg(summary):
    width, height = 1280, 800
    left, right, top, bottom = 92, 1225, 270, 650
    rows = summary["rows"]
    first_date = summary["first_date"]
    last_date = summary["latest_date"]
    y_max = 140

    points = [
        (
            x_position(row["date"], first_date, last_date, left, right),
            y_position(row["price_usd_per_barrel"], y_max, top, bottom),
            row,
        )
        for row in rows
    ]
    line_path = " ".join(
        ("M" if index == 0 else "L") + f" {x:.2f} {y:.2f}"
        for index, (x, y, _) in enumerate(points)
    )
    area_path = (
        f"M {points[0][0]:.2f} {bottom} "
        + " ".join(f"L {x:.2f} {y:.2f}" for x, y, _ in points)
        + f" L {points[-1][0]:.2f} {bottom} Z"
    )
    invasion_x = x_position(
        date(INVASION_DATE.year, INVASION_DATE.month, 1),
        first_date,
        last_date,
        left,
        right,
    ) + (INVASION_DATE.day - 1) / 28 * (
        (right - left) / (month_index(last_date) - month_index(first_date))
    )
    peak_x = x_position(
        summary["peak_date"], first_date, last_date, left, right
    )
    peak_y = y_position(summary["peak_price"], y_max, top, bottom)

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title description" viewBox="0 0 {width} {height}">',
        '<title id="title">Brent crude oil prices before and after Russia invaded Ukraine</title>',
        (
            '<desc id="description">Monthly average Brent crude oil price '
            f'from {first_date:%B %Y} to {last_date:%B %Y}, in nominal US '
            "dollars per barrel. A vertical marker shows Russia's full-scale "
            "invasion of Ukraine on 24 February 2022. Prices rose from January "
            "to March 2022 and reached a later peak in "
            f'{summary["peak_date"]:%B %Y}. The chart '
            "does not attribute all price changes to the invasion."
            "</desc>"
        ),
        '<defs><linearGradient id="oil-fill" x1="0" x2="0" y1="0" y2="1">'
        '<stop offset="0%" stop-color="#e7a83e" stop-opacity="0.34"/>'
        '<stop offset="100%" stop-color="#e7a83e" stop-opacity="0.01"/>'
        "</linearGradient></defs>",
        '<rect width="100%" height="100%" fill="#191b1a"/>',
        '<text x="74" y="54" fill="#f6f1e7" font-family="Arial, sans-serif" '
        'font-size="29" font-weight="700">Oil prices before and after the '
        'Russian invasion of Ukraine</text>',
        '<text x="76" y="85" fill="#c6c0b4" font-family="Arial, sans-serif" '
        'font-size="15">Brent crude · monthly average · nominal USD per barrel · '
        f'{first_date.year}–{last_date.year}</text>',
        '<rect x="74" y="112" width="1132" height="1" fill="#45433c"/>',
    ]

    cards = (
        (
            "2021 PRE-WAR AVERAGE",
            f'${summary["baseline_average"]:.2f}',
            "#d3b46a",
        ),
        (
            f'POST-INVASION PEAK · {summary["peak_date"]:%b %Y}',
            f'${summary["peak_price"]:.2f}',
            "#e7a83e",
        ),
        (
            "PEAK VS 2021 AVERAGE",
            f'+{summary["peak_vs_baseline"]:.0f}%',
            "#e47a54",
        ),
        (
            f'LATEST · {summary["latest_date"]:%b %Y}',
            f'${summary["latest_price"]:.2f}',
            "#c6c0b4",
        ),
    )
    card_width, card_gap = 264, 16
    for index, (label, value, accent) in enumerate(cards):
        x = 76 + index * (card_width + card_gap)
        elements.extend(
            [
                f'<rect x="{x}" y="132" width="{card_width}" height="76" '
                'rx="8" fill="#252722" stroke="#45433c"/>',
                f'<text x="{x+15}" y="158" fill="#b8b2a7" '
                'font-family="Arial, sans-serif" font-size="10" '
                f'font-weight="700">{html.escape(label)}</text>',
                f'<text x="{x+15}" y="191" fill="{accent}" '
                'font-family="Arial, sans-serif" font-size="25" '
                f'font-weight="700">{html.escape(value)}</text>',
            ]
        )

    elements.append(
        f'<rect x="{left}" y="{top}" width="{right-left}" '
        f'height="{bottom-top}" fill="#20231f" stroke="#45433c"/>'
    )
    for price in range(0, y_max + 1, 20):
        y = y_position(price, y_max, top, bottom)
        elements.extend(
            [
                f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
                'stroke="#393b34" stroke-width="1"/>',
                f'<text x="{left-12}" y="{y+5:.2f}" text-anchor="end" '
                'fill="#b8b2a7" font-family="Arial, sans-serif" '
                f'font-size="12">${price}</text>',
            ]
        )

    first_year = first_date.year
    last_year = last_date.year
    year_ticks = list(range(first_year, last_year + 1, 2))
    if last_year not in year_ticks:
        year_ticks.append(last_year)
    for year in year_ticks:
        x = x_position(
            date(year, 1, 1), first_date, last_date, left, right
        )
        elements.extend(
            [
                f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" '
                'stroke="#30322d" stroke-width="1"/>',
                f'<text x="{x:.2f}" y="{bottom+25}" text-anchor="middle" '
                'fill="#c6c0b4" font-family="Arial, sans-serif" '
                f'font-size="12">{year}</text>',
            ]
        )

    baseline_y = y_position(summary["baseline_average"], y_max, top, bottom)
    elements.extend(
        [
            f'<path d="{area_path}" fill="url(#oil-fill)"/>',
            f'<line x1="{left}" y1="{baseline_y:.2f}" x2="{right}" '
            f'y2="{baseline_y:.2f}" stroke="#d3b46a" stroke-width="1.5" '
            'stroke-dasharray="7 5"/>',
            f'<text x="{left+8}" y="{baseline_y-8:.2f}" fill="#e5ca87" '
            'font-family="Arial, sans-serif" font-size="11">'
            f'2021 average · ${summary["baseline_average"]:.2f}</text>',
            f'<path d="{line_path}" fill="none" stroke="#e7a83e" '
            'stroke-width="2.8" stroke-linejoin="round" stroke-linecap="round"/>',
            f'<line x1="{invasion_x:.2f}" y1="{top}" x2="{invasion_x:.2f}" '
            f'y2="{bottom}" stroke="#e47a54" stroke-width="2" '
            'stroke-dasharray="7 5"/>',
            f'<rect x="{invasion_x+10:.2f}" y="{top+10}" width="247" '
            'height="38" rx="5" fill="#302522" stroke="#7d493b"/>',
            f'<text x="{invasion_x+20:.2f}" y="{top+26}" fill="#f09a72" '
            'font-family="Arial, sans-serif" font-size="10" '
            'font-weight="700">24 FEB 2022</text>',
            f'<text x="{invasion_x+20:.2f}" y="{top+41}" fill="#f6f1e7" '
            'font-family="Arial, sans-serif" font-size="11">'
            "Russia's full-scale invasion of Ukraine</text>",
            f'<circle cx="{peak_x:.2f}" cy="{peak_y:.2f}" r="6" '
            'fill="#e47a54" stroke="#191b1a" stroke-width="2"/>',
            f'<line x1="{peak_x:.2f}" y1="{peak_y-7:.2f}" '
            f'x2="{peak_x+34:.2f}" y2="{peak_y-48:.2f}" '
            'stroke="#e47a54" stroke-width="1.3"/>',
            f'<text x="{peak_x+39:.2f}" y="{peak_y-50:.2f}" '
            'fill="#f09a72" font-family="Arial, sans-serif" font-size="12" '
            'font-weight="700">'
            f'{summary["peak_date"]:%b %Y} PEAK · '
            f'${summary["peak_price"]:.2f}</text>',
        ]
    )

    for target_date, price, color in (
        (date(2022, 1, 1), summary["jan_2022_price"], "#d3b46a"),
        (date(2022, 3, 1), summary["march_2022_price"], "#f09a72"),
    ):
        x = x_position(target_date, first_date, last_date, left, right)
        y = y_position(price, y_max, top, bottom)
        elements.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.5" fill="{color}" '
            'stroke="#191b1a" stroke-width="1.5"/>'
        )

    march_x = x_position(date(2022, 3, 1), first_date, last_date, left, right)
    march_y = y_position(summary["march_2022_price"], y_max, top, bottom)
    elements.extend(
        [
            f'<text x="{march_x+10:.2f}" y="{march_y+20:.2f}" '
            'fill="#f09a72" font-family="Arial, sans-serif" font-size="11">'
            f'Mar 2022 · ${summary["march_2022_price"]:.2f}</text>',
            '<text x="74" y="722" fill="#c6c0b4" '
            'font-family="Arial, sans-serif" font-size="12">'
            "Brent had already climbed before the invasion; March 2022 was "
            f'+{summary["jan_to_march_change"]:.0f}% vs January. '
            "The chart shows timing, not a single-cause estimate.</text>",
            '<text x="74" y="760" fill="#9e998e" '
            'font-family="Arial, sans-serif" font-size="11">'
            "Source: U.S. EIA Brent Europe spot price, monthly average "
            '(via FRED). Nominal dollars; not inflation-adjusted.</text>',
            "</svg>",
        ]
    )
    return "\n".join(elements)


def main():
    rows = load_rows()
    summary = summarize(rows)
    CHART_PATH.write_text(render_svg(summary), encoding="utf-8")
    print(f"Saved chart to {CHART_PATH}.")
    print(
        f'2021 average: ${summary["baseline_average"]:.2f}/barrel; '
        f'peak: ${summary["peak_price"]:.2f} in '
        f'{summary["peak_date"]:%B %Y} '
        f'(+{summary["peak_vs_baseline"]:.1f}% vs 2021 average).'
    )
    print(
        f'Latest observation: {summary["latest_date"]:%B %Y}, '
        f'${summary["latest_price"]:.2f}/barrel.'
    )


if __name__ == "__main__":
    main()
