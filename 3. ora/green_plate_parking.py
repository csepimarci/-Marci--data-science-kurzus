"""Download EU alternative-fuel vehicle fleet data and chart Hungary's EV trend."""

import csv
import html
import io
import math
import re
from pathlib import Path
from urllib.request import Request, urlopen


ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "eu_alternative_fuel_vehicle_fleet.csv"
CHART_PATH = ROOT / "green_plate_parking.svg"
OBSERVATORY_URL = (
    "https://alternative-fuels-observatory.ec.europa.eu/transport-mode/road"
)
LATEST_COMPLETE_YEAR = 2025
BASE_YEAR = 2015
FUEL_TYPES = ("BEV", "PHEV", "H2", "LPG", "CNG", "LNG")
COUNTRIES = (
    ("Austria", "austria"),
    ("Belgium", "belgium"),
    ("Bulgaria", "bulgaria"),
    ("Croatia", "croatia"),
    ("Cyprus", "cyprus"),
    ("Czechia", "czech-republic"),
    ("Denmark", "denmark"),
    ("Estonia", "estonia"),
    ("Finland", "finland"),
    ("France", "france"),
    ("Germany", "germany"),
    ("Greece", "greece"),
    ("Hungary", "hungary"),
    ("Ireland", "ireland"),
    ("Italy", "italy"),
    ("Latvia", "latvia"),
    ("Lithuania", "lithuania"),
    ("Luxembourg", "luxembourg"),
    ("Malta", "malta"),
    ("Netherlands", "netherlands"),
    ("Poland", "poland"),
    ("Portugal", "portugal"),
    ("Romania", "romania"),
    ("Slovakia", "slovakia"),
    ("Slovenia", "slovenia"),
    ("Spain", "spain"),
    ("Sweden", "sweden"),
)
COMPARISON_COUNTRIES = (
    "Hungary",
    "Austria",
    "Czechia",
    "Poland",
    "Romania",
    "Slovakia",
)
COLORS = {
    "Hungary": "#8be28b",
    "Austria": "#c1e58b",
    "Czechia": "#52c9a0",
    "Poland": "#e0d978",
    "Romania": "#3eaa72",
    "Slovakia": "#79d1b1",
}


def fetch_country_rows(country_name, slug):
    page_url = f"{OBSERVATORY_URL}/{slug}"
    request = Request(
        page_url,
        headers={"Accept": "text/html", "User-Agent": "green-plate-coursework/1.0"},
    )
    with urlopen(request, timeout=45) as response:
        page = html.unescape(response.read().decode("utf-8")).replace("\\/", "/")

    source_match = re.search(
        r'https://[^"\\\s]+/total_number_of_af_passenger_cars_and_vans_m1_n1\.csv'
        r'\?token=[^"\\\s]+',
        page,
    )
    if not source_match:
        raise ValueError(f"No official vehicle-fleet CSV was published for {country_name}.")

    source_url = source_match.group(0)
    csv_request = Request(
        source_url,
        headers={"Accept": "text/csv", "User-Agent": "green-plate-coursework/1.0"},
    )
    with urlopen(csv_request, timeout=45) as response:
        source_csv = response.read().decode("utf-8-sig")

    source_rows = list(csv.reader(io.StringIO(source_csv)))
    if not source_rows or source_rows[0][0] != "YEAR":
        raise ValueError(f"Unexpected fleet CSV format for {country_name}.")

    observations = []
    for row in source_rows[1:]:
        if not row or not row[0].isdigit():
            continue
        year = int(row[0])
        if year > LATEST_COMPLETE_YEAR:
            continue
        for index, fuel_type in enumerate(source_rows[0][1:], start=1):
            if fuel_type not in FUEL_TYPES:
                raise ValueError(
                    f"Unexpected fuel type {fuel_type!r} for {country_name}."
                )
            raw_count = row[index] if index < len(row) else ""
            if raw_count.strip() == "":
                vehicle_count = None
            else:
                try:
                    vehicle_count = int(float(raw_count.replace(",", "")))
                except ValueError as exc:
                    raise ValueError(
                        f"Invalid {fuel_type} count for {country_name} in {year}."
                    ) from exc
                if vehicle_count < 0:
                    raise ValueError(
                        f"Negative {fuel_type} count for {country_name} in {year}."
                    )
            observations.append(
                {
                    "country": country_name,
                    "year": year,
                    "fuel_type": fuel_type,
                    "vehicle_count": vehicle_count,
                }
            )
    if not observations:
        raise ValueError(f"The official fleet CSV for {country_name} is empty.")
    return observations


def fetch_all_rows():
    observations = []
    for country_name, slug in COUNTRIES:
        observations.extend(fetch_country_rows(country_name, slug))
    return observations


def save_csv(rows):
    DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    with DATA_PATH.open("w", newline="", encoding="utf-8") as output:
        writer = csv.DictWriter(
            output, fieldnames=("country", "year", "fuel_type", "vehicle_count")
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    **row,
                    "vehicle_count": (
                        "" if row["vehicle_count"] is None else row["vehicle_count"]
                    ),
                }
            )


def ev_totals(rows):
    totals = {}
    for row in rows:
        if row["fuel_type"] not in ("BEV", "PHEV") or row["vehicle_count"] is None:
            continue
        key = (row["country"], row["year"])
        totals[key] = totals.get(key, 0) + row["vehicle_count"]
    return totals


def indexed_series(rows, countries=COMPARISON_COUNTRIES, base_year=BASE_YEAR):
    totals = ev_totals(rows)
    series = {}
    for country in countries:
        baseline = totals.get((country, base_year))
        if baseline is None or baseline <= 0:
            raise ValueError(f"No positive BEV+PHEV baseline for {country} in {base_year}.")
        country_series = []
        for year in sorted(year for name, year in totals if name == country):
            value = totals[(country, year)]
            country_series.append((year, value / baseline * 100))
        series[country] = country_series
    return series


def summary_statistics(rows):
    totals = ev_totals(rows)
    latest_year = max(year for country, year in totals if country == "Hungary")
    baseline = totals.get(("Hungary", BASE_YEAR))
    latest = totals.get(("Hungary", latest_year))
    if baseline is None or latest is None or baseline <= 0:
        raise ValueError("Hungary's complete BEV+PHEV fleet history is incomplete.")

    bev = next(
        row["vehicle_count"]
        for row in rows
        if row["country"] == "Hungary"
        and row["year"] == latest_year
        and row["fuel_type"] == "BEV"
    )
    phev = next(
        row["vehicle_count"]
        for row in rows
        if row["country"] == "Hungary"
        and row["year"] == latest_year
        and row["fuel_type"] == "PHEV"
    )
    if bev is None or phev is None:
        raise ValueError(f"Hungary's BEV or PHEV count is missing for {latest_year}.")
    return {
        "baseline_year": BASE_YEAR,
        "baseline_count": baseline,
        "latest_year": latest_year,
        "latest_count": latest,
        "growth_multiple": latest / baseline,
        "latest_bev": bev,
        "latest_phev": phev,
    }


def render_svg(rows):
    series = indexed_series(rows)
    first_year = min(year for values in series.values() for year, _ in values)
    last_year = max(year for values in series.values() for year, _ in values)
    max_index = max(value for values in series.values() for _, value in values)
    y_max = math.ceil(max_index / 100) * 100

    width, height = 1200, 740
    left, right, top, bottom = 100, 1140, 230, 610

    def x_position(year):
        return left + (year - first_year) / (last_year - first_year) * (right - left)

    def y_position(value):
        return bottom - value / y_max * (bottom - top)

    policy_x = x_position(2016)
    elements = [
        f'<svg xmlns="http://www.w3.org/2000/svg" role="img" '
        f'aria-labelledby="title description" viewBox="0 0 {width} {height}">',
        '<title id="title">Hungary’s electric-car fleet and green-plate parking</title>',
        (
            '<desc id="description">EU Observatory annual BEV and PHEV fleet counts '
            f'indexed to {BASE_YEAR}=100, from {first_year} through {last_year}, '
            "for Hungary and five neighboring countries. Budapest’s green-plate "
            "free-parking policy is marked at 2016. This comparison does not estimate "
            "the policy’s causal effect.</desc>"
        ),
        '<rect width="100%" height="100%" fill="#12372d"/>',
        '<text x="76" y="56" fill="#f1f7ed" font-family="Arial, sans-serif" '
        'font-size="28" font-weight="700">Hungary’s EV fleet after green-plate parking?</text>',
        '<text x="78" y="87" fill="#c4d9c7" font-family="Arial, sans-serif" '
        'font-size="15">BEV + PHEV fleet, indexed to 2015 = 100 · Hungary and regional peers</text>',
        '<text x="78" y="114" fill="#c4d9c7" font-family="Arial, sans-serif" '
        'font-size="13">Fleet growth is not evidence that parking benefits caused people to buy EVs.</text>',
        f'<rect x="{left}" y="{top}" width="{right - left}" height="{bottom - top}" '
        'fill="#1d493a" stroke="#396b53" stroke-width="1"/>',
    ]

    for value in range(0, y_max + 1, 100):
        y = y_position(value)
        elements.extend(
            [
                f'<line x1="{left}" y1="{y:.2f}" x2="{right}" y2="{y:.2f}" '
                'stroke="#396b53" stroke-width="1"/>',
                f'<text x="{left - 12}" y="{y + 5:.2f}" text-anchor="end" '
                'fill="#c4d9c7" font-family="Arial, sans-serif" font-size="13">'
                f"{value}</text>",
            ]
        )

    elements.extend(
        [
            f'<line x1="{policy_x:.2f}" y1="{top}" x2="{policy_x:.2f}" y2="{bottom}" '
            'stroke="#f1f7ed" stroke-width="1.5" stroke-dasharray="7,6"/>',
            f'<text x="{policy_x + 9:.2f}" y="{top + 20}" fill="#f1f7ed" '
            'font-family="Arial, sans-serif" font-size="13" font-weight="700">'
            "2016 · Budapest green-plate parking</text>",
        ]
    )

    for country, values in series.items():
        points = " ".join(
            f"{x_position(year):.2f},{y_position(index):.2f}" for year, index in values
        )
        stroke_width = 3.5 if country == "Hungary" else 2
        elements.append(
            f'<polyline points="{points}" fill="none" stroke="{COLORS[country]}" '
            f'stroke-width="{stroke_width}" stroke-linejoin="round" stroke-linecap="round"/>'
        )

    for index, country in enumerate(series):
        x = left + 12 + index * 170
        elements.extend(
            [
                f'<line x1="{x}" y1="665" x2="{x + 25}" y2="665" '
                f'stroke="{COLORS[country]}" stroke-width="3"/>',
                f'<text x="{x + 32}" y="670" fill="#f1f7ed" '
                'font-family="Arial, sans-serif" font-size="13">'
                f"{country}</text>",
            ]
        )

    for year in range(first_year, last_year + 1, 2):
        x = x_position(year)
        elements.append(
            f'<text x="{x:.2f}" y="{bottom + 24}" text-anchor="middle" '
            'fill="#c4d9c7" font-family="Arial, sans-serif" font-size="12">'
            f"{year}</text>"
        )
    elements.extend(
        [
            '<text x="80" y="704" fill="#c4d9c7" font-family="Arial, sans-serif" '
            'font-size="12">Source: European Alternative Fuels Observatory. '
            "Index compares growth from each country's own 2015 fleet; 2026 partial "
            "data excluded.</text>",
            "</svg>",
        ]
    )
    return "\n".join(elements)


def main():
    rows = fetch_all_rows()
    save_csv(rows)
    CHART_PATH.write_text(render_svg(rows), encoding="utf-8")
    print(f"Saved {len(rows):,} country-year-fuel observations to {DATA_PATH}.")
    print(f"Saved chart to {CHART_PATH}.")
    print(summary_statistics(rows))


if __name__ == "__main__":
    main()
