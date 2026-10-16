# Hungary's hyperinflation, month by month

![Monthly inflation rates implied by Hungary's published price index in 1946, with the period of billion-pengő banknotes highlighted.](./hungary_hyperinflation.svg)

## Executive summary

Hungary's post-war hyperinflation peaked in 1946. This chart shows the
percentage increase implied by seven consecutive published index
observations from January through July 1946. Rates are calculated as
`(ending level / starting level - 1) × 100`. The final observation, from
1–31 July, is a rise of about **26.7 trillion percent**.

The chart highlights the period from **13 May 1946**, when the first
one-billion-pengő banknote was issued, to the end of July. Larger denominations
followed rapidly. Hanke and Krus report a separate peak monthly inflation
estimate of **4.19 × 10¹⁶%**, with prices doubling in about 15 hours. That
expert peak statistic uses a different method/price series, so it is shown as
context rather than mixed into the plotted observations.

## How to read the chart

- Each point is the percentage increase between the two dates shown by its
  adjacent monthly interval. Most periods run from the first day of one month
  to the first day of the next. The last interval is 1–31 July.
- The vertical axis is logarithmic. Each step is a tenfold increase; this
  keeps the earlier rates visible alongside the enormous July value.
- The shaded period starts on the documented issue date of the first
  one-billion-pengő banknote. It marks the banknote chronology, not a separate
  inflation measure.
- Hyperinflation began in August 1945, but this chart's monthly source
  observations begin in January 1946. It does not invent monthly rates for
  1945.

## About the data

The historical source's dated series is called the **adópengő index**. The
adópengő was a temporary accounting unit introduced in 1946; the index
expressed pengő values per adópengő. Rather than make that unfamiliar index
the chart, the CSV keeps its dated start and end values and the script
converts consecutive values into percentage changes. This is a historical
inflation proxy, not a modern official monthly CPI series. The number of
available observations is limited, and the rates are changes implied by the
published dates.

The banknote timeline is separate context. A one-billion-pengő note was
issued on 13 May 1946; later high denominations included milpengő and
b.-pengő notes. The chart shades the period beginning with the first
one-billion-pengő issue rather than implying that every later note had the
same unit.

## Reproducibility

```bash
python "3. ora/hungary_inflation_visualization.py"
python -m unittest discover -s "3. ora" -p "test_*.py" -v
```

The SVG and chart are generated using Python's standard library.

## References

1. Garami, Erika. “Hyperinflation in numbers” (“A hiperinfláció
   számokban”). *Pénzportál*, 1 November 2006; archived 21 July 2011.
   Source for the dated index values used to calculate the monthly rates.
   <https://web.archive.org/web/20110721085706/http://www.penzportal.hu/index.cgi?r=&v=&l=&feaz=75a8wc4sitder9&mf=&p=12732>
2. “Hungarian adópengő.” *Wikipedia*. Dated price-index table reproduced from
   Pénzportál; used here as a source for the dated inputs, not as the chart's
   subject.
   <https://en.wikipedia.org/wiki/Hungarian_ad%C3%B3peng%C5%91>
3. “Paper money of the Hungarian pengő.” *Wikipedia*. 1945–46 banknote issue
   table, including the one-billion-pengő note's 13 May 1946 issue date.
   <https://en.wikipedia.org/wiki/Paper_money_of_the_Hungarian_peng%C5%91>
4. Hanke, Steve H., and Nicholas Krus. *World Hyperinflations*. Cato
   Institute. Source for the separately reported peak monthly inflation rate
   and approximate price-doubling time.
   <https://www.cato.org/working-paper/world-hyperinflations>
   <https://object.cato.org/sites/cato.org/files/pubs/pdf/hanke-krus-hyperinflation-table-may-2013.pdf>
