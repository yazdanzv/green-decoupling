"""Consequential dashboard data, callbacks, export and local-server checks."""

import base64
import io
import json
import re
import socket
import tempfile
import unittest
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

import pandas as pd

from src.visualization.app import create_app, filtered_data, load_data
from src.visualization.desktop import SaveBridge, local_server
from src.visualization.figures import source_figure, trend_figure


class DashboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.table, cls.metadata = load_data()

    def call(self, app, marker, values, states=None, changed=None):
        key = next(k for k in app.callback_map if marker in k)
        callback = app.callback_map[key]
        outputs = callback["output"]
        if isinstance(outputs, list):
            output_payload = [{"id": o.component_id, "property": o.component_property} for o in outputs]
        else:
            output_payload = {"id": outputs.component_id, "property": outputs.component_property}
        payload = dict(output=key, outputs=output_payload,
                       inputs=[{**item, "value": values[item["id"]]} for item in callback["inputs"]],
                       state=[{**item, "value": (states or {})[item["id"]]} for item in callback["state"]],
                       changedPropIds=[changed or f"{callback['inputs'][0]['id']}.{callback['inputs'][0]['property']}"])
        response = app.server.test_client().post("/_dash-update-component", json=payload)
        self.assertEqual(response.status_code, 200, response.data.decode()[:1000])
        return response.json["response"]

    def controls(self, **overrides):
        defaults = {"focus-country": "DEU", "compare-countries": [], "start-year": 1990, "end-year": 2022,
                    "snapshot-year": 2022, "ranking-metric": "co2", "ranking-count": 10, "source-units": "mt", "reset-counter": 0}
        return defaults | overrides

    def test_real_http_assets_and_callback_match_prepared_values(self):
        with local_server(self.app) as url:
            with urlopen(url, timeout=10) as response:
                page = response.read().decode()
            resources = re.findall(r'<(?:script|link)[^>]+(?:src|href)="([^"]+)"', page)
            self.assertTrue(resources)
            for resource in resources:
                self.assertFalse(urlsplit(resource).netloc, resource)
                with urlopen(url + resource, timeout=10) as response:
                    self.assertEqual(response.status, 200)
                    self.assertGreater(len(response.read()), 0)
        result = self.call(self.app, "growth-scatter.figure", self.controls(**{"focus-country": "USA", "start-year": 2000}))
        trend = result["indexed-trend"]["figure"]["data"]
        usa = self.table.loc[self.table.iso_code.eq("USA")].set_index("year")
        self.assertEqual(trend[0]["name"], "United States · GDP")
        self.assertEqual(trend[0]["x"][0], 2000)
        self.assertEqual(trend[0]["y"][0], 100)
        self.assertAlmostEqual(trend[1]["y"][-1], 100 * usa.at[2022, "co2"] / usa.at[2000, "co2"])
        self.assertIn("20/20", result["growth-coverage"]["children"])

    def test_source_share_and_endpoint_summary(self):
        result = self.call(self.app, "growth-scatter.figure", self.controls(**{"source-units": "share"}))
        source = result["source-trend"]["figure"]
        self.assertEqual(source["layout"]["yaxis"]["range"], [0, 100])
        for i in range(33):
            self.assertAlmostEqual(sum(trace["y"][i] for trace in source["data"]), 100)
        self.assertIn("pp", result["source-status"]["children"])

    def test_source_missing_year_splits_whole_stack(self):
        table = self.table.copy()
        mask = table.iso_code.eq("DEU") & table.year.eq(2000)
        table.loc[mask, ["q4_breakdown_available", "q4_shares_available"]] = False
        fig, _ = source_figure(table, 1990, 2022, "DEU", "mt")
        self.assertEqual(len(fig.data), 8)  # Two complete four-source runs.
        for trace in fig.data:
            self.assertNotIn(2000, trace.x)
            self.assertFalse(min(trace.x) < 2000 < max(trace.x))
        self.assertNotEqual(fig.data[0].stackgroup, fig.data[4].stackgroup)

    def test_newer_snapshot_keeps_territorial_ranking_without_accounting_pair(self):
        result = self.call(self.app, "growth-scatter.figure", self.controls(**{
            "snapshot-year": 2024, "ranking-metric": "co2_per_capita", "ranking-count": 20}))
        self.assertIn("0/20", result["pair-status"]["children"])
        self.assertEqual(result["accounting-pairs"]["figure"]["data"], [])
        bar = result["country-ranking"]["figure"]["data"][0]
        expected = self.table.loc[self.table.year.eq(2024)].sort_values(["co2_per_capita", "iso_code"], ascending=[False, True])
        self.assertEqual(bar["y"], expected.country.tolist())
        self.assertEqual(len(bar["x"]), 20)

    def test_country_click_limit_and_reset(self):
        inputs = {"focus-country": "DEU", "compare-countries": ["CHN", "USA", "IND"],
                  "growth-scatter": {"points": [{"customdata": ["USA", "United States"]}]},
                  "accounting-pairs": None, "country-ranking": None, "reset": 0}
        selected = self.call(self.app, "focus-country.value", inputs, {"reset-counter": 0}, "growth-scatter.clickData")
        self.assertEqual(selected["focus-country"]["value"], "USA")
        self.assertEqual(selected["compare-countries"]["value"], ["CHN", "IND"])
        limited = self.call(self.app, "focus-country.value", inputs, {"reset-counter": 0}, "compare-countries.value")
        self.assertEqual(limited["compare-countries"]["value"], ["CHN", "USA"])
        self.assertIn("at most", limited["comparison-note"]["children"])
        reset = self.call(self.app, "focus-country.value", inputs | {"reset": 1}, {"reset-counter": 0}, "reset.n_clicks")
        self.assertEqual(reset["focus-country"]["value"], "DEU")
        self.assertEqual(reset["compare-countries"]["value"], [])
        self.assertEqual(reset["snapshot-year"]["value"], 2022)
        self.assertEqual(reset["view"]["value"], "growth")
        self.assertEqual(reset["reset-counter"]["data"], 1)
        rerendered = self.call(self.app, "growth-scatter.figure", self.controls(**{"reset-counter": 1}))
        self.assertTrue(rerendered["growth-scatter"]["figure"]["layout"]["uirevision"].endswith("reset-1"))
        self.assertEqual(rerendered["country-ranking"]["figure"]["layout"]["yaxis"]["autorange"], "reversed")


    def test_csv_export_preserves_filters_and_missing(self):
        state = self.controls(**{"snapshot-year": 2024}) | {"view": "footprints"}
        result = self.call(self.app, "export-payload.data", {"export-csv": 1}, state, "export-csv.n_clicks")
        payload = result["export-payload"]["data"]
        frame = pd.read_csv(io.StringIO(payload["content"]))
        self.assertEqual(len(frame), 20)
        self.assertTrue(frame.year.eq(2024).all())
        self.assertTrue(frame.consumption_co2.isna().all())
        self.assertTrue(frame.co2.notna().all())
        growth = filtered_data(self.table, "growth", "DEU", ["USA", "CHN"], 2000, 2022, 2024)
        self.assertEqual(set(growth.iso_code), {"DEU", "USA", "CHN"})
        self.assertEqual(len(growth), 3*23)

    def test_export_bridge_writes_expected_bytes(self):
        with tempfile.TemporaryDirectory() as directory:
            bridge = SaveBridge(Path(directory))
            result = bridge.save_file("example.csv", "country,value\nTest,1\n")
            self.assertTrue(result["saved"])
            self.assertEqual((Path(directory)/"example.csv").read_text(), "country,value\nTest,1\n")
            content = b"\x89PNG\r\n\x1a\n"
            bridge.save_file("example.png", base64.b64encode(content).decode(), True)
            self.assertEqual((Path(directory)/"example.png").read_bytes(), content)
            with self.assertRaises(ValueError):
                bridge.save_file("unsupported.exe", "no")

    def test_missing_index_observations_remain_gaps(self):
        table = self.table.copy()
        table.loc[table.iso_code.eq("DEU") & table.year.eq(2000), "gdp"] = float("nan")
        fig = trend_figure(table, 1990, 2022, ["DEU"])
        self.assertTrue(pd.isna(fig.data[0].y[10]))
        self.assertFalse(fig.data[0].connectgaps)

    def test_server_releases_port(self):
        with local_server(self.app) as url:
            port = urlsplit(url).port
            with urlopen(url+"/_dash-layout", timeout=10) as response:
                self.assertEqual(response.status, 200)
        with socket.socket() as connection:
            connection.settimeout(1)
            self.assertNotEqual(connection.connect_ex(("127.0.0.1", port)), 0)


if __name__ == "__main__":
    unittest.main()
