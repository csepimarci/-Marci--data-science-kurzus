"""Download CDC life-expectancy data and render the 1918 pandemic chart."""

import csv
import io
import math
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "us_life_expectancy_1900_2018.csv"
CHART_PATH = ROOT / "us_life_expectancy_1918_flu.svg"
DATA_URL = (
    "https://data.cdc.gov/api/views/w9j2-ggv5/rows.csv"
    "?accessType=DOWNLOAD"
)
YEARS_OF_INTEREST = (1917, 1918, 1919)


def fetch_rows():
    request = Request(
        DATA_URL,
        headers={
            "Accept": "text/csv",
            "User-Agent": "life-expectancy-homework/1.0",
        },
    )
    with urlopen(request, timeout=45) as response:
        content = response.read().decode("utf-8-sig")

    source_rows = csv.DictReader(io.StringIO(content))
    required_fields = {
        "Year",
        "Race",
        "Sex",
        "Average Life Expectancy (Years)",
    }
    if not source_rows.fieldnames or not required_fields.issubset(
        source_rows.fieldnames
    ):
        raise ValueError("CDC dataset is missing expected life-expectancy fields.")

    rows = []
    for source_row in source_rows:
        if source_row["Race"] != "All Races" or source_row["Sex"] != "Both Sexes":
            continue
        raw_value = source_row["Average Life Expectancy (Years)"]
        if raw_value in (None, ""):
            continue
        year = int(source_row["Year"])
        life_expectancy = float(raw_value)
        if not math.isfinite(life_expectancy):
            raise ValueError(f"Non-finite life expectancy for {year}.")
        rows.append({"year": year, "life_expectancy_years": life_expectancy})

    rows.sort(key=lambda row: row["year"])
    if not rows:
        raise ValueError("The CDC dataset returned no all-races life-expectancy rows.")
    if len({row["year"] for row in rows}) != len(rows):
        raise ValueError("The CDC dataset returned duplicate annual observations.")
    values = {row["year"] for row in rows}
    if not set(YEARS_OF_INTEREST).issubset(values):
        raise ValueError("The CDC dataset is missing one or more 1917–1919 values.")
    return rows


def save_csv(rows):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output,
            fieldnames=("year", "life_expectancy_years"),
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "year": row["year"],
                    "life_expectancy_years": (
                        f'{row["life_expectancy_years"]:.1f}'
                    ),
                }
            )


def summarize(rows):
    by_year = {row["year"]: row["life_expectancy_years"] for row in rows}
    missing = set(YEARS_OF_INTEREST) - by_year.keys()
    if missing:
        raise ValueError(
            "Cannot summarize the 1918 shock; missing values for "
            + ", ".join(str(year) for year in sorted(missing))
            + "."
        )

    before = by_year[1917]
    shock = by_year[1918]
    after = by_year[1919]
    return {
        "first_year": min(by_year),
        "last_year": max(by_year),
        "before": before,
        "shock": shock,
        "after": after,
        "drop_years": before - shock,
        "drop_percent": (shock / before - 1) * 100,
        "rebound_years": after - shock,
        "recovery_vs_1917": after - before,
    }


def render_svg(rows, summary):
    width, height = 1280, 790
    left, right, top, bottom = 94, 1214, 272, 622
    y_min, y_max = 30, 90
    first_year = rows[0]["year"]
    last_year = rows[-1]["year"]
    if first_year == last_year:
        raise ValueError("At least two annual observations are needed to plot.")

    def x_position(year):
        return left + (year - first_year) / (last_year - first_year) * (
            right - left
        )

    def y_position(value):
        return bottom - (value - y_min) / (y_max - y_min) * (bottom - top)

    points = [
        (
            x_position(row["year"]),
            y_position(row["life_expectancy_years"]),
            row,
        )
        for row in rows
    ]
    line_path = " ".join(
        ("M" if index == 0 else "L") + f" {x:.2f} {y:.2f}"
        for index, (x, y, _) in enumerate(points)
    )
    area_path = (
        f"{line_path} L {right} {bottom} L {left} {bottom} Z"
    )
    event_x = x_position(1918)
    event_y = y_position(summary["shock"])
    event_label_x = event_x + 18
    event_label_y = event_y - 16

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title description" viewBox="0 0 {width} {height}">',
        '<title id="title">The 1918 flu pandemic and U.S. life expectancy</title>',
        (
            '<desc id="description">Annual U.S. life expectancy at birth from '
            f'{first_year} to {last_year}. It falls from '
            f'{summary["before"]:.1f} years in 1917 to '
            f'{summary["shock"]:.1f} in 1918, then rebounds to '
            f'{summary["after"]:.1f} in 1919.</desc>'
        ),
        '<rect width="100%" height="100%" fill="#111114"/>',
        '<text x="76" y="55" fill="#fff5f5" font-family="Arial, sans-serif" '
        'font-size="30" font-weight="700">The year life expectancy fell '
        f'{summary["drop_years"]:.1f} years</text>',
        '<text x="78" y="87" fill="#d2c9cb" font-family="Arial, sans-serif" '
        'font-size="15">U.S. life expectancy at birth · CDC/NCHS · '
        f'{first_year}–{last_year}</text>',
        '<text x="80" y="139" fill="#ff6574" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">1917 · BEFORE</text>',
        '<text x="80" y="174" fill="#fff5f5" font-family="Arial, sans-serif" '
        f'font-size="27" font-weight="700">{summary["before"]:.1f} years</text>',
        '<text x="399" y="139" fill="#ff6574" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">1918 · PANDEMIC YEAR</text>',
        '<text x="399" y="174" fill="#fff5f5" font-family="Arial, sans-serif" '
        f'font-size="27" font-weight="700">{summary["shock"]:.1f} years</text>',
        '<text x="399" y="198" fill="#ff6574" font-family="Arial, sans-serif" '
        f'font-size="14">−{summary["drop_years"]:.1f} years '
        f'({summary["drop_percent"]:.1f}%)</text>',
        '<text x="764" y="139" fill="#ff6574" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">1919 · REBOUND</text>',
        '<text x="764" y="174" fill="#fff5f5" font-family="Arial, sans-serif" '
        f'font-size="27" font-weight="700">{summary["after"]:.1f} years</text>',
        '<text x="764" y="198" fill="#d2c9cb" font-family="Arial, sans-serif" '
        f'font-size="14">+{summary["rebound_years"]:.1f} from 1918</text>',
        '<text x="1060" y="139" fill="#ff6574" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">ONE-YEAR SNAPSHOT</text>',
        '<text x="1060" y="174" fill="#fff5f5" font-family="Arial, sans-serif" '
        'font-size="16" font-weight="700">Not a lifespan forecast</text>',
        f'<rect x="{left}" y="{top}" width="{right-left}" '
        f'height="{bottom-top}" fill="#1b191d" stroke="#42343a"/>',
    ]

    for value in range(y_min, y_max + 1, 10):
        y = y_position(value)
        elements.extend(
            [
                f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
                'stroke="#382e33" stroke-width="1"/>',
                f'<text x="{left-14}" y="{y+5:.2f}" text-anchor="end" '
                'fill="#c9bdc0" font-family="Arial, sans-serif" font-size="12">'
                f"{value}</text>",
            ]
        )

    tick_years = list(range(((first_year + 9) // 10) * 10, last_year + 1, 10))
    if not tick_years or tick_years[-1] != last_year:
        tick_years.append(last_year)
    for year in tick_years:
        x = x_position(year)
        elements.extend(
            [
                f'<line x1="{x:.2f}" y1="{bottom}" x2="{x:.2f}" '
                f'y2="{bottom+5}" stroke="#7d6d72"/>',
                f'<text x="{x:.2f}" y="{bottom+24}" text-anchor="middle" '
                'fill="#c9bdc0" font-family="Arial, sans-serif" font-size="11">'
                f"{year}</text>",
            ]
        )

    elements.extend(
        [
            f'<rect x="{event_x-5:.2f}" y="{top}" width="10" '
            f'height="{bottom-top}" fill="#b8172c" opacity="0.18"/>',
            f'<line x1="{event_x:.2f}" y1="{top}" x2="{event_x:.2f}" '
            f'y2="{bottom}" stroke="#ff5263" stroke-width="1.5" '
            'stroke-dasharray="5 6"/>',
            f'<path d="{area_path}" fill="#a9162a" opacity="0.22"/>',
            f'<path d="{line_path}" fill="none" stroke="#ff5263" '
            'stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>',
            f'<circle cx="{event_x:.2f}" cy="{event_y:.2f}" r="10" '
            'fill="#111114" stroke="#ff5263" stroke-width="4"/>',
            f'<text x="{event_label_x:.2f}" y="{event_label_y:.2f}" '
            'fill="#fff5f5" font-family="Arial, sans-serif" font-size="13" '
            f'font-weight="700">{summary["shock"]:.1f}</text>',
            '<text x="80" y="698" fill="#ff6574" font-family="Arial, sans-serif" '
            'font-size="13" font-weight="700">WHAT THE LINE MEASURES</text>',
            '<text x="80" y="721" fill="#ded5d7" font-family="Arial, sans-serif" '
            'font-size="13">Period life expectancy summarizes that year’s death '
            'rates across ages; it is not the average age of people who died.</text>',
            '<text x="80" y="754" fill="#95888c" font-family="Arial, sans-serif" '
            'font-size="11">Source: CDC/NCHS · All races, both sexes · '
            'Historical annual data · The chart shows association, not '
            'causation.</text>',
            "</svg>",
        ]
    )
    return "\n".join(elements)


def main():
    rows = fetch_rows()
    save_csv(rows)
    summary = summarize(rows)
    CHART_PATH.write_text(render_svg(rows, summary), encoding="utf-8")
    print(
        f"Saved {len(rows)} annual observations to {DATA_PATH} and "
        f"chart to {CHART_PATH}."
    )


if __name__ == "__main__":
    main()
