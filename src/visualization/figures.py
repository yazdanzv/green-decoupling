"""Plotly views of the approved OWID measures; no data imputation."""

import pandas as pd
import plotly.graph_objects as go

from src.data.measures import endpoint_changes, indexed_trends, matched_rankings

CATEGORY_COLORS = {
    "Absolute decoupling": "#007A68", "Relative decoupling": "#2868B2",
    "GDP growth with flat emissions": "#856000", "Equal GDP and emissions growth": "#6B55A1",
    "Emissions growing faster than GDP": "#AD4B1F", "GDP not growing": "#667085",
}
COUNTRY_COLORS = ["#007A68", "#2868B2", "#9658A4"]
SOURCES = [
    ("coal_co2", "Coal", "#526170"), ("oil_co2", "Oil", "#BC7018"),
    ("gas_co2", "Gas", "#287CB8"),
    ("other_fossil_industrial_co2", "Other fossil/industrial (derived)", "#9770AA"),
]
TERRITORIAL, CONSUMPTION = "#2868B2", "#AD4B1F"


def base_figure(height=390):
    fig = go.Figure()
    fig.update_layout(
        template="plotly_white", height=height, margin=dict(l=62, r=22, t=50, b=65),
        font=dict(family="-apple-system, BlinkMacSystemFont, Segoe UI, sans-serif", size=12, color="#344054"),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="top", y=-0.21, x=0, font=dict(size=11)),
        hoverlabel=dict(bgcolor="white", font_size=12),
    )
    fig.update_xaxes(gridcolor="#edf0f2", zerolinecolor="#c6cdd3", automargin=True)
    fig.update_yaxes(gridcolor="#edf0f2", zerolinecolor="#c6cdd3", automargin=True)
    return fig


def empty_figure(message, height=390):
    fig = base_figure(height)
    fig.add_annotation(text=message, x=0.5, y=0.5, xref="paper", yref="paper", showarrow=False)
    fig.update_xaxes(visible=False)
    fig.update_yaxes(visible=False)
    return fig


def scatter_figure(table, start, end, focus, comparisons):
    changes = endpoint_changes(table, start, end)
    eligible = changes.loc[changes.q1_available]
    if eligible.empty:
        return empty_figure("No countries have valid endpoints for this period.", 470), changes
    fig = base_figure(470)
    endpoints = table.set_index(["iso_code", "year"])
    for category, color in CATEGORY_COLORS.items():
        group = eligible.loc[eligible.decoupling.eq(category)]
        if group.empty:
            continue
        custom, labels = [], []
        for row in group.itertuples():
            a, b = endpoints.loc[(row.iso_code, start)], endpoints.loc[(row.iso_code, end)]
            custom.append([row.iso_code, row.country, category, a.gdp, b.gdp, a.co2, b.co2])
            labels.append(row.iso_code if row.iso_code in [focus, *comparisons] else "")
        fig.add_trace(go.Scatter(
            x=group.gdp_change_pct.tolist(), y=group.co2_change_pct.tolist(),
            mode="markers+text", text=labels, textposition="top center", name=category,
            marker=dict(size=11, color=color, line=dict(color="white", width=1)),
            customdata=custom, cliponaxis=False,
            hovertemplate=("<b>%{customdata[1]}</b><br>" + f"{start} → {end}<br>"
                           "GDP change: %{x:.2f}%<br>CO₂ change: %{y:.2f}%<br>"
                           "GDP: %{customdata[3]:,.0f} → %{customdata[4]:,.0f} intl-$ (2011)<br>"
                           "CO₂: %{customdata[5]:,.2f} → %{customdata[6]:,.2f} Mt<br>"
                           "%{customdata[2]}<extra></extra>"),
        ))
    selected = eligible.loc[eligible.iso_code.eq(focus)]
    if not selected.empty:
        fig.add_trace(go.Scatter(
            x=selected.gdp_change_pct.tolist(), y=selected.co2_change_pct.tolist(),
            mode="markers", marker=dict(size=19, color="rgba(0,0,0,0)", line=dict(color="#172B2A", width=2)),
            customdata=[[focus]], hoverinfo="skip", showlegend=False,
        ))
    fig.add_hline(y=0, line_color="#79858E", line_width=1)
    fig.add_vline(x=0, line_color="#79858E", line_width=1)
    upper = max(0, min(eligible.gdp_change_pct.max(), eligible.co2_change_pct.max()))
    if upper > 0:
        fig.add_shape(type="line", x0=0, y0=0, x1=upper, y1=upper,
                      line=dict(color="#A0A9B1", dash="dot", width=1))
        fig.add_annotation(x=upper, y=upper, text="Equal growth", showarrow=False,
                           yshift=13, font=dict(size=10, color="#667085"))
    fig.update_xaxes(title="Total real GDP change (%)")
    fig.update_yaxes(title="Territorial CO₂ change (%)")
    fig.update_layout(title=dict(text=f"Fixed 20-country cohort · {start}–{end}", font_size=12, x=0),
                      uirevision=f"scatter-{start}-{end}", margin=dict(b=100))
    return fig, changes


def trend_figure(table, start, end, codes):
    fig = base_figure(410)
    any_valid = False
    for i, code in enumerate(codes):
        country = table.loc[table.iso_code.eq(code), "country"].iloc[0]
        source = table.loc[table.iso_code.eq(code)].set_index("year")
        for metric, label, dash in [("gdp", "GDP", "solid"), ("co2", "CO₂", "dash")]:
            trend = indexed_trends(table.loc[table.iso_code.eq(code)], metric, start, end)
            any_valid |= trend["index"].notna().any()
            original = source[metric].reindex(trend.year).tolist()
            unit = "intl-$ (2011)" if metric == "gdp" else "Mt CO₂"
            fig.add_trace(go.Scatter(
                x=trend.year.tolist(), y=trend["index"].tolist(), mode="lines",
                line=dict(color=COUNTRY_COLORS[i], width=2.4, dash=dash),
                name=f"{country} · {label}", connectgaps=False, customdata=original,
                hovertemplate=(f"<b>{country} · {label}</b><br>Year %{{x}}<br>"
                               f"Index: %{{y:.2f}} ({start} = 100)<br>"
                               f"Original: %{{customdata:,.2f}} {unit}<extra></extra>"),
            ))
    if not any_valid:
        return empty_figure("Selected-start baselines are unavailable.", 410)
    fig.add_hline(y=100, line_dash="dot", line_color="#9DA9A9")
    fig.update_xaxes(title="Year", dtick=max(1, (end - start) // 6), range=[start, end])
    fig.update_yaxes(title=f"Index ({start} = 100)")
    fig.update_layout(title=dict(text=f"Selected countries · {start}–{end} · baseline {start} = 100", font_size=12, x=0),
                      uirevision=f"index-{start}-{end}-{'-'.join(codes)}", margin=dict(b=100))
    return fig


def source_figure(table, start, end, focus, mode):
    group = table.loc[table.iso_code.eq(focus) & table.year.between(start, end)].sort_values("year")
    is_share = mode == "share"
    available = group.q4_shares_available if is_share else group.q4_breakdown_available
    if not available.any():
        return empty_figure("Complete source breakdown unavailable.", 410), "Endpoint source changes unavailable."
    fig = base_figure(410)
    # Split into runs: fill traces cannot bridge or zero-fill a missing year.
    runs = available.ne(available.shift()).cumsum()
    seen = set()
    for run, segment in group.loc[available].groupby(runs[available], sort=False):
        for column, label, color in SOURCES:
            values = segment[f"{column}_share_pct"] if is_share else segment[column]
            fig.add_trace(go.Scatter(
                x=segment.year.tolist(), y=values.tolist(), mode="lines", stackgroup=f"complete-{run}",
                line=dict(color=color, width=0.8), fillcolor=color,
                name=label, legendgroup=column, showlegend=column not in seen, connectgaps=False,
                customdata=segment[[column, f"{column}_share_pct", "co2"]].values.tolist(),
                hovertemplate=(f"<b>{label}</b><br>Year %{{x}}<br>"
                               "%{customdata[0]:,.2f} Mt · %{customdata[1]:.2f}%<br>"
                               "Total: %{customdata[2]:,.2f} Mt<extra></extra>"),
            ))
            seen.add(column)
    fig.update_xaxes(title="Year", range=[start, end], dtick=max(1, (end-start)//6))
    fig.update_yaxes(title="Share of total CO₂ (%)" if is_share else "CO₂ emissions (Mt)", rangemode="tozero")
    if is_share:
        fig.update_yaxes(range=[0, 100])
    country = group.country.iloc[0]
    fig.update_layout(title=dict(text=f"{country} · {start}–{end}", font_size=12, x=0),
                      hovermode="x unified", legend=dict(itemclick=False, itemdoubleclick=False),
                      uirevision=f"source-{focus}-{start}-{end}-{mode}", margin=dict(b=105))
    indexed = group.set_index("year")
    flag = "q4_shares_available" if is_share else "q4_breakdown_available"
    if any(year not in indexed.index or not indexed.at[year, flag] for year in [start, end]):
        return fig, "Selected endpoint source changes unavailable."
    changes = []
    for column, label, _ in SOURCES:
        metric = f"{column}_share_pct" if is_share else column
        delta = indexed.at[end, metric] - indexed.at[start, metric]
        changes.append(f"{label}: {delta:+,.1f} {'pp' if is_share else 'Mt'}")
    return fig, f"{start} → {end} · " + " · ".join(changes)


def paired_figure(table, year, focus):
    snapshot = table.loc[table.year.eq(year)].copy()
    eligible = snapshot.loc[snapshot.q2_pair_available].sort_values(
        ["accounting_gap_mt", "iso_code"], ascending=[False, True]
    )
    missing = snapshot.loc[~snapshot.q2_pair_available, "country"].tolist()
    status = f"{len(eligible)}/20 matched country pairs · {year}."
    if missing:
        status += " Unavailable: " + ", ".join(missing) + "."
    if eligible.empty:
        return empty_figure(f"Consumption-based CO₂ unavailable for {year}.<br>Select 1990–2023 for matched pairs.", 560), status
    fig = base_figure(max(560, len(eligible) * 25 + 115))
    for row in eligible.itertuples():
        fig.add_trace(go.Scatter(
            x=[row.co2, row.consumption_co2], y=[row.country, row.country], mode="lines",
            line=dict(color="#89999A" if row.iso_code == focus else "#CDD5D9", width=3 if row.iso_code == focus else 1.5),
            hoverinfo="skip", showlegend=False,
        ))
    custom = eligible[["iso_code", "country", "co2", "consumption_co2", "accounting_gap_mt"]].values.tolist()
    for metric, name, symbol, color in [("co2", "Territorial", "circle", TERRITORIAL),
                                       ("consumption_co2", "Consumption", "diamond", CONSUMPTION)]:
        fig.add_trace(go.Scatter(
            x=eligible[metric].tolist(), y=eligible.country.tolist(), mode="markers", name=name,
            marker=dict(color=color, symbol=symbol, size=[13 if c == focus else 8 for c in eligible.iso_code],
                        line=dict(width=1, color="white")), customdata=custom,
            hovertemplate=("<b>%{customdata[1]}</b><br>" + f"{year}<br>"
                           "Territorial: %{customdata[2]:,.2f} Mt<br>Consumption: %{customdata[3]:,.2f} Mt<br>"
                           "Consumption − territorial: %{customdata[4]:+,.2f} Mt<extra></extra>"),
        ))
    fig.update_yaxes(categoryorder="array", categoryarray=eligible.country.tolist(), autorange="reversed", showgrid=False)
    fig.update_xaxes(title="Fossil and industrial CO₂ (Mt)", rangemode="tozero")
    fig.update_layout(title=dict(text=f"Territorial vs consumption CO₂ · {year}", font_size=12, x=0),
                      uirevision=f"paired-{year}", margin=dict(l=125, b=85), legend=dict(y=-0.12))
    return fig, status


def accounting_figure(table, focus, year):
    group = table.loc[table.iso_code.eq(focus)].sort_values("year")
    fig = base_figure(410)
    for metric, label, color, dash in [("co2", "Territorial", TERRITORIAL, "solid"),
                                      ("consumption_co2", "Consumption", CONSUMPTION, "dash")]:
        fig.add_trace(go.Scatter(
            x=group.year.tolist(), y=group[metric].tolist(), mode="lines", name=label,
            line=dict(color=color, dash=dash, width=2.5), connectgaps=False,
            hovertemplate=f"{label}<br>Year %{{x}}<br>%{{y:,.2f}} Mt CO₂<extra></extra>",
        ))
    fig.add_vline(x=year, line_dash="dot", line_color="#7A878C")
    fig.update_xaxes(title="Year", range=[int(group.year.min()), int(group.year.max())], dtick=5)
    fig.update_yaxes(title="CO₂ emissions (Mt)", rangemode="tozero")
    fig.update_layout(title=dict(text=f"{group.country.iloc[0]} · 1990–2024 · selected {year}", font_size=12, x=0),
                      uirevision=f"account-{focus}")
    row = group.loc[group.year.eq(year)]
    status = "Accounting gap unavailable for the selected year."
    if not row.empty and row.iloc[0].q2_pair_available:
        status = f"{year} consumption − territorial: {row.iloc[0].accounting_gap_mt:+,.2f} Mt CO₂."
    return fig, status


def ranking_figure(table, year, focus, metric, count):
    rankings = matched_rankings(table, year)
    eligible = rankings.loc[rankings.q3_available].sort_values([metric, "iso_code"], ascending=[False, True])
    shown = eligible.head(count)
    status = f"Showing {len(shown)} of {len(eligible)} eligible countries in the fixed 20-country cohort."
    if focus not in shown.iso_code.values:
        status += " Focus country is outside this display; choose all 20 to include it if eligible."
    if shown.empty:
        return empty_figure("No matched total/per-capita observations for this year.", 410), status
    unit = "Mt CO₂" if metric == "co2" else "tonnes CO₂/person"
    fig = base_figure(max(410, len(shown)*24 + 90))
    custom = shown[["iso_code", "country", f"{metric}_rank"]].values.tolist()
    fig.add_trace(go.Bar(
        x=shown[metric].tolist(), y=shown.country.tolist(), orientation="h", customdata=custom,
        marker_color=["#007A68" if code == focus else "#A4B7BB" for code in shown.iso_code],
        text=[f"{v:,.1f}" for v in shown[metric]], textposition="outside", cliponaxis=False,
        hovertemplate=f"<b>%{{customdata[1]}}</b><br>Rank %{{customdata[2]}} within cohort<br>%{{x:,.2f}} {unit}<extra></extra>",
    ))
    fig.update_yaxes(categoryorder="array", categoryarray=shown.country.tolist(), autorange="reversed", showgrid=False)
    fig.update_xaxes(title=unit, rangemode="tozero", range=[0, shown[metric].max()*1.18])
    fig.update_layout(title=dict(text=f"Within fixed 20-country cohort · {year}", font_size=12, x=0),
                      showlegend=False, uirevision=f"rank-{year}-{metric}-{count}", margin=dict(l=110, r=45))
    return fig, status
