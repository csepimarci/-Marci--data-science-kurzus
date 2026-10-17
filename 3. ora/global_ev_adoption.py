"""Render an IEA-based comparison of national electric-car adoption."""

import csv
import html
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "iea_ev_sales_share_2026.csv"
CHART_PATH = ROOT / "global_ev_adoption.svg"
COUNTRY_NAMES = {
    "CHN": "China",
    "DNK": "Denmark",
    "FIN": "Finland",
    "ISL": "Iceland",
    "NLD": "Netherlands",
    "NPL": "Nepal",
    "NOR": "Norway",
    "SWE": "Sweden",
    "WLD": "World",
}
COUNTRY_COLORS = {
    "NOR": "#58c4dd",
    "DNK": "#ff8a75",
    "NPL": "#f7c66a",
    "ISL": "#b39ddb",
    "SWE": "#9ad29a",
    "NLD": "#f48fb1",
    "FIN": "#f5a65b",
    "CHN": "#9ecbff",
    "WLD": "#c3cfdd",
}
POLICY_EVENTS = (
    {
        "year": "2020-24",
        "country": "Netherlands",
        "code": "NLD",
        "lines": (
            "SEPP purchase grants supported private",
            "new and used EV purchases.",
        ),
    },
    {
        "year": "2018",
        "country": "Sweden",
        "code": "SWE",
        "lines": (
            "Bonus-malus system introduced a bonus",
            "for eligible low-emission cars.",
        ),
    },
    {
        "year": "2022",
        "country": "Sweden",
        "code": "SWE",
        "lines": (
            "Climate bonus ended from 8 November;",
            "the incentive was withdrawn.",
        ),
    },
    {
        "year": "2022",
        "country": "China",
        "code": "CHN",
        "lines": (
            "National purchase-subsidy payments",
            "ended after the 2022 transition.",
        ),
    },
    {
        "year": "2023",
        "country": "China",
        "code": "CHN",
        "lines": (
            "Purchase-tax exemption extended",
            "through 2027 for new-energy vehicles.",
        ),
    },
    {
        "year": "2023",
        "country": "Norway",
        "code": "NOR",
        "lines": (
            "VAT relief narrowed: the exemption",
            "was capped at the first NOK 500,000.",
        ),
    },
)


def load_rows(path=DATA_PATH):
    rows = []
    seen = set()
    with Path(path).open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(
            line for line in source if not line.startswith("#")
        )
        expected_fields = (
            "country_code",
            "year",
            "ev_sales_share_percent",
        )
        if tuple(reader.fieldnames or ()) != expected_fields:
            raise ValueError(
                f"Expected CSV columns {', '.join(expected_fields)}."
            )
        for line_number, row in enumerate(reader, start=2):
            country_code = row["country_code"].strip()
            year = int(row["year"])
            share = float(row["ev_sales_share_percent"])
            key = (country_code, year)
            if not country_code:
                raise ValueError(f"Missing country code on CSV line {line_number}.")
            if key in seen:
                raise ValueError(
                    f"Duplicate observation for {country_code} in {year}."
                )
            if not math.isfinite(share) or not 0 <= share <= 100:
                raise ValueError(
                    f"Invalid EV sales share for {country_code} in {year}."
                )
            seen.add(key)
            rows.append(
                {
                    "country_code": country_code,
                    "year": year,
                    "ev_sales_share_percent": share,
                }
            )
    if not rows:
        raise ValueError("The IEA EV sales-share dataset contains no observations.")
    return sorted(rows, key=lambda row: (row["country_code"], row["year"]))


def country_name(country_code):
    return COUNTRY_NAMES.get(country_code, country_code)


def rank_countries(rows, limit=8):
    latest_year = max(row["year"] for row in rows)
    latest_rows = [
        row
        for row in rows
        if row["year"] == latest_year and row["country_code"] != "WLD"
    ]
    ranked = sorted(
        latest_rows,
        key=lambda row: (
            -row["ev_sales_share_percent"],
            country_name(row["country_code"]),
        ),
    )
    return [
        {
            "country_code": row["country_code"],
            "country": country_name(row["country_code"]),
            "share": row["ev_sales_share_percent"],
        }
        for row in ranked[:limit]
    ]


def summarize(rows):
    latest_year = max(row["year"] for row in rows)
    world_rows = [
        row
        for row in rows
        if row["country_code"] == "WLD" and row["year"] == latest_year
    ]
    if len(world_rows) > 1:
        raise ValueError(f"Multiple World observations for {latest_year}.")
    return {
        "first_year": min(row["year"] for row in rows),
        "latest_year": latest_year,
        "ranked_countries": rank_countries(rows),
        "world_share": (
            world_rows[0]["ev_sales_share_percent"] if world_rows else None
        ),
    }


def x_position(year, first_year, last_year, left, right):
    return left + (year - first_year) / (last_year - first_year) * (
        right - left
    )


def y_position(share, top, bottom):
    return bottom - share / 100 * (bottom - top)


def render_svg(rows, summary):
    width, height = 1420, 1040
    left, right, top, bottom = 92, 1010, 192, 550
    first_year = summary["first_year"]
    last_year = summary["latest_year"]
    ranking = summary["ranked_countries"]
    selected_codes = {item["country_code"] for item in ranking}

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title description" viewBox="0 0 {width} {height}">',
        '<title id="title">Electric-car adoption leaders and selected subsidy milestones</title>',
        (
            '<desc id="description">Annual electric-vehicle shares of new '
            f'passenger-car sales from {first_year} to {last_year}. The lines '
            "compare the eight highest-share countries in the latest year with "
            "the world average. A lower panel lists selected subsidy and "
            "purchase-tax policy milestones; it does not establish causation."
            "</desc>"
        ),
        '<rect width="100%" height="100%" fill="#172b4d"/>',
        '<text x="78" y="55" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="30" font-weight="700">Where electric cars took hold first</text>',
        '<text x="80" y="87" fill="#c3cfdd" font-family="Arial, sans-serif" '
        'font-size="15">IEA EV sales share for new passenger cars · '
        f'{first_year}-{last_year} · EV includes battery-electric and plug-in hybrid</text>',
        '<rect x="72" y="118" width="1276" height="1" fill="#395174"/>',
        '<text x="80" y="153" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="15" font-weight="700">COUNTRY TRAJECTORIES</text>',
        f'<rect x="{left}" y="{top}" width="{right-left}" height="{bottom-top}" '
        'fill="#20395f" stroke="#395174" stroke-width="1"/>',
    ]

    for share in range(0, 101, 20):
        y = y_position(share, top, bottom)
        elements.extend(
            [
                f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
                'stroke="#395174" stroke-width="1"/>',
                f'<text x="{left-13}" y="{y+5:.2f}" text-anchor="end" '
                'fill="#c3cfdd" font-family="Arial, sans-serif" '
                f'font-size="13">{share}</text>',
            ]
        )

    ticks = sorted(
        {
            first_year,
            last_year,
            *range(((first_year + 2) // 3) * 3, last_year, 3),
        }
    )
    for year in ticks:
        x = x_position(year, first_year, last_year, left, right)
        elements.extend(
            [
                f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" '
                'stroke="#314a6c" stroke-width="1"/>',
                f'<text x="{x:.2f}" y="{bottom+25}" text-anchor="middle" '
                'fill="#c3cfdd" font-family="Arial, sans-serif" '
                f'font-size="13">{year}</text>',
            ]
        )

    elements.extend(
        [
            '<text x="27" y="371" transform="rotate(-90 27 371)" '
            'text-anchor="middle" fill="#f1f4f8" '
            'font-family="Arial, sans-serif" font-size="13">'
            "Share of new car sales (%)</text>",
            '<text x="1044" y="178" fill="#c3cfdd" '
            'font-family="Arial, sans-serif" font-size="12" '
            'font-weight="700">LATEST-YEAR RANKING</text>',
        ]
    )

    series_codes = sorted(selected_codes)
    if any(row["country_code"] == "WLD" for row in rows):
        series_codes.append("WLD")
    for country_code in series_codes:
        series = sorted(
            (
                row
                for row in rows
                if row["country_code"] == country_code
            ),
            key=lambda row: row["year"],
        )
        segments = []
        segment = []
        previous_year = None
        for row in series:
            if previous_year is not None and row["year"] > previous_year + 1:
                if segment:
                    segments.append(segment)
                segment = []
            segment.append(row)
            previous_year = row["year"]
        if segment:
            segments.append(segment)
        color = COUNTRY_COLORS.get(country_code, "#c3cfdd")
        dash = ' stroke-dasharray="5 5"' if country_code == "WLD" else ""
        stroke_width = "2.2" if country_code == "WLD" else "3"
        for points in segments:
            path = " ".join(
                ("M" if index == 0 else "L")
                + " "
                + f'{x_position(row["year"], first_year, last_year, left, right):.2f} '
                + f'{y_position(row["ev_sales_share_percent"], top, bottom):.2f}'
                for index, row in enumerate(points)
            )
            elements.append(
                f'<path d="{path}" fill="none" stroke="{color}" '
                f'stroke-width="{stroke_width}" stroke-linejoin="round" '
                f'stroke-linecap="round"{dash}/>'
            )
        latest = next(
            (row for row in reversed(series) if row["year"] == last_year),
            None,
        )
        if latest is not None:
            elements.append(
                f'<circle cx="{x_position(last_year, first_year, last_year, left, right):.2f}" '
                f'cy="{y_position(latest["ev_sales_share_percent"], top, bottom):.2f}" '
                f'r="4.5" fill="{color}" stroke="#172b4d" stroke-width="1.5"/>'
            )

    for index, item in enumerate(ranking):
        y = 205 + index * 37
        color = COUNTRY_COLORS.get(item["country_code"], "#c3cfdd")
        elements.extend(
            [
                f'<circle cx="1053" cy="{y-5}" r="5" fill="{color}"/>',
                f'<text x="1068" y="{y}" fill="#c3cfdd" '
                'font-family="Arial, sans-serif" font-size="12">'
                f'{index+1:02d}</text>',
                f'<text x="1090" y="{y}" fill="#f1f4f8" '
                'font-family="Arial, sans-serif" font-size="14">'
                f'{html.escape(item["country"])}</text>',
                f'<text x="1328" y="{y}" text-anchor="end" fill="{color}" '
                'font-family="Arial, sans-serif" font-size="14" '
                f'font-weight="700">{item["share"]:.0f}%</text>',
            ]
        )

    if summary["world_share"] is not None:
        elements.extend(
            [
                '<line x1="1045" y1="518" x2="1072" y2="518" '
                'stroke="#c3cfdd" stroke-width="2" stroke-dasharray="5 5"/>',
                '<text x="1082" y="523" fill="#c3cfdd" '
                'font-family="Arial, sans-serif" font-size="13">'
                f'World average: {summary["world_share"]:.0f}%</text>',
            ]
        )
    elements.extend(
        [
            '<text x="80" y="601" fill="#f1f4f8" '
            'font-family="Arial, sans-serif" font-size="16" '
            'font-weight="700">POLICY MILESTONES</text>',
            '<text x="265" y="601" fill="#c3cfdd" '
            'font-family="Arial, sans-serif" font-size="12">'
            "Selected examples only; timing is context, not proof of cause.</text>",
        ]
    )

    card_width, card_height = 390, 108
    card_x_positions = (78, 515, 952)
    for index, event in enumerate(POLICY_EVENTS):
        column = index % 3
        row_number = index // 3
        x = card_x_positions[column]
        y = 624 + row_number * 126
        color = COUNTRY_COLORS[event["code"]]
        elements.extend(
            [
                f'<rect x="{x}" y="{y}" width="{card_width}" '
                f'height="{card_height}" rx="9" fill="#20395f" '
                'stroke="#395174" stroke-width="1"/>',
                f'<rect x="{x}" y="{y}" width="4" height="{card_height}" '
                f'rx="2" fill="{color}"/>',
                f'<text x="{x+18}" y="{y+25}" fill="{color}" '
                'font-family="Arial, sans-serif" font-size="12" '
                'font-weight="700">'
                f'{html.escape(event["year"])} · '
                f'{html.escape(event["country"].upper())}</text>',
                f'<text x="{x+18}" y="{y+52}" fill="#f1f4f8" '
                'font-family="Arial, sans-serif" font-size="13">'
                f'{html.escape(event["lines"][0])}</text>',
                f'<text x="{x+18}" y="{y+74}" fill="#c3cfdd" '
                'font-family="Arial, sans-serif" font-size="13">'
                f'{html.escape(event["lines"][1])}</text>',
            ]
        )

    elements.extend(
        [
            '<text x="80" y="902" fill="#c3cfdd" '
            'font-family="Arial, sans-serif" font-size="12">'
            "Source: IEA Global EV Data Explorer, Global EV Outlook 2026. "
            "Sales share is not the share of the vehicle fleet.</text>",
            '<text x="80" y="924" fill="#c3cfdd" '
            'font-family="Arial, sans-serif" font-size="12">'
            "Policy milestones: IEA Global EV Policy Explorer; Netherlands "
            "SEPP: RVO. Incentives interact with prices, supply and charging access.</text>",
            "</svg>",
        ]
    )
    return "\n".join(elements)


def main():
    rows = load_rows()
    summary = summarize(rows)
    CHART_PATH.write_text(render_svg(rows, summary), encoding="utf-8")
    print(f"Saved chart to {CHART_PATH}.")
    print(
        f'IEA EV sales share, {summary["latest_year"]}: '
        + ", ".join(
            f'{item["country"]} {item["share"]:.0f}%'
            for item in summary["ranked_countries"][:3]
        )
        + "."
    )
    if summary["world_share"] is not None:
        print(f'World average: {summary["world_share"]:.0f}%.')


if __name__ == "__main__":
    main()
