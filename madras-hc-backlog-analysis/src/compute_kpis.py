"""Compute backlog KPIs for the Madras High Court from the 2023 case-flow data.

Reads  data/raw/hc_2023_case_flow.csv
Writes data/processed/unit_kpis.csv, category_kpis.csv, effort_scenarios.csv

Definitions
-----------
clearance_rate  = disposed / filed
net_change      = closing / opening - 1
disposal_years  = closing / disposed   (proxy: years to clear the stock with no
                                        new filings at the 2023 disposal rate;
                                        NOT the age of cases)
"""
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "hc_2023_case_flow.csv"
OUT = ROOT / "data" / "processed"
HORIZON_YEARS = 5          # years to clear stock in the effort scenarios
MIN_STOCK_FLAG = 1000      # categories below this pending count are 'Small stock'
FOCUS = ["Writ Petitions", "Second Appeals", "First Appeals",
         "Criminal Appeals", "Tax Cases", "Arbitration - Interim Relief"]
SCENARIO_CATS = ["Criminal Appeals", "Tax Cases", "First Appeals", "Second Appeals"]


def add_kpis(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["clearance_rate"] = (df["disposed"] / df["filed"]).where(df["filed"] > 0)
    df["net_change"] = (df["closing_published"] / df["opening"] - 1).where(df["opening"] > 0)
    df["disposal_years"] = (df["closing_published"] / df["disposed"]).where(df["disposed"] > 0)
    return df


def status(row) -> str:
    if row["closing_published"] < MIN_STOCK_FLAG:
        return "Small stock"
    cr, dy = row["clearance_rate"], row["disposal_years"]
    if pd.isna(cr):
        return "No new filings: legacy"
    if cr < 0.95:
        return "Stock growing: intervene"
    if cr < 1:
        return "Flat: monitor"
    if pd.notna(dy) and dy >= 5:
        return "Large legacy stock: accelerate"
    return "Healthy: sustain"


def main() -> None:
    raw = pd.read_csv(RAW)
    cols = ["opening", "filed", "disposed", "closing_published"]
    OUT.mkdir(parents=True, exist_ok=True)

    # 1. Headline by bench and side (+ total)
    units = raw.groupby(["bench", "side"], sort=False)[cols].sum().reset_index()
    total = pd.DataFrame([{"bench": "TOTAL", "side": "", **units[cols].sum().to_dict()}])
    units = add_kpis(pd.concat([units, total], ignore_index=True))
    units.to_csv(OUT / "unit_kpis.csv", index=False)

    # 2. Category KPIs (both benches combined)
    cat = raw.groupby(["side", "category"])[cols].sum().reset_index()
    cat = add_kpis(cat)
    cat["share_of_side_pending"] = cat["closing_published"] / cat.groupby("side")["closing_published"].transform("sum")
    cat["status"] = cat.apply(status, axis=1)
    cat["in_report"] = cat["category"].isin(FOCUS)
    cat = cat.sort_values(["side", "closing_published"], ascending=[True, False])
    cat.to_csv(OUT / "category_kpis.csv", index=False)

    # 3. Effort scenarios (filings assumed constant at 2023 levels)
    eff = cat[cat["category"].isin(SCENARIO_CATS)].set_index("category").loc[SCENARIO_CATS].reset_index()
    eff = eff[["category", "filed", "disposed", "closing_published"]].rename(columns={"closing_published": "pending"})
    eff["surplus"] = eff["disposed"] - eff["filed"]
    eff["needed_to_stabilise"] = eff["filed"].where(eff["disposed"] < eff["filed"])
    eff["multiple_to_stabilise"] = eff["needed_to_stabilise"] / eff["disposed"]
    eff["needed_for_n_year_clearance"] = eff["filed"] + eff["pending"] / HORIZON_YEARS
    eff["multiple_for_n_year_clearance"] = eff["needed_for_n_year_clearance"] / eff["disposed"]
    eff["years_to_clear_at_current_surplus"] = (eff["pending"] / eff["surplus"]).where(eff["surplus"] > 0)
    eff.to_csv(OUT / "effort_scenarios.csv", index=False)

    pd.set_option("display.width", 200, "display.max_columns", 20)
    print("\nHEADLINE\n", units.round(4).to_string(index=False))
    print("\nFOCUS CATEGORIES\n", cat[cat["in_report"]].round(4).to_string(index=False))
    print("\nEFFORT SCENARIOS\n", eff.round(2).to_string(index=False))
    gap = (raw["closing_published"] - (raw["opening"] + raw["filed"] - raw["disposed"])).sum()
    print(f"\nRoll-forward gap (published closing - calculated): {gap}")


if __name__ == "__main__":
    main()
