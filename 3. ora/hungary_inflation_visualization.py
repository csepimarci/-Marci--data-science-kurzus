"""Chart Hungary's 1946 adópengő index on a logarithmic scale."""

import csv
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "hungary_adopengo_index.csv"
CHART_PATH = ROOT / "hungary_hyperinflation.svg"


def load_observations(path=DATA_PATH):
    observations = []
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != ["date", "index_value"]:
            raise ValueError("Expected CSV columns: date,index_value.")
        for row_number, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(
                    f"CSV row {row_number} has an unexpected number of fields."
                )
            observation_date = date.fromisoformat(row["date"])
            try:
                index_value = float(row["index_value"])
            except ValueError as exc:
                raise ValueError(
                    f"Invalid index value on {observation_date}."
                ) from exc
            if not math.isfinite(index_value) or index_value <= 0:
                raise ValueError(
                    f"Index value must be positive and finite on {observation_date}."
                )
            observations.append(
                {"date": observation_date, "index_value": index_value}
            )

    if len(observations) < 2:
        raise ValueError("At least two adópengő index observations are required.")
    if observations != sorted(observations, key=lambda row: row["date"]):
        raise ValueError("Adópengő index observations must be in date order.")
    if len({row["date"] for row in observations}) != len(observations):
        raise ValueError("Adópengő index observation dates must be unique.")
    return observations


def render_svg(observations):
    if len(observations) < 2:
        raise ValueError("At least two observations are required to draw the chart.")
    if any(
        row["index_value"] <= 0 or not math.isfinite(row["index_value"])
        for row in observations
    ):
        raise ValueError("Logarithmic chart values must be positive and finite.")

    width, height = 1280, 790
    left, right, top, bottom = 112, 1200, 255, 630
    first_date = observations[0]["date"]
    last_date = observations[-1]["date"]
    first_day = first_date.toordinal()
    last_day = last_date.toordinal()
    max_exponent = math.ceil(
        math.log10(max(row["index_value"] for row in observations))
    )

    def x_position(observation_date):
        return left + (
            (observation_date.toordinal() - first_day)
            / (last_day - first_day)
            * (right - left)
        )

    def y_position(index_value):
        return bottom - math.log10(index_value) / max_exponent * (bottom - top)

    points = [
        (
            x_position(row["date"]),
            y_position(row["index_value"]),
            row,
        )
        for row in observations
    ]
    line_path = " ".join(
        ("M" if index == 0 else "L") + f" {x:.2f} {y:.2f}"
        for index, (x, y, _) in enumerate(points)
    )

    june = next(
        row for row in observations
        if row["date"] == date(1946, 6, 1)
    )
    july_first = next(
        row for row in observations
        if row["date"] == date(1946, 7, 1)
    )
    final = observations[-1]
    june_x = x_position(june["date"])
    june_y = y_position(june["index_value"])
    july_x = x_position(july_first["date"])
    july_y = y_position(july_first["index_value"])
    final_x, final_y, _ = points[-1]

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title description" viewBox="0 0 {width} {height}">',
        '<title id="title">Hungary’s 1946 hyperinflation and the adópengő index</title>',
        (
            '<desc id="description">Eight published adópengő index observations '
            "from January 1 to July 31, 1946, rising from 1 to 2 times 10 to "
            "the 21st. The vertical axis is logarithmic. A separate note reports "
            "the Cato Institute's peak monthly price-inflation estimate. The line "
            "connects the eight reported observations and does not show daily values."
            "</desc>"
        ),
        '<rect width="100%" height="100%" fill="#172b4d"/>',
        '<text x="78" y="57" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="29" font-weight="700">Hungary’s 1946 hyperinflation</text>',
        '<text x="80" y="88" fill="#c3cfdd" font-family="Arial, sans-serif" '
        'font-size="15">Adópengő index · eight reported dates · logarithmic scale</text>',
        '<rect x="78" y="112" width="1060" height="75" rx="4" fill="#20395f"/>',
        '<text x="98" y="141" fill="#ff8a75" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">SEPARATE MEASURE · JULY 1946 PEAK MONTHLY INFLATION</text>',
        '<text x="98" y="168" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="17">4.19 × 10¹⁶% · prices doubled in about 15 hours (Hanke–Krus)</text>',
        f'<text x="{june_x - 12:.2f}" y="216" text-anchor="end" '
        'fill="#b39ddb" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">1 JUNE 1946</text>',
        f'<text x="{june_x - 12:.2f}" y="238" text-anchor="end" '
        'fill="#f1f4f8" font-family="Arial, sans-serif" '
        f'font-size="15">{june["index_value"]:,.0f}</text>',
        f'<line x1="{june_x:.2f}" y1="244" x2="{june_x:.2f}" y2="{top}" '
        'stroke="#b39ddb" stroke-width="1.5"/>',
        f'<text x="{right}" y="216" text-anchor="end" '
        'fill="#ff8a75" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">31 JULY 1946</text>',
        f'<text x="{right}" y="238" text-anchor="end" '
        'fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="15">2 × 10²¹</text>',
        f'<line x1="{final_x:.2f}" y1="244" x2="{final_x:.2f}" y2="{top}" '
        'stroke="#ff8a75" stroke-width="1.5"/>',
        f'<rect x="{left}" y="{top}" width="{right - left}" '
        f'height="{bottom - top}" fill="#20395f" stroke="#395174" stroke-width="1"/>',
    ]

    for exponent in range(0, max_exponent + 1, 3):
        y = y_position(10**exponent)
        elements.extend(
            [
                f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
                'stroke="#395174" stroke-width="1"/>',
                f'<text x="{left - 14}" y="{y + 5:.2f}" text-anchor="end" '
                'fill="#c3cfdd" font-family="Arial, sans-serif" font-size="13">'
                f"10^{exponent}</text>",
            ]
        )

    for month, label in enumerate(
        ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul"), start=1
    ):
        month_date = date(1946, month, 1)
        x = x_position(month_date)
        elements.extend(
            [
                f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" '
                'stroke="#314a6c" stroke-width="1"/>',
                f'<text x="{x:.2f}" y="{bottom + 27}" text-anchor="middle" '
                'fill="#c3cfdd" font-family="Arial, sans-serif" font-size="13">'
                f"{label}</text>",
            ]
        )

    elements.extend(
        [
            f'<path d="{line_path}" fill="none" stroke="#ff8a75" '
            'stroke-width="3" stroke-linejoin="round" stroke-linecap="round"/>',
        ]
    )
    for x, y, _ in points:
        elements.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.5" '
            'fill="#ff8a75" stroke="#f1f4f8" stroke-width="1.5"/>'
        )

    elements.extend(
        [
            f'<text x="{july_x - 12:.2f}" y="{july_y - 18:.2f}" '
            'text-anchor="end" fill="#f1f4f8" font-family="Arial, sans-serif" '
            'font-size="13" font-weight="700">1 Jul · 7.5 billion</text>',
            '<text x="78" y="704" fill="#c3cfdd" font-family="Arial, sans-serif" '
            'font-size="13">Adópengő index (pengős per adópengő), as reported in the source table.</text>',
            '<text x="78" y="729" fill="#c3cfdd" font-family="Arial, sans-serif" '
            'font-size="12">Dots are the eight published observations. The connecting line is a visual guide, not daily data.</text>',
            '<text x="78" y="754" fill="#c3cfdd" font-family="Arial, sans-serif" '
            'font-size="12">Sources: Garami, Pénzportál (via the Hungarian adópengő table); Hanke–Krus, World Hyperinflations.</text>',
            "</svg>",
        ]
    )
    return "\n".join(elements)


def main():
    observations = load_observations()
    CHART_PATH.write_text(render_svg(observations), encoding="utf-8")
    print(f"Loaded {len(observations)} published index observations.")
    print(f"Saved chart to {CHART_PATH}.")


if __name__ == "__main__":
    main()
