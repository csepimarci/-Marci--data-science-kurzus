"""Render policy-timed electric-car adoption case studies from IEA data."""

import csv
import html
import math
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "iea_ev_sales_share_2026.csv"
CHART_PATH = ROOT / "global_ev_adoption.svg"
COUNTRY_NAMES = {
    "CHN": "China",
    "DEU": "Germany",
    "FRA": "France",
}
CASE_STUDIES = (
    {
        "country_code": "DEU",
        "policy_year": 2020,
        "baseline_start": 2015,
        "baseline_end": 2019,
        "after_end": 2022,
        "color": "#58c4dd",
        "policy": (
            "2020: purchase grant doubled",
            "under the Innovation Premium.",
        ),
    },
    {
        "country_code": "CHN",
        "policy_year": 2020,
        "baseline_start": 2018,
        "baseline_end": 2020,
        "after_end": 2022,
        "color": "#f7c66a",
        "policy": (
            "2020: purchase subsidies extended",
            "through 2022.",
        ),
    },
    {
        "country_code": "FRA",
        "policy_year": 2020,
        "baseline_start": 2015,
        "baseline_end": 2019,
        "after_end": 2022,
        "color": "#b39ddb",
        "policy": (
            "2020: purchase bonus increased",
            "in the recovery package.",
        ),
    },
)
MUTED_LINE = "#92a3b9"


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


def case_study_summaries(rows):
    lookup = {
        (row["country_code"], row["year"]): row["ev_sales_share_percent"]
        for row in rows
    }
    summaries = []
    for case in CASE_STUDIES:
        code = case["country_code"]
        years = [
            case["baseline_start"],
            case["baseline_end"],
            case["policy_year"],
            case["after_end"],
        ]
        missing = [
            year for year in years if (code, year) not in lookup
        ]
        if missing:
            raise ValueError(
                f"Missing required {COUNTRY_NAMES[code]} observations: "
                + ", ".join(str(year) for year in missing)
                + "."
            )
        baseline_start = lookup[(code, case["baseline_start"])]
        baseline_end = lookup[(code, case["baseline_end"])]
        post_start = lookup[(code, case["baseline_end"])]
        post_end = lookup[(code, case["after_end"])]
        summaries.append(
            {
                **case,
                "country": COUNTRY_NAMES[code],
                "baseline_start_share": baseline_start,
                "baseline_end_share": baseline_end,
                "post_end_share": post_end,
                "post_change": post_end - post_start,
                "series": sorted(
                    (
                        row
                        for row in rows
                        if row["country_code"] == code
                    ),
                    key=lambda row: row["year"],
                ),
            }
        )
    return summaries


def summarize(rows):
    return {
        "first_year": min(case["baseline_start"] for case in CASE_STUDIES),
        "latest_year": max(row["year"] for row in rows),
        "case_studies": case_study_summaries(rows),
    }


def x_position(year, first_year, last_year, left, right):
    return left + (year - first_year) / (last_year - first_year) * (
        right - left
    )


def y_position(share, top, bottom):
    return bottom - share / 60 * (bottom - top)


def render_svg(rows, summary):
    width, height = 1500, 1020
    first_year = summary["first_year"]
    last_year = summary["latest_year"]
    plot_left, plot_right = 440, 1410
    panel_top = 174
    panel_height = 250
    row_gap = 24
    plot_top_offset, plot_bottom_offset = 62, 220
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title description" viewBox="0 0 {width} {height}">',
        '<title id="title">EV adoption rose after purchase incentives changed</title>',
        (
            '<desc id="description">Three country line charts compare the '
            "gradual early rise in electric-car sales shares with larger rises "
            "after purchase-incentive changes in 2020. Germany, China and "
            "France are shown. The timing is suggestive, not proof that the "
            "policies caused the increases."
            "</desc>"
        ),
        '<rect width="100%" height="100%" fill="#172b4d"/>',
        '<text x="76" y="54" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="29" font-weight="700">Flat… policy change… then the EV share climbs</text>',
        '<text x="78" y="85" fill="#c3cfdd" font-family="Arial, sans-serif" '
        'font-size="15">Selected cases where adoption accelerated after a '
        'purchase-incentive change · new passenger-car sales, 2015–2025</text>',
        '<text x="78" y="115" fill="#ffcc80" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">Policy timing is a clue, not proof '
        'of cause; 2020 annual data also include wider pandemic-era changes.</text>',
        '<rect x="72" y="134" width="1356" height="1" fill="#395174"/>',
    ]

    ticks = list(range(((first_year + 1) // 2) * 2, last_year + 1, 2))
    if first_year not in ticks:
        ticks.insert(0, first_year)
    if last_year not in ticks:
        ticks.append(last_year)
    for panel_index, case in enumerate(summary["case_studies"]):
        y0 = panel_top + panel_index * (panel_height + row_gap)
        plot_top = y0 + plot_top_offset
        plot_bottom = y0 + plot_bottom_offset
        visible_series = [
            row
            for row in case["series"]
            if first_year <= row["year"] <= last_year
        ]
        policy_x = x_position(
            case["policy_year"], first_year, last_year, plot_left, plot_right
        )
        baseline_start_x = x_position(
            case["baseline_start"],
            first_year,
            last_year,
            plot_left,
            plot_right,
        )
        baseline_end_x = x_position(
            case["baseline_end"],
            first_year,
            last_year,
            plot_left,
            plot_right,
        )
        elements.extend(
            [
                f'<rect x="72" y="{y0}" width="1356" height="{panel_height}" '
                'rx="9" fill="#1d3558" stroke="#395174" stroke-width="1"/>',
                f'<text x="94" y="{y0+40}" fill="{case["color"]}" '
                'font-family="Arial, sans-serif" font-size="24" '
                f'font-weight="700">{html.escape(case["country"])}</text>',
                f'<text x="95" y="{y0+72}" fill="#f1f4f8" '
                'font-family="Arial, sans-serif" font-size="13">'
                f'{case["policy"][0]}</text>',
                f'<text x="95" y="{y0+94}" fill="#c3cfdd" '
                'font-family="Arial, sans-serif" font-size="13">'
                f'{case["policy"][1]}</text>',
                f'<text x="95" y="{y0+143}" fill="#c3cfdd" '
                'font-family="Arial, sans-serif" font-size="12">'
                f'Before: {case["baseline_start_share"]:.1f}% '
                f'({case["baseline_start"]}) → '
                f'{case["baseline_end_share"]:.1f}% '
                f'({case["baseline_end"]})</text>',
                f'<text x="95" y="{y0+170}" fill="{case["color"]}" '
                'font-family="Arial, sans-serif" font-size="15" '
                'font-weight="700">'
                f'+{case["post_change"]:.1f} pp by {case["after_end"]}</text>',
                f'<rect x="{baseline_start_x:.2f}" y="{plot_top}" '
                f'width="{max(0, baseline_end_x-baseline_start_x):.2f}" '
                f'height="{plot_bottom-plot_top}" fill="#92a3b9" opacity="0.08"/>',
            ]
        )
        for share in range(0, 61, 20):
            y = y_position(share, plot_top, plot_bottom)
            elements.extend(
                [
                    f'<line x1="{plot_left}" y1="{y:.2f}" x2="{plot_right}" '
                    f'y2="{y:.2f}" stroke="#395174" stroke-width="1"/>',
                    f'<text x="423" y="{y+4:.2f}" text-anchor="end" '
                    'fill="#92a3b9" font-family="Arial, sans-serif" '
                    f'font-size="11">{share}%</text>',
                ]
            )
        for year in ticks:
            x = x_position(year, first_year, last_year, plot_left, plot_right)
            elements.extend(
                [
                    f'<line x1="{x:.2f}" y1="{plot_top}" x2="{x:.2f}" '
                    f'y2="{plot_bottom}" stroke="#314a6c" stroke-width="1"/>',
                    f'<text x="{x:.2f}" y="{plot_bottom+19}" '
                    'text-anchor="middle" fill="#c3cfdd" '
                    'font-family="Arial, sans-serif" font-size="11">'
                    f"{year}</text>",
                ]
            )

        elements.extend(
            [
                f'<line x1="{policy_x:.2f}" y1="{plot_top}" '
                f'x2="{policy_x:.2f}" y2="{plot_bottom}" '
                f'stroke="{case["color"]}" stroke-width="1.8" '
                'stroke-dasharray="6 5"/>',
                f'<rect x="{policy_x-59:.2f}" y="{y0+34}" width="118" '
                'height="21" rx="4" fill="#172b4d"/>',
                f'<text x="{policy_x:.2f}" y="{y0+49}" '
                f'text-anchor="middle" fill="{case["color"]}" '
                'font-family="Arial, sans-serif" font-size="11" '
                'font-weight="700">POLICY · 2020</text>',
            ]
        )
        baseline = [
            row
            for row in visible_series
            if case["baseline_start"] <= row["year"] <= case["baseline_end"]
        ]
        post_policy = [
            row
            for row in visible_series
            if case["baseline_end"] <= row["year"] <= last_year
        ]
        for segment, color, stroke_width in (
            (baseline, MUTED_LINE, "2.5"),
            (post_policy, case["color"], "4"),
        ):
            path = " ".join(
                ("M" if index == 0 else "L")
                + " "
                + f'{x_position(row["year"], first_year, last_year, plot_left, plot_right):.2f} '
                + f'{y_position(row["ev_sales_share_percent"], plot_top, plot_bottom):.2f}'
                for index, row in enumerate(segment)
            )
            elements.append(
                f'<path d="{path}" fill="none" stroke="{color}" '
                f'stroke-width="{stroke_width}" stroke-linejoin="round" '
                'stroke-linecap="round"/>'
            )
        for row in visible_series:
            color = (
                MUTED_LINE
                if row["year"] < case["policy_year"]
                else case["color"]
            )
            x = x_position(row["year"], first_year, last_year, plot_left, plot_right)
            y = y_position(row["ev_sales_share_percent"], plot_top, plot_bottom)
            elements.append(
                f'<circle cx="{x:.2f}" cy="{y:.2f}" r="4.3" fill="{color}" '
                'stroke="#172b4d" stroke-width="1.3"/>'
            )

        after_x = x_position(
            case["after_end"], first_year, last_year, plot_left, plot_right
        )
        after_y = y_position(case["post_end_share"], plot_top, plot_bottom)
        elements.extend(
            [
                f'<text x="{after_x+10:.2f}" y="{after_y-9:.2f}" '
                f'fill="{case["color"]}" font-family="Arial, sans-serif" '
                'font-size="12" font-weight="700">'
                f'{case["post_end_share"]:.0f}%</text>',
            ]
        )
        if panel_index == len(summary["case_studies"]) - 1:
            elements.append(
                f'<text x="{plot_left}" y="{plot_bottom+44}" '
                'fill="#c3cfdd" font-family="Arial, sans-serif" '
                'font-size="12">Electric vehicles as share of new passenger-car '
                'sales (%) · same 0–60% scale in every panel</text>'
            )

    elements.extend(
        [
            '<text x="78" y="1003" fill="#c3cfdd" '
            'font-family="Arial, sans-serif" font-size="11">'
            "Source: IEA Global EV Data Explorer / Global EV Outlook 2026; "
            "BEV + PHEV passenger cars. Policy dates: IEA Global EV Policy Explorer.</text>",
            "</svg>",
        ]
    )
    return "\n".join(elements)


def main():
    rows = load_rows()
    summary = summarize(rows)
    CHART_PATH.write_text(render_svg(rows, summary), encoding="utf-8")
    print(f"Saved chart to {CHART_PATH}.")
    for case in summary["case_studies"]:
        print(
            f'{case["country"]}: {case["baseline_end_share"]:.1f}% '
            f'({case["baseline_end"]}) to {case["post_end_share"]:.1f}% '
            f'({case["after_end"]}), +{case["post_change"]:.1f} percentage points.'
        )


if __name__ == "__main__":
    main()
