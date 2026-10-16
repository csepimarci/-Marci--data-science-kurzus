# Hungary's prices before and after the hyperinflation

![Two separate logarithmic views: historical price-level checkpoints through July 1946 and Hungary's forint-era consumer-price index from 1972 to 2025.](./hungary_hyperinflation.svg)

## What the chart shows

The figure puts the prewar baseline, the hyperinflation, and the much longer
forint era in one clean overview, while keeping unlike series separate:

- **Historical panel, 1938–July 1946:** selected price-level multiples
  relative to 1938 = 1. The final point is about 399,623 quadrillion times
  the 1938 level.
- **Forint-era panel, 1972–2025:** the annual Hungarian consumer price index
  (CPI), rebased by the World Bank to 2010 = 100. It tracks consumer prices
  in the forint era. In 2025 the index is about 192, meaning the measured
  consumer basket cost about 1.92 times as much as in 2010.

Both panels use logarithmic vertical scales, but their reference bases and
underlying historical series are different. The panels are not joined or
directly compared. The figure marks the 1945–46 catastrophe and the August
1946 introduction of the forint; it does not pretend the currency reform left
one seamless nominal-price series.

## Why the forint-era series starts in 1972

The World Bank's annual CPI index used here has observations beginning in
1972, not at the forint's introduction in 1946. The gap from the end of the
hyperinflation to 1972 is therefore a **source-coverage gap**, not evidence
that prices were unchanged. The historical bread-price compilation has a
small number of forint-per-kilogram observations from 1946–1952; those are
shown separately in the [companion bread-price analysis](./homework_hungary_bread_prices.md).

The 1938–46 historical series is also a small set of published checkpoints,
not annual or monthly coverage. Its 1938 value is the reference base. The
later values come from a historical table that reports multiples of the
1938 price level. No values have been invented to fill the gaps.

The source-backed prewar baseline begins in 1938; the sources used here do
not provide a comparable annual CPI series further back. That is why the
chart starts its historical section at 1938 rather than adding unsupported
earlier estimates.

## Data and reproducibility

- `data/hungary_price_level_1938_base.csv` contains the 1938 base and four
  historical price-level observations through July 1946.
- `data/hungary_forint_cpi.csv` contains 54 annual CPI observations from
  1972 through 2025 (World Bank indicator `FP.CPI.TOTL`, 2010 = 100).
- `hungary_inflation_visualization.py` validates the inputs and generates the
  SVG using Python's standard library.

```bash
python "3. ora/hungary_inflation_visualization.py"
python -m unittest discover -s "3. ora" -p "test_*.py" -v
```

## References

1. Garami, Erika. “Hyperinflation in numbers” (“A hiperinfláció
   számokban”). *Pénzportál*, 1 November 2006; archived 21 July 2011.
   Source for the historical price-level multiples relative to 1938.
   <https://web.archive.org/web/20110721085706/http://www.penzportal.hu/index.cgi?r=&v=&l=&feaz=75a8wc4sitder9&mf=&p=12732>
2. World Bank. World Development Indicators, “Consumer price index
   (2010 = 100),” Hungary, indicator `FP.CPI.TOTL`.
   <https://api.worldbank.org/v2/country/HUN/indicator/FP.CPI.TOTL?format=json&per_page=100>
3. Hanke, Steve H., and Nicholas Krus. *World Hyperinflations*. Cato
   Institute. Source for the separately reported July 1946 peak monthly
   inflation rate and approximate price-doubling time.
   <https://www.cato.org/working-paper/world-hyperinflations>
   <https://object.cato.org/sites/cato.org/files/pubs/pdf/hanke-krus-hyperinflation-table-may-2013.pdf>
