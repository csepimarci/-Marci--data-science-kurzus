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
        for row in reader:
            observation_date = date.fromisoformat(row["date"])
            index_value = float(row["index_value"])
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

    width, height = 1200, 770
    left, right, top, bottom = 112, 1140, 245, 605
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

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title description" viewBox="0 0 {width} {height}">',
        '<title id="title">Hungary’s 1946 hyperinflation and the adópengő index</title>',
        (
            '<desc id="description">Eight published adópengő index observations '
            "from January 1 to July 31, 1946. The vertical axis is logarithmic. "
            "The index rises from 1 to 2 times 10 to the 21st. A separate note "
            "reports the Cato Institute's peak monthly price-inflation estimate."
            "</desc>"
        ),
        '<rect width="100%" height="100%" fill="#281923"/>',
        '<text x="76" y="55" fill="#fff2ea" font-family="Arial, sans-serif" '
        'font-size="29" font-weight="700">Hungary’s 1946 hyperinflation</text>',
        '<text x="78" y="87" fill="#e4cbd0" font-family="Arial, sans-serif" '
        'font-size="15">The adópengő index · eight published dates · logarithmic scale</text>',
        '<rect x="78" y="112" width="1060" height="78" rx="4" fill="#3d2631"/>',
        '<text x="98" y="143" fill="#ffad83" font-family="Arial, sans-serif" '
        'font-size="14" font-weight="700">SEPARATE PRICE-INFLATION MEASURE · JULY 1946</text>',
        '<text x="98" y="169" fill="#fff2ea" font-family="Arial, sans-serif" '
        'font-size="17">Hanke–Krus report a peak monthly inflation rate of '
        '4.19 × 10¹⁶% (prices doubling in about 15 hours).</text>',
        f'<rect x="{left}" y="{top}" width="{right - left}" height="{bottom - top}" '
        'fill="#38232f" stroke="#63404a" stroke-width="1"/>',
    ]

    for exponent in range(max_exponent + 1):
        y = y_position(10**exponent)
        elements.extend(
            [
                f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
                'stroke="#63404a" stroke-width="1"/>',
                f'<text x="{left - 14}" y="{y + 5:.2f}" text-anchor="end" '
                'fill="#e4cbd0" font-family="Arial, sans-serif" font-size="13">'
                f"10^{exponent}</text>",
            ]
        )

    months = (
        (1, "Jan"),
        (2, "Feb"),
        (3, "Mar"),
        (4, "Apr"),
        (5, "May"),
        (6, "Jun"),
        (7, "Jul"),
    )
    for month, label in months:
        month_date = date(1946, month, 1)
        x = x_position(month_date)
        elements.extend(
            [
                f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" '
                'stroke="#523541" stroke-width="1"/>',
                f'<text x="{x:.2f}" y="{bottom + 24}" text-anchor="middle" '
                'fill="#e4cbd0" font-family="Arial, sans-serif" font-size="13">'
                f"{label}</text>",
            ]
        )

    for observation in observations:
        x = x_position(observation["date"])
        y = y_position(observation["index_value"])
        elements.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.5" '
            'fill="#ff986b" stroke="#fff2ea" stroke-width="1.5"/>'
        )

    end = observations[-1]
    end_x = x_position(end["date"])
    end_y = y_position(end["index_value"])
    elements.extend(
        [
            f'<line x1="{end_x - 10:.2f}" y1="{end_y + 9:.2f}" '
            f'x2="{end_x - 160:.2f}" y2="{end_y + 38:.2f}" '
            'stroke="#ffad83" stroke-width="1.5"/>',
            f'<text x="{end_x - 166:.2f}" y="{end_y + 57:.2f}" '
            'text-anchor="end" fill="#fff2ea" font-family="Arial, sans-serif" '
            'font-size="14" font-weight="700">31 Jul · 2 × 10²¹</text>',
            '<text x="78" y="684" fill="#e4cbd0" font-family="Arial, sans-serif" '
            'font-size="13">Adópengő index (pengős per adópengő), as reported in the cited table. '
            'Dots are source observations; no daily values are interpolated.</text>',
            '<text x="78" y="714" fill="#e4cbd0" font-family="Arial, sans-serif" '
            'font-size="12">Sources: Hungarian adópengő table; Hanke–Krus, '
            'World Hyperinflations. The two measures are not the same series.</text>',
            "</svg>",
        ]
    )
    return "\n".join(elements)


def main():
    observations = load_observations()
    CHART_PATH.write_text(render_svg(observations), encoding="utf-8")
    print(
        f"Saved chart for {len(observations)} published observations "
        f"to {CHART_PATH}."
    )


if __name__ == "__main__":
    main()
