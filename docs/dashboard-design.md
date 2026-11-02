# Version 1 dashboard specification

Recorded 2026-11-02 before implementation. D015-D020 capture individual approvals;
D021 delegates the remaining UI defaults to the assistant for the first version.
The choices below are accepted for that iteration and can change after review.
This is a local course-project preview, not a validated final Windows release.

## Layout

Use a light desktop interface with a shared header, two named views selected by keyboard-operable radio navigation, and focus
country selector. Keep content within 1440 px. Use native system fonts, 14 px
body text, legible chart labels, visible keyboard focus, and no external assets.
At 1280x800 and 1440x900 the charts fit their containers; vertical page scrolling
is intentional. Below 1000 px the two-column rows stack. Support 800x600 without
horizontal page overflow; native window minimum is 800x600.

```text
Green Decoupling                          Focus country | Reset
Growth & Emissions | Footprints & Comparisons

GROWTH & EMISSIONS
Start year | End year | Compare countries (max 2 additional)
Selected-country GDP / CO2 changes and descriptive category
GDP-change vs CO2-change scatter (all eligible cohort countries)
Indexed GDP/CO2 trend         | Source composition + Mt/share switch

FOOTPRINTS & COMPARISONS
Snapshot year | Ranking metric | Show 10/20
Territorial/consumption paired dots (eligible cohort countries)
Accounting history           | Total/per-capita country ranking

Both tabs: chart PNG download; data/methods + filtered CSV download
```

## Shared state and defaults

- Initial tab: Growth & Emissions. Focus: Germany (a readable starting case,
  not a claimed representative country). Initial comparison list: empty.
- One focus country plus at most two additional comparisons gives at most
  three countries/six indexed lines. Selecting a new focus removes it from
  additional comparisons, retaining the other two where possible. Selecting
  a third additional country keeps the first two and shows an explanatory note.
- Searchable country selector and clicks on scatter, accounting dots, or ranking
  bars set the same focus. Preserve all controls and selections across tabs.
- First-tab start/end years: 1990/2022, constrained to positive-GDP coverage and
  start < end. Options constrain invalid combinations, rather than substituting
  endpoint years. Source composition uses this same period.
- Second-tab snapshot: 2022, with 1990-2024 available. Its accounting-history
  chart shows the entire 1990-2024 prepared range and marks the selected snapshot
  year. Its range is labelled separately from the first-tab analysis period.
- Ranking default: total territorial Mt, top 10 within the fixed 20-country
  cohort. Switch to tonnes/person and/or all 20. Same-year shared eligibility
  for total/per-capita, stable ISO tie-breaker, equal values share minimum rank.
- Reset restores all defaults and zoom. Plotly zoom/pan is visual only; it does
  not alter analysis endpoints, normalization, cohort, or snapshot year. Hover
  and legend inspection never changes focus.

## Chart definitions

1. **GDP vs CO2 changes:** D017/P008. Linear percent axes; zeros and y=x reference;
   equal country marks with focus ring. Use descriptive category colors and
   category text in hover. Label focus/comparison countries, not all 20 labels.
   The equality reference applies to growth comparisons; non-growing GDP has
   its own category. Titles include selected period. No causal language.
2. **Indexed GDP and CO2:** D018/P009. Common linear baseline-100 axis, solid GDP
   and dashed territorial CO2. Country colors are local to the country legend.
   No connecting across gaps, no substitute baseline. Up to three countries.
3. **CO2 sources:** D019/P010. Four fixed layers coal/oil/gas/derived-other,
   default Mt and switchable to percentages. No component-removing legend
   actions. Split stacks into complete contiguous segments so missing years are
   actual gaps, not zero-height areas. A compact endpoint summary shows Mt or
   percentage-point changes. Shares are emissions shares, not energy shares.
4. **Territorial vs consumption:** D020/P011. Horizontal common-linear-axis
   paired dots, circle vs diamond, neutral connectors, descending signed
   consumption-minus-territorial gap. Show all eligible pairs and selected-year
   coverage. Clicking sets focus. In 2024 show explicit unavailable accounting
   message; retain valid territorial ranking and history.
5. **Accounting history:** focus-country territorial and consumption totals in Mt
   on one linear axis, solid territorial/dashed consumption, distinguishable
   colors. Show observed 1990-2024 data with gaps and a selected-year reference.
   Show the signed selected-year gap in a text summary where both exist.
6. **Ranking:** horizontal bars sorted descending metric with zero origin,
   selected-country accent and direct values. State 'within the fixed 20-country
   cohort'. Switching metric reranks the same eligible members. Top-10 can omit
   the focus; show that fact rather than silently inserting an extra bar.

## Visual and accessibility choices

- Neutral off-white page, white chart sections, dark slate text, restrained teal
  accents. Use local CSS only. Avoid red/green-only categories. Category palette:
  absolute #007A68, relative #2868B2, flat #856000, equal growth #6B55A1,
  emissions-faster #AD4B1F, GDP-not-growing #667085. Include category text.
- Country palette: #007A68, #2868B2, #9658A4; metric line styles supplement color.
  Source palette: coal #526170, oil #BC7018, gas #287CB8, derived-other #9770AA.
  Accounting palette: territorial #2868B2, consumption #AD4B1F, plus symbol/stroke.
- Use common axes and explicit units, zero origins for amount/ranking/stacked
  charts; GDP and emissions never share raw values on a common numeric axis.
- Keyboard-operable selectors/buttons, focus styles, associated visible labels,
  semantic page headings. Provide expandable HTML data tables and CSV downloads
  as alternatives to hover-only reading; announce coverage/status with aria-live.
- No animation required. No map, autoplay, extra indicators, or online data calls.

## Data, methods, and exports

- Load only the prepared CSV and metadata, verify CSV hash and unique keys on
  application load. App never writes raw or processed analytical input files.
- Missing endpoint/series/pair observations stay missing. Show counts and country
  names when excluded; no stale-year fallback. Do not display missing as zero.
- Methods section documents formulas, baseline, fixed-cohort selection, units,
  source residual, numerical categories, source links and interpretation limits.
  Include the recorded underlying-source attribution and incomplete release-audit
  items honestly. Local preview does not finish the distribution audit.
- Each Plotly graph has PNG export and reset axes. Download filtered annual CSV
  for the active tab: focus/comparison countries and selected period for Growth;
  cohort at selected snapshot for Footprints. Preserve empty fields for missing.
  Native file-save handling is required for the desktop build; browser download
  behaviour alone is insufficient.

## Acceptance tasks for this iteration

- Default displays match prepared values; baseline rebases at selected start;
  exact endpoint changes and source-change summary agree with calculations.
- Click/select focus and add comparisons; all three first-tab views stay in
  sync, maximum three trend countries, tab switches retain state, reset restores.
- Metric switch reranks the same eligible cohort; top-10/all-20 never changes
  membership. Snapshot 2024 explicitly lacks consumption data while ranking works.
- Test missing intermediate sources/series without connecting gaps or filling.
- Exercise callbacks over HTTP and a real rendered native window. Check PNG/CSV
  save, methods/data access, local-only assets, small/large window layouts, and
  clean server shutdown. Record actual outcomes, not intended outcomes.
- Rebuild and smoke-test the macOS app with bundled prepared data and assets.
  Windows single-file runtime delivery and independent-platform testing remain
  Step 9; do not claim final release readiness from the local Mac preview.

## Implementation review record — 2026-11-02

Both views are implemented with the stated defaults. Native radio navigation
replaces Dash's non-semantic tabs while retaining the two-view layout. Dropdown
triggers include their visible control label and selected value in their
accessible names. Cloud sharing is removed from Plotly's modebar. PNG exports
include country/cohort, period/year, and units within the figure.

Executed checks: 21 data/dashboard tests; rendered Mac source and bundled-app
smoke checks; real CSV and PNG Save dialogs; browser layout at 800x600 and
1440x900 with no horizontal page overflow after resize settles. At 800x600 the
chart columns stack. Full native preview was visually inspected at 1380x900.
Formal screen-reader, contrast, independent-user and Windows evaluations remain
for final acceptance. The user has not yet reviewed this working version.

Additional native window testing found collapsing graph heights after updates
and resizing in WebKit. Graph hosts now have explicit figure-derived heights
updated alongside their figures. The rebuilt Mac app passed nine rendered
geometry checks covering both views at 800x600/1380x900, filter changes, restored
accounting pairs and reset, with no chart overflow. Manual ranking clicks,
2024/per-capita/all-20 controls, CSV/PNG saves, cancellation, data/methods panels
and reset passed. Arrow-key view switching passed after Option-Tab focused the
radio controls under this Mac's native keyboard settings. See Step 9 in
`plan.md` for evidence and the still-unverified Windows release requirements.
