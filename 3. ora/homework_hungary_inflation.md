# Hungary's 1946 hyperinflation: how fast did the index rise?

![Hungary's 1946 adópengő index rising from 1 in January to 2 × 10²¹ in July on a logarithmic scale.](./hungary_hyperinflation.svg)

## Executive summary

Hungary experienced one of history's most extreme hyperinflations in 1945–46.
This chart follows the **adópengő index** through eight published observations
from 1 January to 31 July 1946. The reported index rose from 1 to
2,000,000,000,000,000,000,000 (2 × 10²¹).

The vertical axis is logarithmic: each equal step represents a tenfold
increase. A linear axis would make the early values almost invisible. The
line connects the eight source observations as a visual guide; it does not
invent daily data between them. Hanke and Krus's separate estimate of the
peak monthly inflation rate is highlighted above the chart, not plotted as
part of the index series.

## Reading the chart

- The horizontal axis covers January–July 1946; every dot is a value reported
  in the source table.
- The vertical axis uses powers of ten. The index went from 1 to 2 × 10²¹,
  so this extraordinary change can be seen without compressing the early
  observations to the bottom of the chart.
- The source labels the series “Adópengő index, 1946 (pengős per adópengő).”
  It is an index/currency ratio, not a direct measurement of the price of
  bread or a modern consumer-price index.
- The callout reports Hanke and Krus's peak monthly price-inflation estimate
  of 4.19 × 10¹⁶%, with prices doubling in about 15 hours. This is a separate
  statistic and uses a different measure.

## What about bread?

The available historical retail-price table does not provide bread prices
through the peak of hyperinflation. The companion
[bread-price analysis](./homework_hungary_bread_prices.md) shows the actual
documented bread-price observations before and after the crisis, and keeps
them separate from this index. That distinction avoids presenting the
general index as if it were a bread-price series.

## Data and reproducibility

The CSV contains the eight dated observations transcribed from the
Adópengő-index table cited below. Values are not interpolated in the CSV.

```bash
python "3. ora/hungary_inflation_visualization.py"
python -m unittest discover -s "3. ora" -p "test_*.py" -v
```

The chart is generated as an SVG using Python's standard library.

## References

1. Garami, Erika. “Hyperinflation in numbers” (“A hiperinfláció
   számokban”). *Pénzportál*, 1 November 2006; archived 21 July 2011.
   The cited table reports the adópengő index values.
   <https://web.archive.org/web/20110721085706/http://www.penzportal.hu/index.cgi?r=&v=&l=&feaz=75a8wc4sitder9&mf=&p=12732>
2. “Hungarian adópengő.” *Wikipedia*, table “Adópengő index, 1946
   (pengős per adópengő),” citing Pénzportál.
   <https://en.wikipedia.org/wiki/Hungarian_ad%C3%B3peng%C5%91>
3. Hanke, Steve H., and Nicholas Krus. *World Hyperinflations*. Cato
   Institute. Source for the peak monthly inflation estimate and approximate
   price-doubling time.
   <https://www.cato.org/working-paper/world-hyperinflations>
   <https://object.cato.org/sites/cato.org/files/pubs/pdf/hanke-krus-hyperinflation-table-may-2013.pdf>
