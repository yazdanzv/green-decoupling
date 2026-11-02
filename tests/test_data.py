"""Independent small examples for consequential preparation and period measures."""

import copy
import json
import math
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from src.data.measures import (
    decoupling_label, endpoint_changes, indexed_trends, matched_rankings, percentage_change,
)
from src.data.prepare import (
    NUMERIC_UNITS, SOURCE_COLUMNS, _safe_output, prepare_table, rebuild, sha256,
    validate_table, validate_units, verify_snapshot,
)


def fixture():
    """Synthetic totals: 100 -> 80; GDP: 100 -> 150; exact, easy arithmetic."""
    selection = {
        "default_period": {"start_year": 2000, "end_year": 2002},
        "selection": {"size": 2, "reference_year": 2002},
        "countries": [
            {"iso_code": "AAA", "country": "Test A", "selection_rank": 1, "reference_co2_mt": 80},
            {"iso_code": "BBB", "country": "Test B", "selection_rank": 2, "reference_co2_mt": 40},
        ],
    }
    rows = []
    for iso, name, scale in [("AAA", "Test A", 1), ("BBB", "Test B", 0.5)]:
        for year, gdp, co2, coal, oil, gas in [(2000, 100, 100, 40, 30, 20),
                                               (2002, 150, 80, 30, 20, 10),
                                               (2003, None, 90, 35, 25, 15)]:
            rows.append({"iso_code": iso, "country": name, "year": year,
                         "gdp": gdp, "population": 1_000_000,
                         "co2": co2 * scale, "co2_per_capita": co2 * scale,
                         "consumption_co2": (co2 + 10) * scale,
                         "consumption_co2_per_capita": (co2 + 10) * scale,
                         "coal_co2": coal * scale, "oil_co2": oil * scale, "gas_co2": gas * scale})
    return pd.DataFrame(rows), selection


class MeasureTests(unittest.TestCase):
    def test_hand_calculated_changes_and_selected_baseline(self):
        raw, selection = fixture()
        table = prepare_table(raw, selection)
        changes = endpoint_changes(table, 2000, 2002).set_index("iso_code")
        self.assertEqual(changes.at["AAA", "gdp_change_pct"], 50)
        self.assertEqual(changes.at["AAA", "co2_change_pct"], -20)
        self.assertEqual(changes.at["AAA", "decoupling"], "Absolute decoupling")
        trend = indexed_trends(table, "co2", 2002, 2003).query("iso_code == 'AAA'")
        self.assertEqual(trend["index"].tolist(), [100, 112.5])
        # Absent 2001 is a gap, not zero; endpoints still work.
        trend = indexed_trends(raw, "co2", 2000, 2002).query("iso_code == 'AAA'")
        self.assertEqual(trend["index"].iloc[0], 100)
        self.assertTrue(pd.isna(trend["index"].iloc[1]))
        self.assertEqual(trend["index"].iloc[2], 80)

    def test_missing_endpoints_never_use_nearby_year(self):
        raw, _ = fixture()
        changes = endpoint_changes(raw, 2001, 2002)
        self.assertFalse(changes.q1_available.any())
        self.assertTrue(changes.gdp_change_pct.isna().all())
        self.assertEqual(changes.decoupling.tolist(), ["Unavailable"] * 2)
        self.assertTrue(indexed_trends(raw, "co2", 2001, 2003)["index"].isna().all())
        # GDP missing in 2003, while territorial emissions are still usable.
        self.assertFalse(endpoint_changes(raw, 2002, 2003).q1_available.any())

    def test_invalid_baselines_and_periods(self):
        for start, end in [(0, 10), (-1, 10), (None, 10), (10, None), (10, -1), (10, float("inf"))]:
            self.assertTrue(math.isnan(percentage_change(start, end)))
        self.assertEqual(percentage_change(10, 0), -100)
        raw, _ = fixture()
        for fn, args in [(endpoint_changes, (raw, 2002, 2002)),
                         (indexed_trends, (raw, "co2", 2003, 2000))]:
            with self.assertRaises(ValueError):
                fn(*args)

    def test_classifications_use_unrounded_values(self):
        for gdp, co2, label in [(10, 5, "Relative decoupling"),
                                (10, 0, "GDP growth with flat emissions"),
                                (0, -5, "GDP not growing"),
                                (10, 10, "Equal GDP and emissions growth"),
                                (10, 11, "Emissions growing faster than GDP"),
                                (10, -1e-10, "Absolute decoupling")]:
            self.assertEqual(decoupling_label(gdp, co2), label)

    def test_ranking_switch_uses_same_year_and_eligible_members(self):
        raw, _ = fixture()
        # One metric missing: exclude this member from BOTH rankings.
        raw.loc[raw.iso_code.eq("AAA") & raw.year.eq(2002), "co2_per_capita"] = float("nan")
        result = matched_rankings(raw, 2002).set_index("iso_code")
        self.assertTrue(pd.isna(result.at["AAA", "co2_rank"]))
        self.assertEqual(result.at["BBB", "co2_rank"], 1)
        self.assertEqual(result.at["BBB", "co2_per_capita_rank"], 1)
        self.assertFalse(matched_rankings(raw, 1999).q3_available.any())


class PreparationTests(unittest.TestCase):
    def test_accounting_sources_shares_and_explicit_grid(self):
        raw, selection = fixture()
        table = prepare_table(raw, selection)
        a = table.query("iso_code == 'AAA'").set_index("year")
        self.assertEqual(len(table), 8)
        self.assertFalse(a.at[2001, "source_row_available"])
        self.assertTrue(pd.isna(a.at[2001, "co2"]))
        self.assertEqual(a.at[2000, "accounting_gap_mt"], 10)
        self.assertEqual(a.at[2000, "other_fossil_industrial_co2"], 10)
        self.assertEqual(a.at[2000, "coal_co2_share_pct"], 40)
        self.assertEqual(a.at[2002, "other_fossil_industrial_co2_share_pct"], 25)
        self.assertTrue(pd.isna(a.at[2003, "gdp"]))
        self.assertEqual(validate_table(table, selection)["status"], "passed")

    def test_missing_inputs_invalidate_only_relevant_measures(self):
        raw, selection = fixture()
        raw.loc[0, ["gas_co2", "consumption_co2"]] = float("nan")
        a = prepare_table(raw, selection).iloc[0]
        self.assertTrue(a.q1_observation_available)
        self.assertTrue(a.q3_available)
        self.assertFalse(a.q2_pair_available)
        self.assertFalse(a.q4_breakdown_available)
        self.assertTrue(pd.isna(a.accounting_gap_mt))
        self.assertTrue(pd.isna(a.other_fossil_industrial_co2))
        self.assertTrue(pd.isna(a.coal_co2_share_pct))
        self.assertEqual(a.coal_co2, 40)  # Published observation still preserved.

    def test_negative_residual_fails_without_clamping(self):
        raw, selection = fixture()
        raw.loc[0, "coal_co2"] = 200
        with self.assertRaisesRegex(ValueError, "Negative derived source residual"):
            prepare_table(raw, selection)

    def test_zero_total_does_not_produce_shares(self):
        raw, selection = fixture()
        raw.loc[0, ["co2", "co2_per_capita", "coal_co2", "oil_co2", "gas_co2"]] = 0
        table = prepare_table(raw, selection)
        self.assertTrue(table.iloc[0].q4_breakdown_available)
        self.assertFalse(table.iloc[0].q4_shares_available)
        self.assertTrue(table.loc[0, [f"{c}_share_pct" for c in SOURCE_COLUMNS]].isna().all())

    def test_duplicate_schema_nonfinite_and_cohort_failures(self):
        raw, selection = fixture()
        variants = [pd.concat([raw, raw.iloc[[0]]]), raw.drop(columns="gdp")]
        nonfinite = raw.copy()
        nonfinite.loc[0, "gdp"] = float("inf")
        variants.append(nonfinite)
        for variant in variants:
            with self.assertRaises(ValueError):
                prepare_table(variant, selection)
        wrong_selection = copy.deepcopy(selection)
        wrong_selection["countries"][0]["reference_co2_mt"] = 999
        with self.assertRaisesRegex(ValueError, "Frozen ranking value mismatch"):
            prepare_table(raw, wrong_selection)

    def test_reconciliation_catches_wrong_published_per_capita(self):
        raw, selection = fixture()
        raw.loc[0, "co2_per_capita"] = 1
        with self.assertRaisesRegex(ValueError, "per-capita reconciliation"):
            validate_table(prepare_table(raw, selection), selection)

    def test_rebuild_is_deterministic_and_protects_inputs(self):
        raw_table, selection = fixture()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            raw = root / "data" / "raw" / "owid"
            raw.mkdir(parents=True)
            (root / "config").mkdir()
            try:
                data = raw / "owid-co2-data.csv"
                raw_table.to_csv(data, index=False)
                definitions = pd.DataFrame([{"column": c, "unit": u, "source": "Synthetic test"}
                                            for c, u in NUMERIC_UNITS.items()])
                book = raw / "owid-co2-codebook.csv"
                definitions.to_csv(book, index=False)
                selection["dataset_sha256"] = sha256(data)
                records = [{"file": p.name, "sha256": sha256(p), "bytes": p.stat().st_size}
                           for p in (data, book)]
                (raw / "source.json").write_text(json.dumps({"files": records}))
                (root / "config" / "analysis_selection.json").write_text(json.dumps(selection))
                (root / "config" / "data_sources.json").write_text("{}")
                for p in raw.iterdir():
                    p.chmod(0o444)
                raw.chmod(0o555)
                before = {p.name: sha256(p) for p in raw.iterdir()}
                first = rebuild(root)
                first_bytes = (root / "data" / "processed" / "metadata.json").read_bytes()
                self.assertEqual(rebuild(root), first)
                self.assertEqual((root / "data" / "processed" / "metadata.json").read_bytes(), first_bytes)
                self.assertEqual({p.name: sha256(p) for p in raw.iterdir()}, before)
                with self.assertRaisesRegex(ValueError, "Output overlaps"):
                    _safe_output(raw / "new.csv", raw)
                link = root / "alias"
                link.symlink_to(raw, target_is_directory=True)
                with self.assertRaisesRegex(ValueError, "Output overlaps"):
                    _safe_output(link / "new.csv", raw)
                data.chmod(0o644)
                with self.assertRaisesRegex(ValueError, "read-only"):
                    verify_snapshot(raw, selection)
                data.write_text(data.read_text() + "\n")
                data.chmod(0o444)
                with self.assertRaisesRegex(ValueError, "integrity check failed"):
                    verify_snapshot(raw, selection)
                book.chmod(0o644)
                definitions.loc[definitions.column.eq("gdp"), "unit"] = "Wrong unit"
                definitions.to_csv(book, index=False)
                with self.assertRaisesRegex(ValueError, "codebook unit"):
                    validate_units(book)
            finally:
                raw.chmod(0o755)
                for p in raw.iterdir():
                    p.chmod(0o644)


if __name__ == "__main__":
    unittest.main()
