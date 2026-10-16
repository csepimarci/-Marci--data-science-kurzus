"""Chart Hungary's monthly inflation rate and billion-pengő banknote period."""

import csv
import math
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "hungary_monthly_inflation_rates.csv"
CHART_PATH = ROOT / "hungary_hyperinflation.svg"


def load_observations(path=DATA_PATH):
    observations = []
    expected_fields = [
        "period_start",
        "period_end",
        "index_value_start",
        "index_value_end",
        "source",
    ]
    with path.open(newline="", encoding="utf-8") as source:
        reader = csv.DictReader(source)
        if reader.fieldnames != expected_fields:
            raise ValueError(
                f"Expected CSV columns: {','.join(expected_fields)}."
            )
        for row_number, row in enumerate(reader, start=2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(
                    f"CSV row {row_number} has an unexpected number of fields."
                )
            start = date.fromisoformat(row["period_start"])
            end = date.fromisoformat(row["period_end"])
            try:
                level_start = float(row["index_value_start"])
                level_end = float(row["index_value_end"])
            except ValueError as exc:
                raise ValueError(
                    f"Invalid index value in CSV row {row_number}."
                ) from exc
            if (
                not math.isfinite(level_start)
                or not math.isfinite(level_end)
                or level_start <= 0
                or level_end <= 0
            ):
                raise ValueError(
                    f"Index values must be positive and finite in CSV row {row_number}."
                )
            if end <= start:
                raise ValueError(
                    f"Period end must follow its start in CSV row {row_number}."
                )
            observations.append(
                {
                    "period_start": start,
                    "period_end": end,
                    "index_value_start": level_start,
                    "index_value_end": level_end,
                    "inflation_percent": (level_end / level_start - 1) * 100,
                    "source": row["source"],
                }
            )

    if not observations:
        raise ValueError("The monthly inflation dataset is empty.")
    if observations != sorted(observations, key=lambda row: row["period_start"]):
        raise ValueError("Inflation periods must be in date order.")
    for previous, current in zip(observations, observations[1:]):
        if current["period_start"] != previous["period_end"]:
            raise ValueError("Inflation periods must be contiguous and non-overlapping.")
    return observations


def render_svg(observations):
    if not observations:
        raise ValueError("At least one inflation observation is required.")
    if any(
        row["inflation_percent"] <= 0
        or not math.isfinite(row["inflation_percent"])
        for row in observations
    ):
        raise ValueError("Logarithmic chart values must be positive and finite.")

    width, height = 1280, 800
    left, right, top, bottom = 112, 1205, 285, 620
    first_date = date(1945, 8, 1)
    last_date = date(1946, 8, 1)
    first_day, last_day = first_date.toordinal(), last_date.toordinal()
    minimum_exponent = math.floor(
        math.log10(min(row["inflation_percent"] for row in observations))
    )
    maximum_exponent = math.ceil(
        math.log10(max(row["inflation_percent"] for row in observations))
    )

    def x_position(observation_date):
        return left + (
            (observation_date.toordinal() - first_day)
            / (last_day - first_day)
            * (right - left)
        )

    def y_position(inflation_percent):
        return bottom - (
            (math.log10(inflation_percent) - minimum_exponent)
            / (maximum_exponent - minimum_exponent)
            * (bottom - top)
        )

    points = [
        (
            x_position(row["period_end"]),
            y_position(row["inflation_percent"]),
            row,
        )
        for row in observations
    ]
    line_path = " ".join(
        ("M" if index == 0 else "L") + f" {x:.2f} {y:.2f}"
        for index, (x, y, _) in enumerate(points)
    )

    billion_note_date = date(1946, 5, 13)
    billion_note_x = x_position(billion_note_date)
    band_width = right - billion_note_x
    first_data_x = x_position(date(1946, 1, 1))
    peak_row = max(observations, key=lambda row: row["inflation_percent"])
    peak_x = x_position(peak_row["period_end"])
    peak_y = y_position(peak_row["inflation_percent"])

    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title description" viewBox="0 0 {width} {height}">',
        '<title id="title">Hungary’s monthly inflation during the 1946 hyperinflation</title>',
        (
            '<desc id="description">A logarithmic chart of the inflation rate '
            "calculated between seven consecutive published price-index dates "
            "from January through July 1946. It highlights the period from 13 "
            "May 1946, when a one-billion-pengő banknote was first issued, through "
            "the end of July. Monthly data before January 1946 is not included."
            "</desc>"
        ),
        '<rect width="100%" height="100%" fill="#172b4d"/>',
        '<text x="78" y="57" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="29" font-weight="700">Hungary’s hyperinflation, month by month</text>',
        '<text x="80" y="88" fill="#c3cfdd" font-family="Arial, sans-serif" '
        'font-size="15">Monthly inflation implied by published index changes · logarithmic scale</text>',
        '<rect x="78" y="111" width="1060" height="77" rx="4" fill="#20395f"/>',
        '<text x="98" y="141" fill="#ff8a75" font-family="Arial, sans-serif" '
        'font-size="13" font-weight="700">THE CATASTROPHIC PEAK · JULY 1946</text>',
        '<text x="98" y="168" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="16">Separate published estimate: 4.19 × 10¹⁶% monthly; prices doubled in about 15 hours.</text>',
        '<text x="80" y="230" fill="#c3cfdd" font-family="Arial, sans-serif" '
        'font-size="13">Hyperinflation: August 1945–July 1946 · monthly source observations begin in January 1946.</text>',
        f'<rect x="{left}" y="{top}" width="{first_data_x - left:.2f}" '
        f'height="{bottom - top}" fill="#526177" opacity="0.22"/>',
        f'<rect x="{billion_note_x:.2f}" y="{top}" width="{band_width:.2f}" '
        f'height="{bottom - top}" fill="#6b343e" opacity="0.42"/>',
        f'<rect x="{left}" y="{top}" width="{right - left}" '
        f'height="{bottom - top}" fill="none" stroke="#395174" stroke-width="1"/>',
        f'<line x1="{billion_note_x:.2f}" y1="{top}" '
        f'x2="{billion_note_x:.2f}" y2="{bottom}" stroke="#ff8a75" '
        'stroke-width="1.8" stroke-dasharray="6 5"/>',
        f'<text x="{billion_note_x + 10:.2f}" y="{top + 23}" '
        'fill="#ffd1c6" font-family="Arial, sans-serif" font-size="12" '
        'font-weight="700">BILLION-PENGŐ NOTES</text>',
        f'<text x="{billion_note_x + 10:.2f}" y="{top + 42}" '
        'fill="#f1f4f8" font-family="Arial, sans-serif" font-size="12">from 13 May</text>',
        f'<text x="{(left + first_data_x) / 2:.2f}" y="{(top + bottom) / 2:.2f}" '
        'text-anchor="middle" fill="#c3cfdd" font-family="Arial, sans-serif" '
        'font-size="13">No monthly observations</text>',
        f'<text x="{(left + first_data_x) / 2:.2f}" y="{(top + bottom) / 2 + 20:.2f}" '
        'text-anchor="middle" fill="#c3cfdd" font-family="Arial, sans-serif" '
        'font-size="13">in the cited series</text>',
        f'<text x="{left}" y="266" fill="#f1f4f8" font-family="Arial, sans-serif" '
        'font-size="14" font-weight="700">Inflation between published observations (%)</text>',
    ]

    for exponent in range(minimum_exponent, maximum_exponent + 1, 2):
        y = y_position(10**exponent)
        elements.extend(
            [
                f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
                'stroke="#395174" stroke-width="1"/>',
                f'<text x="{left - 14}" y="{y + 5:.2f}" text-anchor="end" '
                'fill="#c3cfdd" font-family="Arial, sans-serif" font-size="12">'
                f"10^{exponent}%</text>",
            ]
        )

    tick_dates = [
        date(1945, month, 1) for month in range(8, 13)
    ] + [date(1946, month, 1) for month in range(1, 8)]
    for month_date in tick_dates:
        x = x_position(month_date)
        month_label = month_date.strftime("%b")
        elements.extend(
            [
                f'<line x1="{x:.2f}" y1="{top}" x2="{x:.2f}" y2="{bottom}" '
                'stroke="#314a6c" stroke-width="1"/>',
                f'<text x="{x:.2f}" y="{bottom + 27}" text-anchor="middle" '
                'fill="#c3cfdd" font-family="Arial, sans-serif" font-size="13">'
                f"{month_label}</text>",
            ]
        )
        if month_date.month in (8, 1):
            elements.append(
                f'<text x="{x:.2f}" y="{bottom + 45}" text-anchor="middle" '
                'fill="#91a4bc" font-family="Arial, sans-serif" font-size="11">'
                f"{month_date.year}</text>"
            )

    elements.append(
        f'<path d="{line_path}" fill="none" stroke="#ff8a75" stroke-width="3" '
        'stroke-linejoin="round" stroke-linecap="round"/>'
    )
    label_offsets = (-12, 20, -12, 20, -12, 20)
    label_values = (
        "70%",
        "488%",
        "340%",
        "1,332%",
        "25,297%",
        "4.69 million%",
    )
    for index, (x, y, _) in enumerate(points):
        elements.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="#ff8a75" '
            'stroke="#f1f4f8" stroke-width="1.5"/>'
        )
        if index < len(label_values):
            elements.append(
                f'<text x="{x + 10:.2f}" y="{y + label_offsets[index]:.2f}" '
                'fill="#f1f4f8" font-family="Arial, sans-serif" font-size="12" '
                f'font-weight="700">{label_values[index]}</text>'
            )

    elements.extend(
        [
            f'<text x="{peak_x - 10:.2f}" y="{peak_y + 23:.2f}" '
            'text-anchor="end" fill="#f1f4f8" font-family="Arial, sans-serif" '
            'font-size="13" font-weight="700">26.7 trillion% in 30 days</text>',
            f'<line x1="{billion_note_x:.2f}" y1="{top - 20}" '
            f'x2="{billion_note_x:.2f}" y2="{top}" stroke="#ff8a75" stroke-width="1.5"/>',
            '<text x="78" y="690" fill="#c3cfdd" font-family="Arial, sans-serif" '
            'font-size="12">Rates are calculated from the published price-level values between the dates shown; the July interval is 1–31 July.</text>',
            '<text x="78" y="714" fill="#c3cfdd" font-family="Arial, sans-serif" '
            'font-size="12">The source is a historical pengő valuation index; here it is converted to simple monthly percentage changes.</text>',
            '<text x="78" y="738" fill="#c3cfdd" font-family="Arial, sans-serif" '
            'font-size="12">Separate peak estimate: Hanke–Krus; billion-pengő note issue date: historical banknote table. See homework for sources and limits.</text>',
            "</svg>",
        ]
    )
    return "\n".join(elements)


def main():
    observations = load_observations()
    CHART_PATH.write_text(render_svg(observations), encoding="utf-8")
    print(f"Loaded {len(observations)} month-long inflation observations.")
    print(f"Saved chart to {CHART_PATH}.")


if __name__ == "__main__":
    main()
