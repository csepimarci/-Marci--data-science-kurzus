# The EV leaders are moving ahead: who electrified new car sales fastest?

![Line chart comparing EV shares of new passenger-car sales for the eight leading countries through 2025, with the world average and selected subsidy-policy milestones.](./global_ev_adoption.svg)

*Figure 1. Countries are ranked by their 2025 share of new passenger-car sales
that were electric. Policy cards show selected incentive changes, not proven
causes of the adoption trends.*

## Executive summary

- Norway led the countries in the IEA series in 2025: **97%** of new passenger
  cars sold were electric. Denmark followed at **71%**, Nepal at **68%**, and
  Iceland at **62%**.
- The global share was **25%**. China reached **53%**, Sweden **61%**, the
  Netherlands **58%**, and Finland **57%**.
- Norway's EV sales share rose from **22% in 2015** to **97% in 2025**. China's
  climbed from **1.1% to 53%** over the same period.
- The policy panel highlights selected purchase grants, tax relief and
  incentive changes that overlapped with these market shifts. The chart cannot
  show that any one policy caused a change.

## The story behind the data

Electric-car adoption accelerated in very different markets. Norway is the
clearest high-share leader: electric cars rose from roughly one in five new
sales in 2015 to nearly all new sales in 2025. Several other European markets
also passed the halfway mark. China reached 53% in 2025, making it a major
electric-car market as well as a fast-growing one.

Nepal is a striking recent entrant in the top group. Its reported share rose
from **29% in 2022** to **74% in 2024**, then eased to **68% in 2025**. That
variation is a reminder that a high sales share can change quickly and that a
single year's ranking does not tell the whole story.

The policy milestones offer useful context for interpreting the lines. The
Netherlands' SEPP program supported private purchases of new and used electric
cars; Sweden withdrew its climate bonus in November 2022; China ended its
national purchase-subsidy program after 2022 but extended purchase-tax relief;
and Norway narrowed its VAT exemption for more expensive EVs in 2023. These
policies can change the cost of choosing an EV, but their timing alone does not
measure their effect.

## Reading the visualization

- Each line shows **EV sales share**: electric vehicles as a percentage of new
  passenger-car sales in that year. In this IEA series, EV includes
  battery-electric and plug-in hybrid cars.
- The eight country lines are selected by their reported share in the latest
  year, **2025**. The right-hand list gives their 2025 ranking and values.
- The dashed line is the IEA world average. The vertical scale is a percentage
  from 0 to 100.
- A missing early observation is left blank rather than interpolated. In
  particular, the plotted Nepal series starts when IEA observations are
  available.
- Policy cards are selected examples, not a complete inventory of each
  country's support. They distinguish direct purchase grants from tax relief
  and policy withdrawals.

## Interpretation and limitations

This is a measure of the **flow of new car sales**, not the percentage of all
cars on the road that are electric and not the total number of EVs sold. Small
markets can lead on share while larger markets sell many more vehicles in
absolute terms. For that reason, China's 53% should not be read as a smaller
market than Norway's 97% in vehicle count.

The policy dates are context, not a causal analysis. Adoption is also shaped by
vehicle prices and availability, charging networks, fuel prices, income,
taxation, regulation and consumer preferences. Policies may be introduced,
changed or withdrawn alongside several of these factors. The chart cannot
isolate a subsidy's contribution or show what would have happened without it.

The 2026 release provides historical observations through 2025. Country
coverage and the earliest available year differ, and later editions may revise
historical values. The checked-in CSV makes this chart reproducible against the
same snapshot.

## Data and reproducibility

The adoption series is the IEA's *Global EV Data Explorer*, published with the
2026 *Global EV Outlook*. The local CSV contains the IEA-derived historical
passenger-car observations, including the world series, used to create the
figure. It is a filtered snapshot of the publicly shared 2026 IEA sales-share
series; its header records the source and attribution.

From the repository root:

```bash
python "3. ora/global_ev_adoption.py"
python -m unittest discover -s "3. ora" -p "test_*.py" -v
```

The chart is saved to `3. ora/global_ev_adoption.svg`. The script reads the
checked-in CSV and needs no network access.

## References

### EV adoption data

1. International Energy Agency (IEA). *Global EV Outlook 2026: Global EV data*.
   <https://www.iea.org/data-and-statistics/data-product/global-ev-outlook-2026#global-ev-data>
2. IEA. *Global EV Data Explorer*. Historical country sales-share series and
   data definitions. <https://www.iea.org/data-and-statistics/data-tools/global-ev-data-explorer>
3. Environment Dashboard. *Electric share of new vehicle sales*. CC BY 4.0
   derived series used as the snapshot intermediary for this local extract.
   <https://environmentdashboard.org/data/ev/iea/sales-share>

### Policy context

4. IEA. *Global EV Policy Explorer*. Country policy records for Norway, Sweden
   and China. <https://www.iea.org/policies>
5. Netherlands Enterprise Agency (RVO). *Subsidieregeling Elektrische
   Personenauto's Particulieren (SEPP)*. Scheme timing and eligibility,
   including the final application date in December 2024.
   <https://www.rvo.nl/subsidies-financiering/sepp>
