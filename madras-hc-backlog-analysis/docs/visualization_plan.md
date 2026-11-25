# Visualization plan

Charts to build in the next iteration. Data ranges refer to `workbook/Madras_HC_KPI_Workbook.xlsx` (also on the `Viz_Plan` sheet) and the CSVs in `data/processed/`.

| # | Visualization | Chart type | Data | Message |
|---|---|---|---|---|
| 1 | Filed vs disposed vs closing, by bench and side | Clustered column | `unit_kpis.csv`; sheet Headline | Both civil units cleared more than they received; Madurai criminal is the exception |
| 2 | Clearance rate by category with a 100% line | Horizontal bar + reference line | `category_kpis.csv`, six rows with `in_report = True` | Writs and second appeals clear well; criminal appeals and tax cases sit near 50% |
| 3 | Pending stock by category | Sorted bar (Pareto) with cumulative share | `category_kpis.csv`, civil rows | Writ petitions are about half of civil pending; the long tail is where ageing hides |
| 4 | Volume vs flow map | Scatter or bubble: x = pending, y = clearance rate, size = disposal-years | `category_kpis.csv`, six focus rows | Biggest stock is healthy; risky stock is small and slow. This is the core insight chart |
| 5 | Disposal-years by focus category | Bar | `category_kpis.csv`, `disposal_years` | Tax cases and second appeals take longest to clear at the 2023 rate |
| 6 | NJDG pendency trend, 2022 to 2024 | Line | Sheet NJDG_Trend | Pendency is edging down, not collapsing |
| 7 | Disposals needed: 2023 vs stabilise vs 5-year clearance | Grouped bar | `effort_scenarios.csv` | Slow categories need roughly double to triple current throughput |
| 8 | Roadmap and WBS timeline | Gantt | Report section 7 | Visible outputs within a 6-month engagement |

## Design notes

- Put the finding in each chart title (for example, "Criminal appeals clear only 53% of what is filed").
- Draw a 100% reference line on every clearance-rate chart.
- Label the data basis (Statistical Handbook, 2023) in a footnote. Do not plot NJDG and Handbook levels on the same axis.
- Keep one colour for "healthy" and one for "intervene" across all charts.
- Suggested tools: Google Sheets or Excel for 1 to 7, a simple Gantt template or Python (matplotlib) for 8. Power BI or Tableau also work if you want a dashboard.
