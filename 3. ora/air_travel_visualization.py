"""Download BTS passenger-mile data and render a source-backed SVG chart."""

import csv
import json
import math
from datetime import date
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "air_passenger_rpm.csv"
CHART_PATH = ROOT / "air_travel_disruptions.svg"
API_URL = "https://data.bts.gov/resource/bw6n-ddqk.json"
FIELDS = ("obs_date", "rpm", "rpm_d11")


def fetch_rows():
    query = urlencode(
        {
            "$select": ",".join(FIELDS),
            "$order": "obs_date",
            "$limit": 5000,
        }
    )
    request = Request(
        f"{API_URL}?{query}",
        headers={"Accept": "application/json", "User-Agent": "air-travel-homework/1.0"},
    )
    with urlopen(request, timeout=45) as response:
        rows = json.load(response)

    complete_rows = []
    skipped = 0
    for row in rows:
        raw_date = row.get("obs_date")
        raw_rpm = row.get("rpm")
        raw_adjusted = row.get("rpm_d11")
        if not raw_date or raw_rpm in (None, "") or raw_adjusted in (None, ""):
            skipped += 1
            continue
        observation_date = date.fromisoformat(raw_date[:10])
        rpm = float(raw_rpm)
        adjusted_rpm = float(raw_adjusted)
        if not math.isfinite(rpm) or not math.isfinite(adjusted_rpm):
            raise ValueError(f"Non-finite RPM observation for {observation_date}.")
        complete_rows.append(
            {
                "date": observation_date,
                "rpm_thousands": rpm,
                "rpm_seasonally_adjusted_thousands": adjusted_rpm,
            }
        )

    if not complete_rows:
        raise ValueError("The BTS dataset returned no complete passenger-mile rows.")
    return complete_rows, skipped


def save_csv(rows):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=(
                "date",
                "rpm_thousands",
                "rpm_seasonally_adjusted_thousands",
            ),
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "date": row["date"].isoformat(),
                    "rpm_thousands": f'{row["rpm_thousands"]:.0f}',
                    "rpm_seasonally_adjusted_thousands": (
                        f'{row["rpm_seasonally_adjusted_thousands"]:.0f}'
                    ),
                }
            )


def value_for_month(rows, month):
    year, month_number = (int(part) for part in month.split("-"))
    for row in rows:
        if row["date"].year == year and row["date"].month == month_number:
            return row["rpm_seasonally_adjusted_thousands"]
    raise ValueError(f"The BTS series has no observation for {month}.")


def percent_change(start, end):
    if start == 0:
        raise ValueError("Cannot calculate percentage change from a zero baseline.")
    return (end / start - 1) * 100


def event_summary(rows):
    september_2001 = value_for_month(rows, "2001-09")
    august_2001 = value_for_month(rows, "2001-08")
    february_2020 = value_for_month(rows, "2020-02")
    april_2020 = value_for_month(rows, "2020-04")
    latest = rows[-1]
    return {
        "sep_2001_change": percent_change(august_2001, september_2001),
        "covid_change": percent_change(february_2020, april_2020),
        "latest_date": latest["date"],
        "latest_billions": latest["rpm_seasonally_adjusted_thousands"] / 1_000_000,
        "feb_2020_billions": february_2020 / 1_000_000,
        "latest_vs_feb_2020": percent_change(february_2020, latest[
            "rpm_seasonally_adjusted_thousands"
        ]),
    }


def month_index(observation_date):
    return observation_date.year * 12 + observation_date.month - 1


def render_svg(rows, summary):
    width, height = 1280, 770
    left, right, top, bottom = 100, 1232, 230, 638
    first_month = month_index(rows[0]["date"])
    last_month = month_index(rows[-1]["date"])
    max_billions = max(
        row["rpm_seasonally_adjusted_thousands"] / 1_000_000 for row in rows
    )
    y_max = math.ceil(max_billions / 20) * 20

    def x_position(observation_date):
        return left + (month_index(observation_date) - first_month) / (
            last_month - first_month
        ) * (right - left)

    def y_position(billions):
        return bottom - billions / y_max * (bottom - top)

    points = [
        (
            x_position(row["date"]),
            y_position(row["rpm_seasonally_adjusted_thousands"] / 1_000_000),
            row,
        )
        for row in rows
    ]
    line_path = " ".join(
        ("M" if index == 0 else "L") + f" {x:.2f} {y:.2f}"
        for index, (x, y, _) in enumerate(points)
    )
    september_marker = date(2001, 9, 1)
    covid_marker = date(2020, 4, 1)
    september_x = x_position(september_marker)
    covid_x = x_position(covid_marker)

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title description" viewBox="0 0 {width} {height}">',
        "<title id=\"title\">U.S. airline passenger travel after 9/11 and COVID-19</title>",
        (
            '<desc id="description">Monthly seasonally adjusted U.S. scheduled '
            "passenger-flight revenue passenger-miles from "
            f'{rows[0]["date"].year} through {rows[-1]["date"].strftime("%B %Y")}. '
            "A 29.5 percent decline between August and September 2001 and a "
            "96.7 percent decline between February and April 2020 are highlighted."
            "</desc>"
        ),
        '<rect width="100%" height="100%" fill="#172b4d"/>',
        '<text x="78" y="57" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="29" font-weight="700">U.S. airline passenger travel after '
        "9/11 and COVID-19</text>",
        '<text x="80" y="88" fill="#c3cfdd" font-family="Arial, sans-serif" '
        'font-size="15">Monthly revenue passenger-miles, seasonally adjusted · '
        f'{rows[0]["date"].year}–{rows[-1]["date"].strftime("%B %Y")}</text>',
        f'<text x="{september_x:.2f}" y="137" text-anchor="middle" '
        'fill="#b39ddb" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">SEPTEMBER 2001</text>',
        f'<text x="{september_x:.2f}" y="160" text-anchor="middle" '
        'fill="#f1f4f8" font-family="Arial, sans-serif" '
        f'font-size="16">−{abs(summary["sep_2001_change"]):.1f}% from August</text>',
        f'<line x1="{september_x:.2f}" y1="171" x2="{september_x:.2f}" '
        'y2="210" stroke="#b39ddb" stroke-width="1.5"/>',
        f'<text x="{covid_x:.2f}" y="137" text-anchor="middle" '
        'fill="#ff8a75" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">COVID-19 · APRIL 2020 LOW</text>',
        f'<text x="{covid_x:.2f}" y="160" text-anchor="middle" '
        'fill="#f1f4f8" font-family="Arial, sans-serif" '
        f'font-size="16">−{abs(summary["covid_change"]):.1f}% from February</text>',
        f'<line x1="{covid_x:.2f}" y1="171" x2="{covid_x:.2f}" '
        'y2="210" stroke="#ff8a75" stroke-width="1.5"/>',
    ]

    plot_width = right - left
    plot_height = bottom - top
    elements.append(
        f'<rect x="{left}" y="{top}" width="{plot_width}" height="{plot_height}" '
        'fill="#20395f" stroke="#395174" stroke-width="1"/>'
    )
    for billions in range(0, y_max + 1, 20):
        y = y_position(billions)
        elements.extend(
            [
                f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
                'stroke="#395174" stroke-width="1"/>',
                f'<text x="{left - 14}" y="{y + 5:.2f}" text-anchor="end" '
                'fill="#c3cfdd" font-family="Arial, sans-serif" font-size="13">'
                f"{billions}</text>",
            ]
        )

    for event_date, color in (
        (september_marker, "#b39ddb"),
        (covid_marker, "#ff8a75"),
    ):
        x = x_position(event_date)
        elements.append(
            f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" '
            f'stroke="{color}" stroke-width="1.3" stroke-dasharray="5 5" '
            'opacity="0.85"/>'
        )

    first_year = (rows[0]["date"].year // 5) * 5
    for year in range(first_year, rows[-1]["date"].year + 1, 5):
        tick = date(year, 1, 1)
        x = x_position(tick)
        if left <= x <= right:
            elements.extend(
                [
                    f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" '
                    f'y2="{bottom}" stroke="#314a6c"/>',
                    f'<text x="{x:.2f}" y="{bottom + 26}" text-anchor="middle" '
                    'fill="#c3cfdd" font-family="Arial, sans-serif" '
                    f'font-size="13">{year}</text>',
                ]
            )

    elements.extend(
        [
            f'<path d="{line_path}" fill="none" stroke="#58c4dd" '
            'stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>',
            '<text x="38" y="434" transform="rotate(-90 38 434)" '
            'text-anchor="middle" fill="#f1f4f8" '
            'font-family="Arial, sans-serif" font-size="13">'
            "Revenue passenger-miles (billions)</text>",
        ]
    )
    for event_date, color in (
        (september_marker, "#b39ddb"),
        (covid_marker, "#ff8a75"),
    ):
        event_row = next(row for row in rows if row["date"] == event_date)
        elements.append(
            f'<circle cx="{x_position(event_date):.2f}" '
            f'cy="{y_position(event_row["rpm_seasonally_adjusted_thousands"] / 1_000_000):.2f}" '
            f'r="5.5" fill="{color}" stroke="#172b4d" stroke-width="2"/>'
        )

    elements.extend(
        [
            '<text x="100" y="715" fill="#c3cfdd" '
            'font-family="Arial, sans-serif" font-size="12">'
            "Source: U.S. Bureau of Transportation Statistics. RPMs shown in "
            "billions; published source values are in thousands.</text>",
            "</svg>",
        ]
    )
    return "\n".join(elements)


def main():
    rows, skipped = fetch_rows()
    summary = event_summary(rows)
    save_csv(rows)
    CHART_PATH.write_text(render_svg(rows, summary), encoding="utf-8")
    print(f"Saved {len(rows)} observations to {DATA_PATH}.")
    if skipped:
        print(f"Skipped {skipped} incomplete dataset row(s).")
    print(f"Saved chart to {CHART_PATH}.")
    print(
        "Seasonally adjusted passenger-mile change: "
        f'{summary["sep_2001_change"]:.1f}% (Aug–Sep 2001); '
        f'{summary["covid_change"]:.1f}% (Feb–Apr 2020).'
    )
    print(
        f'Latest complete month: {summary["latest_date"]:%B %Y} '
        f'({summary["latest_billions"]:.1f} billion RPMs).'
    )


if __name__ == "__main__":
    main()
