"""The first interactive OWID desktop dashboard; all assets and data are local."""

import hashlib
import json
import sys
from pathlib import Path

import pandas as pd
from dash import Dash, Input, Output, State, ctx, dcc, html, no_update

from src.visualization.figures import (
    accounting_figure, empty_figure, paired_figure, ranking_figure,
    scatter_figure, source_figure, trend_figure,
)

ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
DEFAULTS = dict(focus="DEU", comparisons=[], start=1990, end=2022,
                snapshot=2022, metric="co2", count=10, source="mt", view="growth")
GRAPH_CONFIG = {"displaylogo": False, "responsive": True,
                "modeBarButtonsToRemove": ["toImage", "sendChartToCloud", "lasso2d", "select2d"]}


def load_data(root=ROOT):
    path = root / "data" / "processed" / "country_year.csv"
    metadata = json.loads(path.with_name("metadata.json").read_text())
    if hashlib.sha256(path.read_bytes()).hexdigest() != metadata["prepared_csv_sha256"]:
        raise ValueError("Prepared data hash does not match metadata; rebuild the data.")
    table = pd.read_csv(path)
    if table.duplicated(["iso_code", "year"]).any():
        raise ValueError("Duplicate country-year keys")
    return table, metadata


def selection_codes(focus, comparisons):
    return [focus, *[code for code in (comparisons or []) if code != focus][:2]]


def filtered_data(table, view, focus, comparisons, start, end, snapshot):
    if view == "growth":
        return table.loc[table.iso_code.isin(selection_codes(focus, comparisons)) & table.year.between(start, end)]
    return table.loc[table.year.eq(snapshot)]


def format_value(value, suffix=""):
    return "Unavailable" if pd.isna(value) else f"{value:+,.1f}{suffix}"


def data_table(frame):
    columns = ["country", "year", "gdp", "co2", "consumption_co2", "co2_per_capita", "accounting_gap_mt"]
    labels = ["Country", "Year", "GDP (intl-$ 2011)", "Territorial (Mt)", "Consumption (Mt)", "Tonnes/person", "Accounting gap (Mt)"]
    return html.Div(html.Table([
        html.Thead(html.Tr([html.Th(label, scope="col") for label in labels])),
        html.Tbody([html.Tr([html.Td(
            "Unavailable" if pd.isna(row[c]) else
            (str(int(row[c])) if c == "year" else f"{row[c]:,.2f}" if c != "country" else str(row[c]))
        ) for c in columns]) for _, row in frame.iterrows()]),
    ]), className="table-scroll")


def render_views(table, focus, comparisons, start, end, snapshot, metric, count, source):
    if start is None or end is None or start >= end:
        figures = [empty_figure("Choose an end year later than the start year.") for _ in range(6)]
        return (*figures, [], "Invalid analysis period.", "", "", "", "")
    codes = selection_codes(focus, comparisons)
    name = table.loc[table.iso_code.eq(focus), "country"].iloc[0]
    scatter, changes = scatter_figure(table, start, end, focus, comparisons or [])
    trend = trend_figure(table, start, end, codes)
    sources, source_status = source_figure(table, start, end, focus, source)
    pairs, pair_status = paired_figure(table, snapshot, focus)
    history, history_status = accounting_figure(table, focus, snapshot)
    ranks, rank_status = ranking_figure(table, snapshot, focus, metric, count)
    row = changes.loc[changes.iso_code.eq(focus)].iloc[0]
    summaries = [html.Div([
        html.Span(label, className="stat-label"), html.Strong(value), html.Span(note, className="stat-note"),
    ], className="stat") for label, value, note in [
        (f"{name} · real GDP", format_value(row.gdp_change_pct, "%"), f"Selected endpoints · {start}–{end}"),
        (f"{name} · territorial CO₂", format_value(row.co2_change_pct, "%"), "Fossil fuels and industry · excluding land use"),
        ("Selected-period pattern", row.decoupling, "Descriptive comparison · no causal attribution"),
    ]]
    unavailable = changes.loc[~changes.q1_available, "country"].tolist()
    coverage = f"{changes.q1_available.sum()}/20 countries with valid endpoints · {start}–{end}."
    if unavailable:
        coverage += " Unavailable: " + ", ".join(unavailable) + "."
    return (scatter, trend, sources, pairs, history, ranks, summaries,
            coverage, source_status, pair_status, history_status, rank_status)


def field(label, component, class_name=""):
    return html.Div([html.Label(label, id=f"label-{component.id}", htmlFor=component.id), component],
                    className=f"field {class_name}")


def dropdown(id, options, value, **kwargs):
    return dcc.Dropdown(id=id, options=options, value=value, clearable=False, **kwargs)


def chart_section(title, subtitle, graph_id, figure, extra=None, status_id=None, status=None, class_name=""):
    return html.Section([
        html.Div([html.Div([html.H2(title), html.P(subtitle, className="chart-description")]),
                  html.Button("Save PNG", className="quiet-button png-export", **{"data-chart": graph_id})], className="chart-heading"),
        extra,
        # Responsive Plotly clears layout.height. Give its host an explicit
        # height so WebKit cannot collapse it after an update or window resize.
        html.Div(dcc.Graph(id=graph_id, figure=figure, config=GRAPH_CONFIG,
                           responsive=True, style={"height": f"{figure.layout.height}px"},
                           className="plot"), role="group", **{"aria-label": f"{title}. {subtitle}"}),
        html.P(status or "", id=status_id, className="chart-note", **{"aria-live": "polite"}) if status_id else None,
    ], className=f"chart-section {class_name}")


def create_app():
    table, metadata = load_data()
    countries = table[["iso_code", "country"]].drop_duplicates().sort_values("country")
    country_options = [{"label": r.country, "value": r.iso_code} for r in countries.itertuples()]
    all_codes = set(countries.iso_code)
    years = sorted(table.year.unique().tolist())
    gdp_years = sorted(table.loc[table.gdp.notna(), "year"].unique().tolist())
    initial = render_views(table, **{k: DEFAULTS[k] for k in ["focus", "comparisons", "start", "end", "snapshot", "metric", "count", "source"]})
    app = Dash(__name__, title="Green Decoupling", serve_locally=True,
               assets_folder=str(ROOT / "src" / "visualization" / "assets"))
    app.layout = html.Main([
        dcc.Store(id="reset-counter", data=0), dcc.Store(id="export-payload"), dcc.Store(id="export-result"),
        html.Header([
            html.Div([html.P("INFORMATION VISUALIZATION · GROUP 16", className="eyebrow"),
                      html.H1("Green Decoupling"),
                      html.P("Explore economic growth, carbon footprints, and the sources behind emissions.", className="intro")]),
            html.Div([field("Focus country", dropdown("focus-country", country_options, "DEU", searchable=True)),
                      html.Button("Reset filters", id="reset", n_clicks=0, className="reset-button")], className="header-actions"),
        ], className="page-header"),
        html.Div([html.Span("OWID CO₂ dataset", className="source-tag"),
                  html.Span("Fixed cohort · top 20 territorial emitters in 2022"),
                  html.Span("GDP to 2022 · consumption to 2023 · territorial to 2024")], className="dataset-strip"),
        html.Div(dcc.RadioItems(id="view", value="growth", options=[
            {"label": "Growth & Emissions", "value": "growth"},
            {"label": "Footprints & Comparisons", "value": "footprints"},
        ], className="tabs", inputClassName="tab-radio", labelClassName="tab-option"),
                 role="group", **{"aria-label": "Dashboard view"}, className="tab-container"),
        html.Div([
            html.Div([
                field("Analysis start year", dropdown("start-year", gdp_years[:-1], 1990, searchable=False)),
                field("Analysis end year", dropdown("end-year", gdp_years[1:], 2022, searchable=False)),
                field("Compare with (up to 2 additional countries)", dcc.Dropdown(
                    id="compare-countries", options=country_options, multi=True, value=[],
                    placeholder="Add a country…", searchable=True, closeOnSelect=False), "comparison-field"),
            ], className="control-bar"),
            html.P("", id="comparison-note", className="control-note", **{"aria-live": "polite"}),
            html.Div(id="summary", children=initial[6], className="summary-row"),
            chart_section("Growth and emissions: the country overview", "Each point is a country. Click to focus; the diagonal marks equal GDP and CO₂ growth.",
                          "growth-scatter", initial[0], status_id="growth-coverage", status=initial[7], class_name="overview"),
            html.Div([
                chart_section("When did the trajectories diverge?", "Solid = GDP · dashed = territorial CO₂. Each series starts at 100 in the selected start year.",
                              "indexed-trend", initial[1]),
                chart_section("What makes up the emissions?", "Coal, oil, gas, and other fossil/industrial sources (derived). Shares refer to CO₂, not energy.",
                              "source-trend", initial[2], extra=field("Source display", dropdown("source-units", [
                                  {"label": "Emissions amount · Mt CO₂", "value": "mt"}, {"label": "Share of total CO₂ · %", "value": "share"}], "mt", searchable=False), "compact-field"),
                              status_id="source-status", status=initial[8]),
            ], className="two-columns"),
        ], id="growth-panel"),
        html.Div([
            html.Div([
                field("Snapshot year", dropdown("snapshot-year", years, 2022, searchable=False)),
                field("Ranking metric", dropdown("ranking-metric", [{"label": "Total territorial · Mt CO₂", "value": "co2"},
                      {"label": "Per capita · tonnes CO₂/person", "value": "co2_per_capita"}], "co2", searchable=False)),
                field("Ranking length", dropdown("ranking-count", [{"label": "Top 10 within cohort", "value": 10},
                      {"label": "All 20 cohort countries", "value": 20}], 10, searchable=False)),
            ], className="control-bar"),
            chart_section("Where does the footprint sit?", "Circle = territorial · diamond = consumption. Countries are ordered by consumption minus territorial CO₂.",
                          "accounting-pairs", initial[3], status_id="pair-status", status=initial[9]),
            html.Div([
                chart_section("Two ways to account for one footprint", "Focus country · full 1990–2024 history. The dotted reference marks the selected snapshot year.",
                              "accounting-history", initial[4], status_id="history-status", status=initial[10]),
                chart_section("How does the ranking change?", "Rankings are within the fixed major-emitter cohort. Click a bar to focus a country.",
                              "country-ranking", initial[5], status_id="rank-status", status=initial[11]),
            ], className="two-columns"),
        ], id="footprints-panel", style={"display": "none"}),
        html.Section([
            html.Div([html.H2("Explore the numbers"), html.Button("Download filtered CSV", id="export-csv", n_clicks=0, className="reset-button")], className="chart-heading"),
            html.P("Growth exports the focus/comparison countries over the selected period; Footprints exports the cohort in the snapshot year.", className="chart-description"),
            html.P(id="export-status", className="chart-note", **{"aria-live": "polite"}),
            html.Details([html.Summary("Show accessible data table"), html.Div(id="data-table")]),
            html.Details([
                html.Summary("Methods, definitions & source credits"),
                html.P("Cohort: the 20 eligible individual countries with highest territorial CO₂ in 2022. Membership stays fixed; rankings are not global per-capita rankings."),
                html.P("GDP is total real GDP in international dollars at 2011 prices. CO₂ covers fossil fuels and industry, excluding land-use change. Changes = 100 × (end − start) / start; index = 100 × value / selected-start value."),
                html.P("Absolute decoupling means GDP rises and territorial CO₂ falls. Relative decoupling means both rise but CO₂ rises more slowly. Flat emissions, equal growth, and non-growing GDP are labelled separately using unrounded changes."),
                html.P("Consumption accounting adjusts for emissions embodied in trade. Accounting gap = consumption − territorial CO₂. This difference alone does not demonstrate industrial relocation or a causal mechanism."),
                html.P("Other fossil/industrial sources (derived) = total − coal − oil − gas. It includes cement, flaring and other contributions/adjustments; it is not the published other_industry_co2 column. Shares require a positive total and a complete breakdown."),
                html.P("Missing values remain unavailable; no interpolation, zero fill, stale-year substitution or GDP extrapolation. Trend lines break at gaps. Zoom does not alter analytical selections."),
                html.Ul([html.Li([html.A(source["name"], href=source["url"], target="_blank", rel="noopener noreferrer"),
                                  f" · {source.get('license', 'See source terms and attribution')}"])
                         for source in metadata["sources_and_release_attribution"]["sources"]]),
                html.P("OWID credits and underlying-source terms apply. National GDP-source citations and final GCB/UN attribution checks remain part of the distribution audit. This local preview is not a final release."),
                html.P(f"Prepared CSV SHA-256: {metadata['prepared_csv_sha256']}", className="hash"),
            ], className="methods"),
        ], className="data-section"),
        html.Footer("TU Wien · Information Visualization · Yazdan Zandiyevakili & Ben Barth · OWID snapshot retrieved 2 November 2026"),
    ], className="app-shell")

    @app.callback(
        Output("focus-country", "value"), Output("compare-countries", "value"), Output("comparison-note", "children"),
        Output("reset-counter", "data"), Output("start-year", "value"), Output("end-year", "value"),
        Output("snapshot-year", "value"), Output("ranking-metric", "value"), Output("ranking-count", "value"),
        Output("source-units", "value"), Output("view", "value"),
        Input("focus-country", "value"), Input("compare-countries", "value"),
        Input("growth-scatter", "clickData"), Input("accounting-pairs", "clickData"), Input("country-ranking", "clickData"),
        Input("reset", "n_clicks"), State("reset-counter", "data"), prevent_initial_call=True,
    )
    def select_country(focus, comparisons, scatter_click, pair_click, rank_click, reset, counter):
        if ctx.triggered_id == "reset":
            return ("DEU", [], "", counter + 1, 1990, 2022, 2022, "co2", 10, "mt", "growth")
        click = {"growth-scatter": scatter_click, "accounting-pairs": pair_click, "country-ranking": rank_click}.get(ctx.triggered_id)
        if click and click.get("points"):
            custom = click["points"][0].get("customdata")
            if custom and custom[0] in all_codes:
                focus = custom[0]
        comparisons = list(dict.fromkeys(code for code in (comparisons or []) if code in all_codes and code != focus))
        note = "Compare at most two additional countries; the first two were retained." if len(comparisons) > 2 else ""
        return (focus, comparisons[:2], note, *([no_update] * 8))

    @app.callback(Output("start-year", "options"), Output("end-year", "options"),
                  Input("start-year", "value"), Input("end-year", "value"))
    def valid_year_options(start, end):
        return [y for y in gdp_years if y < end], [y for y in gdp_years if y > start]

    @app.callback(
        *[Output(id, "figure") for id in ["growth-scatter", "indexed-trend", "source-trend", "accounting-pairs", "accounting-history", "country-ranking"]],
        Output("summary", "children"), Output("growth-coverage", "children"), Output("source-status", "children"),
        Output("pair-status", "children"), Output("history-status", "children"), Output("rank-status", "children"),
        *[Output(id, "style") for id in ["growth-scatter", "indexed-trend", "source-trend", "accounting-pairs", "accounting-history", "country-ranking"]],
        Input("focus-country", "value"), Input("compare-countries", "value"), Input("start-year", "value"), Input("end-year", "value"),
        Input("snapshot-year", "value"), Input("ranking-metric", "value"), Input("ranking-count", "value"), Input("source-units", "value"),
        Input("reset-counter", "data"),
    )
    def update_views(focus, comparisons, start, end, snapshot, metric, count, source, reset_counter):
        result = render_views(table, focus, comparisons, start, end, snapshot, metric, count, source)
        for figure in result[:6]:
            figure.update_layout(uirevision=f"{figure.layout.uirevision}-reset-{reset_counter}")
        return (*result, *[{"height": f"{figure.layout.height}px"} for figure in result[:6]])

    @app.callback(Output("data-table", "children"), Input("view", "value"), Input("focus-country", "value"),
                  Input("compare-countries", "value"), Input("start-year", "value"), Input("end-year", "value"), Input("snapshot-year", "value"))
    def update_data(view, focus, comparisons, start, end, snapshot):
        return data_table(filtered_data(table, view, focus, comparisons, start, end, snapshot))

    @app.callback(Output("export-payload", "data"), Input("export-csv", "n_clicks"), State("view", "value"),
                  State("focus-country", "value"), State("compare-countries", "value"), State("start-year", "value"),
                  State("end-year", "value"), State("snapshot-year", "value"), prevent_initial_call=True)
    def export_csv(clicks, view, focus, comparisons, start, end, snapshot):
        frame = filtered_data(table, view, focus, comparisons, start, end, snapshot)
        period = f"{start}-{end}" if view == "growth" else str(snapshot)
        return dict(filename=f"green-decoupling-{view}-{period}.csv", content=frame.to_csv(index=False, na_rep=""),
                    base64_encoded=False, request=clicks)

    app.clientside_callback("""function(view) {
        setTimeout(() => window.dispatchEvent(new Event('resize')), 150);
        return [view === 'growth' ? {} : {display:'none'}, view === 'footprints' ? {} : {display:'none'}];
    }""", Output("growth-panel", "style"), Output("footprints-panel", "style"), Input("view", "value"))
    app.clientside_callback("""function(payload) {
        if (!payload) return window.dash_clientside.no_update;
        window.saveDashboardFile(payload.filename, payload.content, payload.base64_encoded);
        return payload.request;
    }""", Output("export-result", "data"), Input("export-payload", "data"), prevent_initial_call=True)
    return app


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8050)
    args = parser.parse_args()
    create_app().run(host="127.0.0.1", port=args.port, debug=False)
