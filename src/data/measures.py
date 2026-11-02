"""Approved Q1/Q3 measures; no imputation or substitution of observation years."""

import math

import pandas as pd


def _period(start_year: int, end_year: int) -> None:
    if start_year >= end_year:
        raise ValueError("Select an end year later than the start year")


def percentage_change(start: float, end: float) -> float:
    """A positive baseline is required. Missing/invalid endpoints stay missing."""
    if pd.isna(start) or pd.isna(end):
        return float("nan")
    if not math.isfinite(start) or not math.isfinite(end) or start <= 0 or end < 0:
        return float("nan")
    return 100 * (end - start) / start


def decoupling_label(gdp_change: float, co2_change: float) -> str:
    """Descriptive labels from unrounded values, with no significance threshold."""
    if not math.isfinite(gdp_change) or not math.isfinite(co2_change):
        return "Unavailable"
    if gdp_change <= 0:
        return "GDP not growing"
    if co2_change < 0:
        return "Absolute decoupling"
    if co2_change == 0:
        return "GDP growth with flat emissions"
    if co2_change < gdp_change:
        return "Relative decoupling"
    if co2_change == gdp_change:
        return "Equal GDP and emissions growth"
    return "Emissions growing faster than GDP"


def endpoint_changes(table: pd.DataFrame, start_year: int, end_year: int) -> pd.DataFrame:
    """Keep every cohort member, including those without both exact endpoints."""
    _period(start_year, end_year)
    if table.duplicated(["iso_code", "year"]).any():
        raise ValueError("Duplicate country-year keys")
    rows = []
    for iso, group in table.groupby("iso_code", sort=False):
        yearly = group.set_index("year")
        row = {"iso_code": iso, "country": group.iloc[0]["country"],
               "start_year": start_year, "end_year": end_year}
        for metric in ("gdp", "co2"):
            start = yearly.at[start_year, metric] if start_year in yearly.index else float("nan")
            end = yearly.at[end_year, metric] if end_year in yearly.index else float("nan")
            row[f"{metric}_change_pct"] = percentage_change(start, end)
        row["q1_available"] = all(math.isfinite(row[f"{m}_change_pct"]) for m in ("gdp", "co2"))
        row["decoupling"] = decoupling_label(row["gdp_change_pct"], row["co2_change_pct"])
        rows.append(row)
    return pd.DataFrame(rows)


def indexed_trends(table: pd.DataFrame, metric: str, start_year: int, end_year: int) -> pd.DataFrame:
    """Create an explicit year grid; absent/intermediate observations remain gaps."""
    _period(start_year, end_year)
    if table.duplicated(["iso_code", "year"]).any():
        raise ValueError("Duplicate country-year keys")
    rows = []
    for iso, group in table.groupby("iso_code", sort=False):
        series = group.set_index("year")[metric].reindex(range(start_year, end_year + 1))
        baseline = series.loc[start_year]
        valid_base = pd.notna(baseline) and math.isfinite(baseline) and baseline > 0
        for year, value in series.items():
            valid = valid_base and pd.notna(value) and math.isfinite(value) and value >= 0
            rows.append({"iso_code": iso, "country": group.iloc[0]["country"],
                         "year": year, "metric": metric, "baseline_year": start_year,
                         "index": 100 * value / baseline if valid else float("nan")})
    return pd.DataFrame(rows)


def matched_rankings(table: pd.DataFrame, year: int) -> pd.DataFrame:
    """Q3: both rankings use the same eligible cohort and exact selected year.

    Missing members remain in the result with null ranks. Ties share a rank.
    """
    if table.duplicated(["iso_code", "year"]).any():
        raise ValueError("Duplicate country-year keys")
    cohort = table[["iso_code", "country"]].drop_duplicates("iso_code")
    snapshot = table.loc[table.year.eq(year), ["iso_code", "co2", "co2_per_capita"]]
    result = cohort.merge(snapshot, on="iso_code", how="left", validate="one_to_one")
    result["year"] = year
    result["q3_available"] = result[["co2", "co2_per_capita"]].notna().all(axis=1)
    for metric in ("co2", "co2_per_capita"):
        result[f"{metric}_rank"] = result[metric].where(result.q3_available).rank(
            ascending=False, method="min"
        ).astype("Int64")
    return result
