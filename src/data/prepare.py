"""Rebuild the approved OWID cohort without writing to the raw snapshot.

Run from the repository root: .venv/bin/python -m src.data.prepare
"""

import csv
import hashlib
import json
import math
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
NUMERIC_UNITS = {
    "population": "people",
    "gdp": "international-$ in 2011 prices ($)",
    "co2": "million tonnes (Mt)",
    "consumption_co2": "million tonnes (Mt)",
    "co2_per_capita": "tonnes per person (t/person)",
    "consumption_co2_per_capita": "tonnes per person (t/person)",
    "coal_co2": "million tonnes (Mt)",
    "oil_co2": "million tonnes (Mt)",
    "gas_co2": "million tonnes (Mt)",
}
FUEL_COLUMNS = ["coal_co2", "oil_co2", "gas_co2"]
SOURCE_COLUMNS = FUEL_COLUMNS + ["other_fossil_industrial_co2"]
FLAGS = ["source_row_available", "q1_observation_available", "q2_pair_available",
         "q3_available", "q4_breakdown_available", "q4_shares_available"]


def sha256(path: Path) -> str:
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def verify_snapshot(raw: Path, selection: dict) -> dict:
    """Verify the pinned data/codebook and local permission bits; never chmod here."""
    if raw.stat().st_mode & 0o222:
        raise ValueError(f"Raw directory must be read-only: {raw}")
    for path in raw.iterdir():
        if path.is_symlink() or not path.is_file() or path.stat().st_mode & 0o222:
            raise ValueError(f"Raw entry must be a read-only regular file: {path}")
    provenance = json.loads((raw / "source.json").read_text())
    records = {entry["file"]: entry for entry in provenance["files"]}
    hashes = {}
    for name in ("owid-co2-data.csv", "owid-co2-codebook.csv"):
        path = raw / name
        hashes[name] = sha256(path)
        if hashes[name] != records[name]["sha256"] or path.stat().st_size != records[name]["bytes"]:
            raise ValueError(f"Source integrity check failed: {name}")
    if hashes["owid-co2-data.csv"] != selection["dataset_sha256"]:
        raise ValueError("Snapshot differs from approved cohort selection")
    return hashes


def validate_units(codebook: Path) -> dict:
    with codebook.open(newline="") as stream:
        definitions = {row["column"]: row for row in csv.DictReader(stream)}
    for column, expected in NUMERIC_UNITS.items():
        if column not in definitions or definitions[column]["unit"] != expected:
            raise ValueError(f"Missing or unexpected codebook unit: {column}")
    return {column: definitions[column] for column in NUMERIC_UNITS}


def prepare_table(raw: pd.DataFrame, selection: dict) -> pd.DataFrame:
    """Keep the frozen cohort and approved years, then calculate annual measures."""
    required = ["iso_code", "country", "year", *NUMERIC_UNITS]
    if missing := set(required) - set(raw.columns):
        raise ValueError(f"Missing source columns: {sorted(missing)}")
    countries = selection["countries"]
    codes = [item["iso_code"] for item in countries]
    if len(codes) != len(set(codes)) or len(codes) != selection["selection"]["size"]:
        raise ValueError("Invalid fixed cohort configuration")
    table = raw.loc[raw.iso_code.isin(codes), required].copy()
    for column in ["year", *NUMERIC_UNITS]:
        table[column] = pd.to_numeric(table[column], errors="raise")
        if not table[column].dropna().map(math.isfinite).all():
            raise ValueError(f"Non-finite source values: {column}")
    if table.year.isna().any() or table.year.mod(1).ne(0).any():
        raise ValueError("Years must be non-missing integers")
    table["year"] = table.year.astype(int)
    if table.duplicated(["iso_code", "year"]).any():
        raise ValueError("Duplicate source country-year keys")
    start = selection["default_period"]["start_year"]
    table = table.loc[table.year.ge(start)].copy()
    if table.empty or table.year.max() < selection["default_period"]["end_year"]:
        raise ValueError("Snapshot does not cover the default period")
    for item in countries:
        group = table.loc[table.iso_code.eq(item["iso_code"])]
        if group.empty or not group.country.eq(item["country"]).all():
            raise ValueError(f"Country identity mismatch: {item['iso_code']}")
        reference = group.loc[group.year.eq(selection["selection"]["reference_year"]), "co2"]
        if len(reference) != 1 or not math.isclose(reference.iloc[0], item["reference_co2_mt"], rel_tol=1e-12):
            raise ValueError(f"Frozen ranking value mismatch: {item['iso_code']}")
    for column in NUMERIC_UNITS:
        if table[column].dropna().lt(0).any():
            raise ValueError(f"Negative input: {column}")
    for column in ("population", "gdp"):
        if table[column].dropna().eq(0).any():
            raise ValueError(f"Non-positive denominator/baseline: {column}")

    table["source_row_available"] = True
    grid = pd.MultiIndex.from_product(
        [codes, range(start, int(table.year.max()) + 1)], names=["iso_code", "year"]
    )
    table = table.set_index(["iso_code", "year"]).reindex(grid).reset_index()
    # Identity labels are configuration, not imputed analytical observations.
    table["country"] = table.iso_code.map({c["iso_code"]: c["country"] for c in countries})
    table["selection_rank"] = table.iso_code.map({c["iso_code"]: c["selection_rank"] for c in countries})
    table["source_row_available"] = table.source_row_available.eq(True)
    table["q1_observation_available"] = table[["gdp", "co2"]].notna().all(axis=1)
    table["q2_pair_available"] = table[["co2", "consumption_co2"]].notna().all(axis=1)
    table["q3_available"] = table[["co2", "co2_per_capita"]].notna().all(axis=1)
    table["accounting_gap_mt"] = (table.consumption_co2 - table.co2).where(table.q2_pair_available)
    table["q4_breakdown_available"] = table[["co2", *FUEL_COLUMNS]].notna().all(axis=1)
    residual = table.co2 - table[FUEL_COLUMNS].sum(axis=1, min_count=3)
    if residual.dropna().lt(0).any():
        bad = table.loc[residual.lt(0), ["iso_code", "year"]].to_dict("records")
        raise ValueError(f"Negative derived source residual; investigate: {bad[:10]}")
    table["other_fossil_industrial_co2"] = residual.where(table.q4_breakdown_available)
    table["q4_shares_available"] = table.q4_breakdown_available & table.co2.gt(0)
    for column in SOURCE_COLUMNS:
        table[f"{column}_share_pct"] = (100 * table[column] / table.co2).where(table.q4_shares_available)
    return table


def validate_table(table: pd.DataFrame, selection: dict) -> dict:
    """Fail consequential inconsistencies and describe actual per-view coverage."""
    if table.duplicated(["iso_code", "year"]).any():
        raise ValueError("Duplicate prepared country-year keys")
    source_sum = table[SOURCE_COLUMNS].sum(axis=1, min_count=4)
    if not (source_sum - table.co2).dropna().abs().le(1e-6).all():
        raise ValueError("Source components do not reconcile to total")
    shares = table[[f"{column}_share_pct" for column in SOURCE_COLUMNS]].sum(axis=1, min_count=4)
    if not (shares - 100).dropna().abs().le(1e-9).all():
        raise ValueError("Source shares do not sum to 100%")
    for total, per_capita in [("co2", "co2_per_capita"), ("consumption_co2", "consumption_co2_per_capita")]:
        matched = table[[total, per_capita, "population"]].dropna()
        expected = matched[total] * 1e6 / matched.population
        if not (expected - matched[per_capita]).abs().le(1e-6 + expected.abs() * 0.001).all():
            raise ValueError(f"Published per-capita reconciliation failed: {per_capita}")
    years = table.groupby("year", sort=True)
    start, end = (selection["default_period"][key] for key in ("start_year", "end_year"))
    default = table.loc[table.year.between(start, end)]
    return {
        "status": "passed", "rows": len(table), "countries": table.iso_code.nunique(),
        "years": [int(table.year.min()), int(table.year.max())], "default_period_rows": len(default),
        "checks": ["snapshot hashes and read-only modes before/after", "required columns and codebook units",
                   "fixed cohort identity and reference values", "unique country-year keys",
                   "finite/nonnegative observations; positive GDP/population", "no negative source residuals",
                   "four sources reconcile to total", "shares reconcile to 100%",
                   "published territorial/consumption per-capita reconciliation"],
        "missing_observations": {c: int(table[c].isna().sum()) for c in NUMERIC_UNITS},
        "default_period_missing": {c: int(default[c].isna().sum()) for c in NUMERIC_UNITS},
        "availability_by_year": {str(year): {f: int(group[f].sum()) for f in FLAGS} for year, group in years},
        "missing_by_country": {iso: {c: int(g[c].isna().sum()) for c in NUMERIC_UNITS}
                               for iso, g in table.groupby("iso_code", sort=True)},
        "minimum_derived_residual_mt": float(table.other_fossil_industrial_co2.min()),
        "excluded_entities": "All entities outside the fixed configuration cohort; no metric/year reranking.",
    }


def _safe_output(path: Path, raw: Path) -> Path:
    resolved, protected = path.resolve(), raw.resolve()
    if resolved == protected or protected in resolved.parents or resolved in protected.parents:
        raise ValueError(f"Output overlaps protected raw directory: {path}")
    return resolved


def rebuild(root: Path = PROJECT_ROOT) -> dict:
    root = root.resolve()
    raw = root / "data" / "raw" / "owid"
    selection = json.loads((root / "config" / "analysis_selection.json").read_text())
    hashes = verify_snapshot(raw, selection)
    definitions = validate_units(raw / "owid-co2-codebook.csv")
    table = prepare_table(pd.read_csv(raw / "owid-co2-data.csv"), selection)
    report = validate_table(table, selection)
    csv_path = _safe_output(root / "data" / "processed" / "country_year.csv", raw)
    metadata_path = _safe_output(root / "data" / "processed" / "metadata.json", raw)
    report_path = _safe_output(root / "outputs" / "data-validation.json", raw)
    for path in (csv_path, metadata_path, report_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(csv_path, index=False, na_rep="", lineterminator="\n")
    if verify_snapshot(raw, selection) != hashes:
        raise ValueError("Raw snapshot changed during preparation")
    report["raw_sha256"] = hashes
    report["prepared_csv_sha256"] = sha256(csv_path)
    sources = json.loads((root / "config" / "data_sources.json").read_text())
    metadata = {
        "schema_version": 1, "decisions": ["D010", "D012", "D013", "D014"],
        "raw_sha256": hashes, "prepared_csv_sha256": report["prepared_csv_sha256"],
        "selection_config_sha256": sha256(root / "config" / "analysis_selection.json"),
        "default_period": selection["default_period"], "frozen_cohort": selection["countries"],
        "published_columns": definitions, "sources_and_release_attribution": sources,
        "derived_columns": {
            "accounting_gap_mt": "consumption_co2 - co2; million tonnes CO2; matched observations only",
            "other_fossil_industrial_co2": "co2 - coal_co2 - oil_co2 - gas_co2; million tonnes CO2; derived, not other_industry_co2",
            "*_share_pct": "100 * component / co2; percent of fossil/industrial CO2, not energy; complete breakdown and positive total required",
            "q1_observation_available": "GDP and territorial CO2 observed; endpoint eligibility checked separately at query time",
            "q2_pair_available": "territorial and consumption totals observed in same country/year",
            "q3_available": "total and per-capita territorial CO2 observed in same country/year",
            "q4_breakdown_available": "total, coal, oil and gas observed in same country/year",
            "q4_shares_available": "complete breakdown and positive territorial CO2 total",
            "source_row_available": "original source has this country/year; false for inserted gap rows",
        },
        "missing_values": "Empty CSV fields are missing, never zero-filled, carried, interpolated or extrapolated.",
        "period_measures": "Use src/data/measures.py with selected endpoints; no stored fixed-baseline classifications.",
        "rebuild_command": ".venv/bin/python -m src.data.prepare",
    }
    for path, value in ((metadata_path, metadata), (report_path, report)):
        path.write_text(json.dumps(value, indent=2, allow_nan=False) + "\n")
    return report


if __name__ == "__main__":
    result = rebuild()
    print(f"Prepared {result['rows']} rows for {result['countries']} countries; validation passed.")
    print("Data: data/processed/country_year.csv; checks: outputs/data-validation.json")
