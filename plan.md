# Green Decoupling: working plan and decision log

Last updated: 2026-11-04

This file is the shared record for discussing, deciding, implementing, and
checking each stage of the Information Visualization project. The original
[team proposal](docs/proposal/Project%20Plan.pdf) remains unchanged. Its research
questions and source choices guide this plan; they are not findings or an
official course rubric. The original two-source proposal is retained as history;
D007 supersedes its data integration strategy for the current implementation.

**Workspace relocation — 2026-11-04:** at the user's explicit request, move the
project from `2026-WS/information-visualization/projects/green-decoupling/` to
`2026-WS/visual-data-science/projects/green-decoupling/`. Keep the standalone public
repository and the University workspace's submodule relationship, update the
workspace and clone instructions, and push the updated University repository.
Preserve the original proposal and existing project decisions. This changes the
workspace location; dashboard behaviour and release status are unchanged.
The submodule resolves from the new directory. Updated 28 ignored local virtual
environment launch/config files containing the old absolute path; `pip` resolves
to the relocated environment. All 21 data/dashboard tests passed from the new
location (`outputs/relocation-tests.log`).

## How we work through each step

1. Discuss the current step, its options, and the recommendation.
2. Inspect documentation or data and make small sketches as needed to inform the
   decision. Discussion and investigation do not authorize implementation.
3. Agree on the choices with the user, then record them in this file with the
   date, rationale, and relevant scope or limitations.
4. Implement only the agreed work after its decisions have been recorded. The
   user's agreement authorizes that work; an additional confirmation is not
   required unless the scope changes.
5. Record what actually changed and the checks actually performed. Review the
   result together before marking the step complete and opening the next step.

Recommendations remain proposals until agreed. Do not silently resolve open
choices, mark unexecuted checks as passed, or start later implementation stages.
If a decision changes, retain the earlier entry, mark it superseded, and record
the replacement and any affected work.

Statuses: **Discussion**, **Ready** (agreed decisions recorded),
**Implementing**, **Review**, and **Complete**.

## Confirmed requirements

| ID | Agreed requirement | Basis and limits |
| --- | --- | --- |
| D001 | Code the application in Python using libraries; do not use Power BI or ready-made dashboard platforms. | User's description of the course rule. Exact libraries remain to be agreed. |
| D002 | Deliver `GreenDecoupling.app` for macOS and `GreenDecoupling.exe` for Windows from a shared codebase. | Explicitly agreed by the user. Supported OS versions, processor architectures, and distribution wrappers remain open. |
| D003 | No deadline is currently known. | User reported no deadline for now; do not invent milestone dates. |
| D004 | Discuss each stage and document its agreed decisions before implementing that stage. | Explicitly requested by the user. |
| D005 | Submit exactly one Windows `.exe`, with dependencies bundled inside it or installed through launching it. | User clarified the submission expectation on 2026-11-02. A ZIP or separately supplied support files do not meet this requirement. Standalone execution versus a single-file installer remains to be chosen. |
| D006 | Aim first for a directly launching standalone Windows executable; discuss an installer fallback if dependencies require it. Proceed to the Step 2 discussion. | User accepted the explanation of single-file packaging and requested the next step on 2026-11-02. This does not approve a framework, offline mode, or implementation yet. |
| D007 | Use only the Our World in Data CO₂ and Greenhouse Gas Emissions Dataset (`owid-co2-data.csv`). Do not add World Bank WDI or another analytical dataset. | Explicit user instruction on 2026-11-02. Supersedes the original proposal's two-source integration strategy. Select questions and variables from this dataset's verified contents and coverage; additional sources would require a new scope decision. |
| D008 | Use Python with pandas, Plotly, Dash, pywebview, and PyInstaller; proceed with the minimal packaging prototype. | User explicitly agreed to the suggested technologies and asked to proceed on 2026-11-02. This approves the technical prototype, not the final charts, analysis period, or supported OS matrix. |
| D009 | Retain P001's four core questions (Q1-Q4) and its two-tab concept with approximately six linked chart panels as the dashboard direction. | User said they liked the current ideas and wanted to keep them on 2026-11-02. The exact measures, time period, country eligibility, chart specifications, and interaction details remain for Steps 3, 4, and 6. |
| D010 | Use 1990-2022 inclusive as the shared default analysis period. Emissions-only views may offer newer available years with explicit coverage labels. | User agreed to this approach and requested documentation and the next step on 2026-11-02. GDP-based comparisons must stay within available GDP coverage; accounting comparisons must use matching years. This is a default, not a requirement that every entity have complete data for every variable and year. |
| D011 | Focus on a shortlist of major emitting countries/territories (approximately 10 or 20), retaining aggregate/historical-union exclusions. Determine availability per question and use matching-year comparisons. Choose missing-data treatment case by case for each measure/view. | User's four-part reply on 2026-11-02 accepts question-specific eligibility and comparable-year handling, narrows the broad country scope, and qualifies the proposed uniform missing-data approach. Exact shortlist size, ranking metric/reference year, and per-case missing-data strategies remain open. No blanket imputation rule is approved. |
| D012 | Select the top 20 eligible individual countries/territories by total territorial CO₂ (`co2`) in 2022. Keep cohort membership fixed across years and metric changes, with question-specific availability. Label rankings as within this selected cohort; retain an optional top-10 display direction for dense ranking panels. | User explicitly agreed to the proposed top-20 rule and requested the next step on 2026-11-02. This resolves P003. Any top-10 display limit must not redefine the underlying study cohort. |
| D013 | Adopt P004's four measure definitions: endpoint GDP/territorial CO₂ percentage changes and baseline-100 trends; territorial versus consumption totals and their difference; total versus per-capita rankings within the selected cohort; and a coal/oil/gas/derived-other source breakdown. | User agreed to the proposed measures and grouped Q4 breakdown on 2026-11-02. Preserve matched observations, scope and units, positive-baseline/denominator requirements, and the question-specific missing-data rules documented in P004. The derived remainder is distinct from published `other_industry_co2`. |
| D014 | Approve P005 reproducible preparation and keep the original OWID snapshot in a read-only folder. Write derived tables and validation reports separately; verify source hashes before and after preparation. | User explicitly approved P005 and requested a read-only main dataset on 2026-11-02. This authorizes Step 5 implementation, not the final dashboard. |
| D015 | Arrange Growth & Emissions with the GDP/CO2-change scatterplot across the top, followed by the indexed GDP/CO2 trend and source-composition trend underneath. | On 2026-11-02 the user accepted the proposed chart ordering. Country selection, controls, exact encodings, and the second-tab layout remain discussion items. |
| D016 | Accept P007 interaction controls: focus-country selection by search/chart click; up to three countries in indexed comparison trends; separate analysis-period and snapshot-year controls; total/per-capita ranking switch; Mt/share source switch; top-10/all-20 ranking display; hover details, zoom, and reset. | User explicitly agreed to the discussed project choices and requested documentation and the next step on 2026-11-02. Keep the fixed cohort and exact-year/missing-data rules. Initial country selections, focus/comparison synchronization, detailed encodings, exports, and cross-tab state remain to be specified. |
| D017 | Accept P008 main scatterplot: GDP percentage change on the horizontal axis, territorial CO2 percentage change on the vertical axis, equally sized country marks, category colors, zero/equal-growth references, selected-country emphasis, and detailed hover values. | User agreed to the scatterplot recommendation and requested the next step on 2026-11-02. Preserve matching endpoints, descriptive categories, fixed-cohort context, and unavailable-data reporting. Exact palette and remaining accessibility/default-state choices are still to be specified. |
| D018 | Accept P009 indexed GDP/CO2 trend: year on the horizontal axis, a shared linear index with selected start year = 100 on the vertical axis, solid GDP/dashed territorial-CO2 lines, country colors, up to three displayed countries, a baseline reference, hover values, and visible missing-data gaps. | User agreed to the trend-chart design and requested the next step on 2026-11-02. Initially show the focus country alone. Changing the selected start year rebases the series; zoom does not. Exact country defaults, synchronization, palette, and readability checks remain to be specified. |
| D019 | Accept P010 source-composition panel: a stacked area chart for the focus country over the selected period, with coal/oil/gas/derived-other layers, Mt CO2 by default and a percentage-share switch, detailed hover, endpoint-change summary, and gaps for unavailable breakdowns. | User agreed to the stacked-area recommendation and requested the next step on 2026-11-02. Preserve the derived residual definition, complete-stack accounting, positive-total share rule, and distinction between emissions shares and energy shares. Exact colors and remaining shared-control/default specifications remain open. |
| D020 | Accept P011 territorial/consumption paired-dot chart with country rows, matched-year Mt values, distinct symbols, signed-gap ordering, hover values, and linked focus selection. | User agreed on 2026-11-02. Preserve exact-year eligibility and interpretation limits. |
| D021 | Delegate all remaining version-1 UI choices to the assistant's recommendations, document those defaults, and proceed to implementation without further individual UI approvals. | Explicit user instruction on 2026-11-02: use the suggested UI choices for the first version and revise after trying it. Defaults in docs/dashboard-design.md are accepted under this delegation, not individually reviewed decisions. This authorizes both agreed tabs for the first reviewable version; final release/platform validation remains separate. |

All twenty-one requirements were recorded on 2026-11-02. The technology stack, four
core questions, high-level dashboard direction, and default period are approved.
The major-emitter shortlist direction and question-specific eligibility are
agreed; D012 fixes the shortlist selection rule and D013 approves the core
measures and their missing-data treatment. Final offline requirements, detailed
chart specifications, and final release requirements remain open. D014 approves
reproducible preparation and raw-data protection. The official
brief, rubric, and AI-use policy have not been supplied; apply them when available
and record any resulting changes.

## Progress

The project scaffold, original proposal copy, and public GitHub repository already
exist. The project is linked into the university workspace as a Git submodule.
A minimal technical prototype has been implemented and its macOS build tested
on the development Mac. The approved real-data preparation pipeline is now
implemented and validated. The original OWID snapshot is read-only and unchanged.
Final source-attribution checks remain open. Both dashboard tabs are now
implemented as a reviewable first version. The Windows executable and final
release acceptance have not been verified.
The approved top-20 cohort has now been materialized in
`config/analysis_selection.json` and its core-variable coverage verified.

| Step | Stage | Status |
| --- | --- | --- |
| 1 | Delivery requirements and scope | Complete for prototype scope; deferred details listed below |
| 2 | Technology choice and packaging prototype | Partial verification: Mac prototype passes; Windows build/runtime checks outstanding |
| 3 | Dataset audit and selection | Core cohort and variable choices agreed/verified; source/license audit remains open |
| 4 | Analytical definitions | P004 accepted in D013; numerical handling documented in D014 and implemented |
| 5 | Reproducible data preparation | Complete: validated implementation reviewed; user requested the next step |
| 6 | Dashboard design and interaction specification | Complete for version 1: D015-D021; remaining defaults documented under delegated approval |
| 7 | First complete dashboard view | Review: version 1 implemented; calculations/callbacks/native Mac checked |
| 8 | Remaining views and shared interactions | Review: second tab and shared controls implemented; review together in version 1 |
| 9 | Evaluation and final releases | Not started |

## Step 1: Delivery requirements and scope

**Discuss and decide**

- Confirm the interpretation of the course restrictions and add any available
  official brief, rubric, submission rules, or AI-use requirements under `docs/`.
  Distinguish documented rules from working assumptions if details are unavailable.
- Choose supported Windows and macOS versions and architectures, including
  whether macOS must support Apple Silicon, Intel, or both.
- Decide whether the application must work offline and whether installation of
  supporting runtimes is acceptable.
- Windows submission must be exactly one `.exe` (D005). Choose between an
  application that launches directly and a single-file installer that handles
  required dependencies. Decide the distribution wrapper for the macOS `.app`.
- Confirm the intended audience, main exploration tasks, and minimum submission
  contents, including any report or demonstration requirements.

**Recommendation:** an offline desktop dashboard with the selected OWID data
bundled. Following D007, revise the original research areas to match variables
available within this single dataset; the final questions remain pending.

**After decisions:** record the delivery checklist here and identify the machines
or build services and physical/virtual test systems available for each platform.

**Complete when:** the delivery target and any unresolved course assumptions are
explicit, and the next stage has a usable packaging target.

**Decision record:** D001-D003 establish the original requirements; D005 adds the
single-file Windows submission constraint, and D007 narrows the data scope to the
OWID CO₂ dataset. The user clarified that dependencies
must be inside the executable or installed by launching it. The earlier proposed
Windows ZIP with supporting files is rejected by this requirement.

**Original packaging recommendation, subsequently accepted as the preferred
target in D006:** aim for a directly launching
single-file application with Python, selected libraries, prepared data, and local
visual assets bundled. If the chosen desktop renderer needs an external runtime,
evaluate bundling that runtime or including its installer inside the submitted
executable. Do not assume PyInstaller automatically bundles every system runtime.
Temporary extraction at launch is compatible with a single submitted file;
internet access, installation permissions, and startup time remain design choices.

**Review outcome (2026-11-02):** the delivery formats and preferred Windows launch
experience provide a usable packaging target. Step 1 is complete for proceeding
to Step 2 discussion, as requested by the user. This does not mean all original
questions are resolved. Offline behaviour, supported OS versions/architectures,
runtime installation, and the macOS distribution wrapper are carried into Step 2
before prototype implementation. Course policy and final submission/report
details remain open and must be revisited when available. No packaging has been
implemented or tested.

## Step 2: Technology choice and packaging prototype

**Discuss and decide**

- Compare Python library options against the agreed interactions and delivery
  requirements. Current proposal: pandas, Plotly, Dash, pywebview, and PyInstaller.
- Choose the desktop window approach, dependencies, and local application
  lifecycle. If a local server is used, include startup, shutdown, and port handling.
- Choose per-platform build methods and a reproducible dependency setup.
- Resolve runtime prerequisites, such as WebView2 for a chosen Windows renderer,
  against Step 1's installation and offline requirements. Validate D005 with only
  the submitted `.exe` available on the Windows test system, including a case
  where any optional runtime is absent.
- Settle Step 1's deferred compatibility and offline choices before implementing
  the prototype. The inspected development machine is Apple Silicon (`arm64`),
  running macOS 26.6; this is an observed environment, not an approved support
  promise. Windows testing availability has not been established.

**Technology recommendation, accepted in D008:** Python with pandas for data work,
Plotly for charts, Dash for Python-defined layout and linked chart interactions,
pywebview for the desktop window, and PyInstaller for packaging. Use bundled
demonstration data and local chart assets to test offline operation. Start with
the available Apple Silicon Mac and propose Windows 11 x64 as the first Windows
target; additional OS versions and Intel Mac support need explicit selection.
Choose and verify a desktop rendering backend that meets D005; do not assume
Python dependency bundling also resolves system runtime prerequisites.

**After decisions:** build the smallest application containing one interactive
chart and clearly labelled demonstration data. Package it for both selected
platforms before building the full dashboard. Demo data is not research evidence.

**Complete when:** both prototype builds launch and the chart works on the target
systems, including offline operation if required. Record environment, build
commands, prerequisites, and observed results. A successful build alone is not
evidence of a successful launch.

**Decision record:** D008 approves the stack and proceeding with the small
prototype. Technical implementation choices: a localhost-only server with an
automatically allocated port, an embedded desktop window, one interactive chart
and selector, clearly labelled synthetic demonstration values, and locally served
assets. These choices test packaging rather than define analytical results or
final dashboard design. Start development on the inspected Apple Silicon Mac;
do not imply Windows or other Mac configurations have been tested.

Final platform support, Windows runtime delivery, macOS distribution wrapper,
and final offline requirements remain open. Bundling demo assets for this
prototype does not settle those final product requirements. Record actual
implementation and verification results below when available.

**Implementation and verification (2026-11-02):**

- Added `src/visualization/app.py` and `desktop.py`, with a chart, selector,
  synthetic demo values, local assets, an ephemeral localhost port, and server
  cleanup when the window closes. No real CO₂ observations are represented.
- Added pinned direct dependencies in `requirements.txt`, an isolated `.venv`,
  and an exact development-environment snapshot in
  `config/requirements-macos-arm64.lock.txt`. The snapshot is Mac-specific;
  Windows dependencies still require resolution and testing on Windows.
- Added `config/build_prototype.py`: builds a macOS `.app` on Mac or uses
  PyInstaller's one-file mode on Windows. The Windows branch has not been run.
- Ran `.venv/bin/python -m unittest discover -s tests -v`: both tests passed.
  Checks exercised real local HTTP script requests, the filter callback and
  returned values, and release of the server port after shutdown.
- Ran `.venv/bin/python -m pip check`: no broken requirements found.
- Built `dist/GreenDecoupling.app` successfully on macOS 26.6 / arm64 with
  Python 3.12.14 and PyInstaller 6.22.3 (approximately 124 MB on disk).
- Ran the source app and the packaged Mac app with `--smoke-report`. Both
  launched a native desktop window, rendered the initial Plotly chart, updated
  its values through the selector's Dash state, wrote passing reports, and
  exited successfully. Reports: `outputs/prototype-source-smoke.json` and
  `outputs/prototype-macos-smoke.json` (generated local files).
- The browser resource check reported no external HTTP(S) resources. This was
  not a network-disconnected test and does not establish final offline support.

**Remaining before Step 2 is complete:** build and run the single-file executable
on Windows, handle the WebView2 runtime through the agreed single-file delivery
flow, verify behaviour when that runtime is absent, and review the prototype
with the user. Other OS versions, Intel Macs, signing/notarization, and clean
machine distribution are unverified. Do not describe this developer prototype
as a final release or mark cross-platform packaging complete.

## Where we decide what the dashboard shows

- **Step 3:** inspect the one approved dataset, check coverage, and agree on the
  analytical questions and relevant variables. Produce a short question-to-data
  mapping: question, required columns, usable years/countries, and limitations.
- **Step 4:** agree on how each question is measured: totals versus per-capita,
  territorial versus consumption-based accounting, changes, and intensity.
- **Step 6:** turn those agreed questions and measures into charts, layout,
  filters, and linked interactions. Each proposed chart must identify its question,
  measure, encoding, and useful user action.

Do not wait until implementation to choose the research questions. The Step 2
prototype verifies technical feasibility only; its demo chart is not a decision
about the final dashboard.

## Step 3: Dataset audit and selection

**Discuss and decide**

- Inspect only `owid-co2-data.csv` and its codebook/source metadata (D007).
- Identify available variables for territorial and consumption-based CO₂,
  per-capita emissions, GDP, population, carbon/energy intensity, cumulative
  emissions, and emissions by fuel or source. These are candidates, not an
  approved indicator list. Verify exact columns, definitions, units, and licenses.
- Revise questions that depend on renewable shares, manufacturing/services,
  general trade profiles, or population density if the required variables are
  absent. Do not fill those gaps by importing WDI or another dataset.
- Compare country-year coverage and missingness. Start from the proposal's
  interest in 1990 onward; choose the actual period from usable coverage rather
  than assuming all variables reach the same latest year.
- Decide country eligibility, aggregate exclusions, and a manageable core set of
  indicators. Separate essential variables from optional extensions.

**After decisions:** preserve selected source snapshots under `data/raw/`, with
URLs, retrieval dates, releases where available, and attribution requirements.
Record indicator selections in `config/` and the data dictionary and coverage
summary in `docs/`.

**Complete when:** every selected indicator has a verified definition and an
explicit coverage assessment. Missingness must remain visible; do not silently
reduce every view to countries complete on every optional variable.

**Decision record:** the original team proposal named OWID and WDI. D007
supersedes that strategy: only the OWID CO₂ dataset will be used. Exact columns
and country eligibility remain pending audit and agreement. D009 accepts the
four revised research questions below, and D010 sets the shared default period
to 1990-2022 with newer years permitted in eligible emissions-only views.
No external analytical join is planned. Implementation and checks:
no preparation pipeline or final analytical selection yet. The user requested
question recommendations while Step 2's Windows verification remains outstanding;
this discussion does not mark Step 2 complete.

### Preliminary coverage inspection (2026-11-02)

Downloaded the official OWID CSV and codebook, unchanged, to `data/raw/owid/`.
`source.json` records requested/resolved URLs, retrieval time, file sizes,
last-modified headers where supplied, and SHA-256 hashes. Sources:

- [OWID dataset documentation](https://github.com/owid/co2-data)
- [Official CSV](https://owid-public.owid.io/data/co2/owid-co2-data.csv)
- [Codebook](https://raw.githubusercontent.com/owid/co2-data/master/owid-co2-codebook.csv)

The inspected snapshot contains 50,411 rows and 79 columns, covering 1750-2024.
The preliminary country/territory subset uses uppercase three-letter ISO codes
and years from 1990 onward. It includes some historical entities and is not the
final country eligibility rule. Under that filter:

| Measure | Latest non-missing year | Entities with a value in that year |
| --- | --- | --- |
| Territorial CO₂ (`co2`) | 2024 | 215 |
| Territorial CO₂ per person (`co2_per_capita`) | 2024 | 213 |
| Consumption-based CO₂ (`consumption_co2`) | 2023 | 120 |
| GDP (`gdp`) | 2022 | 164 |

At both the 1990 and 2022 endpoints, 117 entities have GDP, territorial CO₂, and
consumption-based CO₂. This checks endpoints only, not complete annual coverage.
GDP comparisons therefore need an earlier end year than emissions-only views.
The original candidate shared default was 1990-2022; this was subsequently
accepted through D010. Other views can offer later years with explicit coverage
labels and matching observations for their comparisons.

Coal, oil, gas, cement, flaring, and other-industry emissions columns are present,
but their missingness differs substantially. Requiring all six source components
would retain only 46 ISO-coded entities in 2022. Do not assume missing components
are zero or claim a complete decomposition without reconciliation. No columns
for renewable shares, manufacturing, or general imports/exports were found.
No duplicate country-year keys were found in the snapshot.

These are feasibility observations, not substantive findings about countries or
completion of the metadata/license audit. Detailed output is in
`outputs/owid-preliminary-coverage.json` (generated local evidence).

### Analytical questions: P001 (accepted through D009 on 2026-11-02)

The original recommendation was **four core questions**, with about six linked
chart panels across two tabs. The user accepted these ideas on 2026-11-02:
"I like the current ideas and I want to keep them" (spelling normalized).
D009 records the agreement. This is the selected project scope and design
direction; exact layout and chart specifications remain for Step 6.

| ID | Agreed question | Why include it | Candidate data and visual treatment |
| --- | --- | --- | --- |
| Q1 | Which countries have grown their economies while reducing territorial CO₂ emissions over the selected period? | Central question for the Green Decoupling project; distinguishes total emissions reductions from improved intensity alone. | `gdp`, `co2`, `year`: GDP-change versus CO₂-change scatterplot with zero lines, linked to an indexed country time series. Use real total GDP and total emissions; evaluate the selected period rather than presume every country has reduced emissions. |
| Q2 | How do a country's footprint and trend change when emissions are counted by consumption rather than domestic production? | Tests whether domestic reductions are also visible under consumption-based accounting. | `co2`, `consumption_co2` and their per-capita counterparts: paired-dot comparison plus a selected-country time series. Compare matching countries and years; an accounting gap alone does not prove industrial relocation. |
| Q3 | How does the ranking of high-emitting countries change when we compare total emissions with emissions per person? | Gives scale and population context, complementing the growth and footprint questions. | `co2`, `co2_per_capita`: sorted horizontal ranking with an explicit total/per-capita switch. Label the units and allow comparison of selected countries on a consistent eligible set. |
| Q4 | Which fuel and industrial emission sources account for the observed changes in a selected country's territorial emissions? | Adds compositional detail about where emissions changed, using variables inside the approved dataset. | `coal_co2`, `oil_co2`, `gas_co2`, `cement_co2`, `flaring_co2`, `other_industry_co2`: source trends with absolute/share modes. Restrict to available comparable components and reconcile before attributing the total change; otherwise describe observed source changes without claiming full accounting. |

Accepted high-level grouping; detailed design remains for Step 6:

- **Growth & emissions:** Q1 scatterplot, Q1 indexed trend, Q4 source trends.
- **Footprints & comparison:** Q2 paired-dot comparison, Q2 accounting trends,
  Q3 total/per-capita ranking.

Shared country selection and time controls should connect the panels. Each view
must show its actual coverage; do not silently use different years in a single
cross-country comparison. Historical cumulative emissions, land-use change, and
energy-intensity decomposition remain possible later extensions, outside P001's
four core questions. Do not add them as separate main questions without review.

**Decision recorded:** retain Q1-Q4 and the two-tab, approximately six-panel
concept (D009). No analytical implementation is authorized merely by accepting
the ideas; discuss and record the applicable data and calculation choices first.

**Decision recorded:** the shared default period is 1990-2022 inclusive (D010).
Newer years may be offered in emissions-only views when supported by their
variables, with visible year/coverage labels. Do not silently compare countries
using different years or extend GDP by carrying its last observation forward.

**Next decisions:** settle country eligibility, chart-specific availability rules,
and exact variables in Step 3, then the analytical formulas and detailed
missing-data behaviour in Step 4. Final chart behaviour and layout remain for
Step 6. Step 3 is not complete until its remaining choices and source/metadata
checks are resolved.

### Country eligibility and missing data: P002 (amended through D011)

The following bullets preserve the original proposal. D011 records the user's
subsequent acceptance and amendments below; the original broad country scope and
uniform missing-data recommendation do not override those amendments.

- Make individual countries and territories available, subject to data coverage;
  exclude World, regional/income-group aggregates, and historical unions from
  country comparisons. Review the entity classification against the OWID
  snapshot/metadata rather than relying solely on a three-letter-code regex.
- Determine eligibility separately for each question. Do not restrict the entire
  dashboard to countries complete on every variable. Q1 needs GDP and territorial
  emissions at the selected endpoints; Q2 needs both emissions accounting
  measures for matching years; Q3 needs both total and per-capita values for a
  consistent ranking comparison; Q4 depends on the reported source components.
- Keep missing values missing. Do not substitute zero, carry observations
  forward, or interpolate by default. Show unavailable comparisons, gaps, and
  excluded-country counts explicitly. Decide detailed chart behaviour in Steps
  4 and 6; incomplete source components cannot support a claimed full breakdown.
- Allow exploration across eligible countries and selection of a small group for
  readable detailed comparisons. Exact initial selections and selection limits
  belong to Step 6, not to the analytical eligibility rule.

**Agreed outcome (D011, 2026-11-02):**

- Focus on a manageable shortlist of the most significant emitters, approximately
  10 or 20. Retain the individual-country/territory approach and exclusions for
  World, regional/income aggregates, and historical unions. The exact definition
  of "top" and shortlist size have not been decided.
- Assess data availability separately for each question; missing consumption
  observations do not exclude a country from unrelated views.
- Use a case-specific missing-data strategy for each measure/view rather than a
  universal interpolation or exclusion rule. Preserve raw missingness; agree and
  document any derived-data imputation, structural-zero interpretation, or
  exclusion, and distinguish estimated values from observations. No specific
  imputation technique has been approved.
- Make gaps/unavailable comparisons visible and use matching years in country
  comparisons. This follows the user's acceptance of the comparison approach.

**Shortlist definition: P003 (accepted through D012 on 2026-11-02)**

- Use the top **20** eligible individual countries/territories ranked by total
  territorial CO₂ (`co2`) in **2022**, the last shared default analysis year.
- Fix that cohort across the default period and metric changes. Values and
  rankings may change with the selected year or measure, but cohort membership
  does not silently change. Per-question data availability still applies.
- Label Q3's per-capita rankings as rankings **within the selected major
  emitters**; this cohort is not necessarily the world's top 20 per-capita
  emitters. Findings about this sample must not be generalized to all countries.
- Discuss a top-10 display option for dense ranking panels during Step 6 without
  confusing a display limit with the underlying study cohort.

**Decision recorded:** D012 accepts N=20, total territorial CO₂ as the ranking
metric, reference year 2022, and fixed cohort membership. Materialize this agreed
selection from the preserved snapshot and inspect coverage before specifying
the measures. Exact variable/unit choices and source/license checks still need
to be documented before Step 3 can be completed; per-measure missing-data rules
follow in Steps 4 and 5.

**Selection implementation and checks (2026-11-02):**

- Saved the approved selection rule, source SHA-256, default period, ranked ISO
  codes, country names, and reference emissions in `config/analysis_selection.json`.
- The resulting cohort, in selection-rank order, is China, United States, India,
  Russia, Japan, Iran, Indonesia, Germany, Saudi Arabia, South Korea, Canada,
  Brazil, Mexico, Turkey, South Africa, Australia, Italy, Vietnam, Poland, and
  United Kingdom. Reviewed these selected names as individual current entities;
  no aggregate or historical union is in the list. The initial three-letter
  filter was candidate generation, not the sole entity-classification check.
- Independently reproduced the pandas ranking with Python's standard-library CSV
  reader and numeric sorting; the ordered ISO-code lists match exactly.
- Verified 660 unique country-year rows (20 entities x 33 years) for 1990-2022.
  GDP, territorial and consumption-based CO₂, both per-capita emissions columns,
  and coal/oil/gas emissions are non-missing throughout this selected period.
- Detailed source components have gaps: other-industry emissions are missing in
  all 33 years for India, Indonesia, Iran, Mexico, Saudi Arabia, South Africa,
  and Vietnam. Flaring is missing in four years each for China, South Africa,
  and South Korea. These are not interpreted as zero.
- For the proposed grouped Q4 measure only, inspected the residual
  `co2 - coal_co2 - oil_co2 - gas_co2`. It is non-negative in all 660 rows
  (approximately 1.117-1017.607 Mt). This is a feasibility check, not agreement
  to implement the residual as a production measure or evidence about its causes.

At the user's request to proceed, open Step 4's measure discussion using this
verified core selection. Step 3's metadata/license checklist remains open and
must be resolved before final preparation/distribution; opening the discussion
does not assert that the full audit is complete.

## Step 4: Analytical definitions

### Measures and missing-data treatment: P004 (accepted through D013 on 2026-11-02)

Use the dataset's fossil-fuel and industrial CO₂ scope, excluding land-use change,
for the main comparisons. Keep land-use-inclusive columns separate. OWID's GDP
column is total real GDP adjusted for inflation and purchasing power, measured
in international dollars at 2011 prices, according to the preserved codebook.

| Question | Agreed measures | Agreed missing-data and interpretation rules |
| --- | --- | --- |
| Q1: growth and emissions | Percentage change in total real GDP and territorial CO₂ between the selected endpoints: `100 * (end / start - 1)`. Selected-country trends indexed to 100 at the chosen start: `100 * value / start`. | Require valid, positive baselines and matching endpoints. Missing endpoints make the change unavailable; do not substitute another year or estimate GDP. Break trend lines at missing years. Valid intermediate gaps need not invalidate an endpoint-only change. Use total GDP and total emissions for national decoupling. |
| Q2: accounting footprints | Published territorial and consumption totals in Mt, with accounting gap `consumption_co2 - co2`. Positive values mean a larger consumption footprint; negative values mean a larger territorial footprint. | Use matched observations for the same country/year. If either total is missing, the paired comparison and gap are unavailable. Retain raw gaps; do not infer industrial relocation or causation from their sign. Optional per-capita comparisons use the corresponding published columns consistently. |
| Q3: total versus per-capita ranking | Published `co2` in Mt and `co2_per_capita` in tonnes/person. Rank the fixed D012 cohort using one selected year and the same eligible entities for both metrics. | Show unavailable values and eligible counts; do not use stale values from different years or label the per-capita result a global top-20 ranking. Published values are available for all selected entities during the default period. |
| Q4: source changes | Four comparable groups: coal, oil, gas, and **other fossil/industrial sources (derived)**. Compute the fourth as `co2 - coal_co2 - oil_co2 - gas_co2`. This residual includes cement, flaring, and other contributions/adjustments within the total; it is not the published `other_industry_co2` column. Show Mt or each group's share of total CO₂, with percentage-point or Mt changes as appropriate. | Require total and all three fuel values for the grouped calculation. Missing required values make that year's full breakdown unavailable. A negative residual requires investigation rather than silent clamping. Only compute shares for a positive total. Do not replace missing detailed industrial/flaring values with zero. Label the residual as derived; individual detailed source series can remain visible where observed, without claiming they exhaust the total. |

For Q1, propose these descriptive labels over the chosen period:

- **Absolute decoupling:** total real GDP increases and territorial CO₂ decreases.
- **Relative decoupling:** both increase, but emissions grow more slowly than GDP.
- **GDP growth with flat emissions:** a separate category rather than silently
  combining it with declining emissions.
- If GDP does not grow, show its observed trajectory without classifying it as
  growth-based decoupling. Specify numerical tolerance/rounding before coding
  boundary classifications; no arbitrary threshold has been agreed yet.

The grouped Q4 proposal retains the user's interest in industrial sources while
avoiding a false assumption that missing detailed categories equal zero. It does
not measure renewable shares or establish causes of emissions reductions.

**Decision recorded:** D013 accepts P004's four measure definitions, including
the grouped Q4 residual, after the user agreed to the proposed measures. Do not
reopen these agreed definitions without a reason or a user-requested change.
The dashboard still uses a labelled synthetic packaging prototype. D014 records
numerical handling before implementation of reusable data measures in Step 5;
no interpolation or significance threshold is introduced.

**Discuss and decide**

- Verify the GDP basis and population definitions within the OWID dataset and
  distinguish total from per-capita measures. Check compatibility with existing
  OWID ratios before calculating derived measures; do not introduce external GDP.
- Define emissions coverage, carbon intensity, percentage changes, baseline-year
  indexing, and the consumption-minus-territorial emissions gap, with units.
- Define absolute and relative decoupling, the selected time window, and treatment
  of flat values, small changes, missing endpoints, and invalid denominators.
- Apply D011 by specifying missing-data treatment for each measure/view:
  endpoint-based changes, within-country trends, paired accounting comparisons,
  rankings, and source-component totals may require different strategies. Record
  the rationale, any estimation limits, and how affected values are labelled.
- Distinguish emissions by fuel from energy generation or consumption shares.
  A fuel's share of CO₂ is not its share of energy. Do not claim to measure
  renewable adoption or industrial structure without the necessary variables.
- Agree on interpretation limits: correlations and footprint gaps alone do not
  establish causal mechanisms or prove industrial relocation. Renewable adoption
  and outsourcing need not be mutually exclusive or exhaustive explanations.

**After decisions:** document formulas and interpretation rules under `docs/`
before implementing derived measures.

**Complete when:** each displayed analytical measure can be reproduced from its
definition, including its missing-data and comparison rules.

**Decision record:** P004's core measures and per-question missing-data rules are
accepted through D013. Feasibility/coverage inspection is recorded above.
Numerical boundary handling is now recorded in D014; the reusable analytical
implementation and checks are recorded in Step 5.

## Step 5: Reproducible data preparation

### Proposal P005: preparation approach (approved through D014)

- Keep the downloaded CSV/codebook unchanged and verify their recorded hashes.
  Read the fixed D012 cohort from `config/analysis_selection.json` rather than
  recalculating a different top 20 when the user changes a chart filter.
- Build one prepared country-year table with the approved input columns,
  accounting gap, grouped source values/shares, and explicit availability flags.
  Store generated data under `data/processed/` and a compact validation summary
  under `outputs/`. Retain source/units/provenance information with the outputs.
- Preserve available observations from 1990 onward for the approved newer-year
  emissions-only option; default to 1990-2022. Keep GDP/accounting values missing
  beyond their own coverage instead of extrapolating them.
- Compute endpoint changes and baseline-100 series from the user's selected
  period when requested. Do not hard-code 1990 as the only possible baseline or
  allow a display filter to silently alter cohort membership.
- Check country-year uniqueness, required columns and units, positive baselines
  and denominators, matching observations, source reconciliation, and missingness.
  Investigate negative source residuals rather than silently clamping them.
- Verify consequential calculations with independent hand-worked examples and
  meaningful edge cases. Document one rebuild command, preserve raw inputs, and
  report only checks actually executed.

**Decision D014 — 2026-11-02; Step 5: Review.** The user accepts P005 and
specifically requests read-only preservation of the main dataset. Set raw files
to mode `0444` and their OWID directory to `0555`; do not modify or redownload the
snapshot. Git does not retain these permission bits, so protection must be
reapplied on a fresh checkout/download. Hash checks detect changed inputs even
where permissions can be overridden by the file owner.

Implementation clarifications within the approved measures:

- Use strict comparisons of unrounded endpoint changes for descriptive Q1
  labels. Exactly zero is flat; there is no substantive deadband or significance
  threshold. Display rounding must never determine the category. Equal positive
  GDP/emissions growth is labelled equal growth; faster emissions growth is
  distinguished from relative decoupling. Missing/invalid endpoints are unavailable.
- Write `data/processed/country_year.csv` and `metadata.json`, and
  `outputs/data-validation.json`. Retain published columns, explicit availability
  flags, derived accounting gaps, the derived residual, and source shares.
  Include a full cohort/year grid so absent years stay visible as gaps.
- Before local preparation, check snapshot hashes, codebook units, source names,
  and coverage. Distribution attribution is a release gate: OWID material is
  CC BY, third-party data retain their own terms. Record verified sources and
  outstanding source-specific attribution without claiming the release audit is
  finished. This separates reproducible local preparation from final redistribution;
  it does not authorize adding another analytical dataset.
- Fail validation for a negative residual rather than clamp it. Check the
  published per-capita values against total/population using a 0.1% relative
  tolerance (plus 0.000001 tonnes/person absolute tolerance) for reconciliation
  only; never replace published values with the check calculation.

**Discuss and decide:** country/aggregate handling, missing-data rules,
output schema, validation checks, and how to rebuild from preserved source data.
Any interpolation must be explicitly justified and agreed.

**After decisions:** implement preparation in `src/data/`, configuration in
`config/`, meaningful data checks in `tests/`, and generated datasets in
`data/processed/`. Preserve raw inputs unchanged.

**Complete when:** a documented command rebuilds the prepared data from OWID, duplicate
country-year keys and unit inconsistencies are checked, missingness and exclusions
are reported, and derived measures are checked against independent hand-worked
examples. Record executed checks and their results.

**Decision record:** D014 approves P005, including the user's explicit request
for a read-only original dataset. Implementation is ready for user review.

**Implementation and executed checks — 2026-11-02**

- `src/data/prepare.py` reads the protected snapshot and fixed cohort, validates
  hashes/units/keys/domains, and writes the prepared CSV, metadata, and validation
  report. `src/data/measures.py` handles selected-period changes, explicit-gap
  indexed trends, descriptive labels, and matched-cohort rankings.
- All original OWID files are mode `0444`; `data/raw/owid/` and its parent
  `data/raw/` are mode `0555`. Original CSV and codebook SHA-256 hashes match
  their recorded values before and after the real-data rebuilds. The provenance
  JSON and original proposal were not edited.
- Command: `.venv/bin/python -m src.data.prepare`. Observed result: **700 rows,
  20 countries, 1990-2024**. The default 1990-2022 grid has **660 rows** with no
  missing approved numeric inputs. Newer years retain actual coverage: GDP is
  unavailable after 2022, consumption accounting after 2023; territorial CO₂
  and grouped sources continue through 2024. No analytical observations filled.
- Domain, matching, per-capita reconciliation, four-source recomposition, and
  share-sum checks passed. No negative residuals were found. The residual stays
  explicitly labelled as derived and distinct from `other_industry_co2`.
- Command: `.venv/bin/python -m unittest discover -s tests -v`. **14 tests passed**:
  12 data/measure tests plus 2 existing prototype HTTP/callback/shutdown tests.
  Cases cover hand-calculated changes and shares, changing baselines, absent
  endpoints/intermediate years, nonpositive baselines, zero totals, strict
  boundary categories, matched ranking eligibility, invalid schemas/keys,
  non-finite inputs, negative residuals, per-capita inconsistencies, altered
  hashes/units/permissions, raw-output path protection including symlinks, and
  deterministic preparation with unchanged fixture inputs.
- Full-snapshot integration checks confirmed all 20 countries are eligible for
  Q1 in 1990-2022, all 660 GDP index values are present for that period, Q1 is
  unavailable for an endpoint in 2024, and all 20 countries remain eligible for
  Q3 in 2024.
- Repeat real-data rebuilds produced byte-identical CSV, metadata, and report
  for unchanged inputs/configuration. Tested on the development Mac with Python
  3.12.14/pandas 3.1.0. Data preparation and file protection have not been tested
  on Windows.
- `config/data_sources.json` records codebook sources, verified Maddison dataset
  and paper DOIs/CC BY 4.0, OWID's third-party terms distinction, and population
  provenance. **The release audit is incomplete:** map Maddison national-source
  citations and finish exact GCB component/UN attribution and reuse checks before
  distributing the final application. No second analytical dataset was added.

**Review boundary:** data preparation is implemented; chart design is Step 6.
No final dashboard UI is approved by D014. Windows packaging/runtime checks remain
outstanding. **Review outcome, 2026-11-02:** following the implementation/checks
summary, the user requested the next step. Step 5 is complete for its approved
local preparation scope; the separately tracked release tasks remain open.

## Step 6: Dashboard design and interaction specification

**Status — Complete for version-1 specifications, 2026-11-02.** Initially the user requested
questions with a recommendation for each. Discuss one decision at a time and
record each accepted answer before implementation. D009 already establishes two
tabs and approximately six charts; retain that direction.

Discussion order:

1. Layout and visual hierarchy within the two agreed tabs.
2. Exact chart encodings, scales, and labels for Q1-Q4.
3. Country selection, defaults, and linked highlighting/detail views.
4. Period versus snapshot-year controls and cross-tab state.
5. Accessible colors, legends, coverage, and unavailable-data messages.
6. Reset, exports, methods/sources access, and window-size acceptance tasks.

### Proposal P006: first-tab layout (ordering accepted through D015)

For **Growth & Emissions**, place the GDP-change versus territorial-CO₂-change
scatterplot across the top. Show the fixed 20-country cohort to provide the
comparison overview. Beneath it, put the indexed GDP/CO₂ trend and the four-source
CO₂ trend side by side as country detail panels. The exact selection behaviour
and number of displayed trend series are subsequent decisions. Stack panels on
narrow windows rather than shrinking chart labels.

Rationale: the overview answers which countries follow different trajectories;
the detail panels then reveal timing and source composition. A large main plot
provides room for 20 country marks and reference lines; subordinate panels limit
competition for attention. An equal-sized three-chart grid is an alternative,
but offers less room for the primary cross-country comparison. The layout is
accepted for chart ordering through D015. D016 accepts the high-level country
selection and interaction controls; precise synchronization and encodings remain
pending.


**Decision D015 — 2026-11-02:** the user accepts the first-tab chart ordering and
asks which controls would make the dashboard interactive. Explain the control
scope before settling detailed chart specifications. No interaction proposal
below is approved merely by accepting the ordering.

### Proposal P007: interactive controls (accepted through D016)

- **Focus country:** searchable selector and equivalent chart click; highlight
  the focus country in the overview and update its detail panels. Keep all 20
  cohort countries in the overview for context.
- **Comparison countries:** optionally compare up to three countries in the
  indexed GDP/territorial-CO2 trend; source composition remains one focus country
  to avoid overlapping fuel breakdowns. Exact focus/comparison synchronization
  and initial selections remain to be decided.
- **Analysis start/end years:** default 1990-2022; update Q1 endpoint changes,
  indexed-trend baseline, and first-tab trend window together. GDP-based controls
  use valid GDP coverage; no silent replacement of selected endpoints.
- **Snapshot year:** distinct second-tab control, default 2022; update accounting
  pairs and total/per-capita rankings for the exact same selected year. Newer
  territorial data must not silently substitute an older consumption observation.
- **Ranking metric:** total Mt versus published tonnes/person for Q3 only, keeping
  the same eligible members. Do not change Q1's agreed total-emissions definition.
- **Source units:** Mt versus percent of total CO2 for Q4 only; shares concern
  emissions, not energy. Country, period, and availability stay explicit.
- **Ranking display size:** optional top 10 versus all 20 display within the frozen
  cohort; this never selects a new global cohort. The control is accepted in
  D016; its initial display size remains to be specified.
- **Supporting interactions:** hover values with units/year, linked country
  highlighting, chart zoom and reset, plus a dashboard reset to agreed defaults.
  Methods/source access and exports will be specified later in this step.

**Decision D016 — 2026-11-02:** the user agrees to the discussed controls and
requests documentation and progression. Accept all seven listed controls and
the supporting hover/click, zoom, and reset interactions. The indexed trend can
display up to three countries; source composition displays one focus country.
All 20 cohort members remain visible in the scatter overview where eligible.
Defaults already specified are 1990-2022 for analysis and 2022 for the snapshot.
Methods/sources access and exports are not settled by this approval. Remaining
initial selections, synchronization behaviour, and exact visual encodings still
need to be documented before the final UI is implemented.

### Proposal P008: main scatterplot specification (accepted through D017)

Accepted design decision, within Step 6:

- Horizontal axis: percentage change in total real GDP over selected endpoints.
  Vertical axis: percentage change in total territorial CO2 over the same period.
  Use linear percentage axes, equal-sized country points, and a period-labelled
  title. The ranking metric switch does not alter these Q1 definitions.
- Show horizontal/vertical zero-change lines and a labelled equality reference
  `CO2 change = GDP change`. For positive GDP growth, below zero CO2 change means
  absolute decoupling; positive CO2 change below the equality line means relative
  decoupling; above it means emissions growing faster than GDP. Equal growth,
  flat emissions, and GDP-not-growing cases retain their approved distinct labels.
  These are descriptive selected-period comparisons, not causal conclusions.
- Color represents the approved descriptive category, with accessible colors and
  explicit text labels in hover/detail information; never rely on color alone.
  Outline/enlarge the focus point and directly label focus/comparison countries;
  show every eligible country's name and values on hover to reduce text overlap.
- Hover includes country, selected years, GDP and territorial-CO2 endpoint values
  with units, both percentage changes, and category. Clicking sets focus; an
  equivalent searchable selector remains available.
- Keep the full fixed cohort in context; missing/invalid endpoints produce an
  explicit unavailable count/list rather than stale years or substituted values.
  Choose exact palette, initial axis padding, overlap handling, and keyboard/data
  alternatives in the remaining accessibility/design specification.

Rationale: position on common axes supports accurate comparison; zero and
same-growth references expose the analytical definitions. Equal point sizes
avoid adding an unrequested magnitude encoding to the two-change comparison.


**Decision D017 — 2026-11-02:** the user accepts the scatterplot specification
and requests progression. Record that agreement before opening the indexed-trend
design below. This does not approve the remaining chart specifications.

### Proposal P009: indexed GDP/CO2 trend specification (accepted through D018)

Recommend a shared-axis line chart in the first tab's lower-left panel:

- Horizontal axis: calendar year within the selected analysis period. Vertical
  axis: index with the selected start year equal to 100 for each observed metric
  and country. Use a common linear index axis, not separate GDP/CO2 scales.
- For the focus country, show total real GDP as a solid line and territorial
  CO2 as a dashed line. A country has one consistent color within this chart;
  line style identifies the metric. This chart's country-color legend is distinct
  from the scatterplot's category-color legend.
- Support up to three displayed countries in total (at most six lines), as agreed
  in D016. Initially show only the focus country; comparison defaults and exact
  focus/comparison synchronization will be settled with the shared controls.
  Use accessible country colors, explicit country/metric legend labels, and
  selected/direct labels where space permits. Review six-line readability in the
  actual lower-panel width; exact palette and overlap handling remain open.
- Include a labelled baseline reference at 100 and show the selected baseline
  year in the title/axis label. Example, explicitly hypothetical: GDP index 150
  and CO2 index 80 mean GDP rose 50% and CO2 fell 20% since the same start year.
  The chart compares proportional trajectories, not the numerical sizes of GDP
  and emissions in their original units.
- Changing analysis start/end updates the series window and selected-start
  baseline. Zoom changes the visible window only and never silently rebases.
- Hover shows country, year, metric, index, and original value with its own units.
  Optional percent-since-baseline is index minus 100, not annual growth.
- Preserve intermediate gaps as broken lines. A missing/nonpositive selected
  baseline makes that metric's indexed series unavailable; report it explicitly
  without substituting a later year. Baseline validity is checked per series;
  other observed series need not be hidden.

Rationale: indexing places different units on a comparable proportional scale;
solid/dashed strokes distinguish GDP and CO2 without relying on color alone.
A single focus country keeps the initial panel readable, while the accepted
comparison control supports deliberate exploration.


**Decision D018 — 2026-11-02:** the user accepts the indexed trend recommendation
and requests progression. This settles its core encodings and baseline behaviour;
remaining first-tab chart design is the source-composition panel below.

### Proposal P010: source-composition trend specification (accepted through D019)

Recommend a stacked area chart in the first tab's lower-right panel:

- Show the single focus country over the selected analysis period; horizontal
  axis is year. Four layers are coal, oil, gas, and **other fossil/industrial
  sources (derived)**, in that fixed bottom-to-top order. The fourth is the D013
  residual, not published `other_industry_co2` and not a renewable-energy measure.
- Default to absolute **Mt CO2**, with the accepted switch to **share of total
  CO2 (%)**. In Mt mode the upper envelope shows total territorial fossil/industrial
  CO2; use a zero baseline. In share mode the complete stack totals 100% for
  positive totals. A rising share does not necessarily mean a rising absolute
  amount, and percentage mode conceals changes in total magnitude.
- Assign stable, accessible source colors with visible legend labels and thin
  boundaries. The palette is source-specific and distinct from the scatter's
  category legend and indexed trend's country legend. Choose exact colors during
  the accessibility specification.
- Hover at a year shows all four source names, amounts in Mt, shares, and total,
  with country and year. Label the residual as derived in the legend/tooltip and
  explain its scope through methods information.
- For the selected endpoints, include a compact textual change summary reporting
  each source's end-minus-start Mt change in absolute mode, or percentage-point
  share change in share mode. Missing endpoints make the corresponding summary
  unavailable; do not use nearby years. This supports Q4's change-accounting task
  without adding another chart panel.
- A missing required fuel/total makes the full breakdown unavailable for that
  year; preserve a visible gap in the whole stack. Do not render missing components
  as zero or connect a filled area across an unavailable year. Shares at a zero
  total are unavailable. Preparation already rejects negative residuals.
- Keep all four groups in the stack; legend interaction may highlight a source
  without removing components or renormalizing shares. Country focus, selected
  period, source-unit switch, hover, and zoom provide the interactions. Zoom does
  not alter the selected period or its endpoint summary.

Rationale: the stacked chart shows the total trajectory and composition together;
only the bottom layer has a common baseline, so precise source changes are provided
by hover and the endpoint summary. Interpret this as source accounting, not causal
proof of economic policy effects or energy transition.


**Decision D019 — 2026-11-02:** the user accepts the source-composition chart and
requests progression. The first tab's three core chart designs are now accepted;
shared defaults, accessibility, and detailed state behaviour remain to be settled.
Open the second tab's accounting-comparison design next.

### Proposal P011: territorial/consumption paired comparison (accepted through D020)

Recommend a horizontal paired-dot (dumbbell) chart in **Footprints & Comparisons**:

- One row per eligible country in the fixed 20-country cohort; horizontal axis
  shows absolute fossil/industrial CO2 in Mt for the exact selected snapshot year.
  The chart compares published territorial and consumption totals, not GDP or
  land-use-inclusive CO2. Retain a common linear scale with zero visible.
- A circle marks territorial CO2, a diamond consumption CO2, joined by a neutral
  connector. Use two accessible colors plus distinct symbols, with explicit
  legend labels. Both marks use the same unit, year, and axis. A connector is
  an accounting difference, not a directional causal arrow.
- Order rows by signed accounting gap, consumption minus territorial CO2,
  descending, with ISO code as a stable tie-breaker. This places larger positive
  gaps above negative gaps. Reorder when the selected year changes and retain
  the focus highlight. Exact palette/row sizing remain to be specified.
- Hover includes country, selected year, both published totals, and the signed
  gap in Mt. A consumption mark to the right of its territorial mark means a
  larger consumption footprint; to the left means a larger territorial footprint.
  The shared absolute scale can compress small gaps for low-total countries;
  exact hover values and selected-country detail retain access to those values.
- Selecting a row/mark sets focus, with an equivalent searchable selector; the
  accounting history panel will follow that focus once its design is agreed.
  Highlight the focus row and report eligible count out of 20.
- Require both observations for the exact same year. If one is missing, exclude
  the pair from comparison and list it as unavailable; never substitute another
  year. For 2024 the current snapshot has no consumption observations, so show
  an explicit empty-comparison message while territorial ranking can remain usable.
- Explain the accounting bases in concise help: territorial emissions occur
  within a country's territory; consumption accounting adjusts for embodied
  emissions in imports/exports. Their difference alone does not establish
  industrial relocation or a causal explanation.

The paired comparison is accepted through D020. D021 delegates the remaining
version-1 UI defaults; these are specified in `docs/dashboard-design.md` before
implementation. No additional analytical dataset or new measure is introduced.

**Discuss and decide**

- Refine D009's accepted two-tab concept and approximately six linked panels
  against actual data coverage and the agreed measures.
- Earlier layout proposal: Growth & Emissions, Carbon Footprints, and Energy &
  Economic Structure. D007 requires revising the third area and checking that
  the first two have sufficient coverage. Revised candidates: Growth & Emissions,
  Carbon Footprints, and Emissions Composition & Intensity. Those earlier
  three-area layouts are superseded by D009's two-tab concept: Growth & Emissions
  and Footprints & Comparisons. Preserve Q1-Q4 while specifying the exact layout.
- Candidate charts: GDP-change versus emissions-change scatterplot, indexed time
  series, territorial/consumption paired-dot comparisons, footprint-gap trends,
  fuel/source composition charts, and intensity or per-capita comparisons.
  GDP-based charts depend on adequate GDP coverage within this same dataset.
- Define country selection, period and snapshot-year controls, linked selections,
  cross-tab state, reset, export, and data/methods access. Explain which filters
  affect which views; avoid an ambiguous single time control.
- Agree on encodings, units, axes, color mappings, legends, and accessible labels.
  Plan for missing data, no eligible countries, and excessive country selections.

**After decisions:** record reviewed wireframes and interaction behaviour under
`docs/`. Use prior-year screenshots as design references, not course requirements.

**Complete when:** each chart serves an agreed task, its interactions are explicit,
and the layout is legible at the agreed desktop window sizes.

**Decision record:** D015 accepts the first-tab ordering; D016 accepts P007
controls; D017 accepts P008 scatterplot encoding; D018 accepts P009 indexed
trends; D019 accepts P010 source composition; D020 accepts P011 accounting pairs.
D021 delegates the remaining UI decisions for version 1 and authorizes moving
into implementation. `docs/dashboard-design.md` records the selected defaults,
wireframes, interactions, and acceptance tasks before implementation.

## Step 7: First complete dashboard view

**Discuss and decide:** the first view, its exact scope, default selections, and
acceptance tasks. Current recommendation: Growth & Emissions.

**After decisions:** implement that view in `src/visualization/` using the prepared
data, including its filters, selection behaviour, units, and missing-data messages.

**Complete when:** agreed exploration tasks work, displayed values match the
prepared data, and the user has reviewed the interaction and visual design.
Record actual checks and any requested revisions before extending the interface.

**Decision record:** D021 authorizes recommended version-1 defaults and implementation.
Scope: Growth & Emissions with prepared data, agreed controls, accessible data
alternatives, and selected-country summaries. Implementation is ready for review.

**Implementation/checks — 2026-11-02:**

- Replaced the synthetic packaging demo with the real prepared-data dashboard.
  `src/visualization/figures.py` contains six chart builders;
  `app.py` contains state, controls, summaries, data/methods and export callbacks.
  Local CSS/JS is in `src/visualization/assets/`.
- First tab: scatter with descriptive categories/references and focus highlighting,
  selected-period baseline-100 GDP/CO2 trends for at most three countries, complete
  four-source stacks with Mt/share toggle, and exact endpoint source changes.
- Initial focus Germany; initial period 1990-2022. Clicking/searching focus and
  comparison limits, exact-year rebasing and zoom-independent calculations work.
  Reset uses a figure revision rather than reversing ordered country axes.
- Executed `.venv/bin/python -m unittest discover -s tests -v`: **21 passed**
  (12 preparation/measure tests and 9 dashboard/data/export/server tests). These
  check callback outputs against prepared observations, source sums, missing
  source-run separation, 2024 accounting unavailability with valid rankings,
  focus/comparison/reset state, CSV filtering/missingness, export bytes, indexed
  gaps, local HTTP assets and server port cleanup.
- Built `dist/GreenDecoupling.app` using `config/build_prototype.py`. The build now
  bundles pandas/other Python dependencies, prepared CSV/metadata and local assets.
  Mac source and bundled native smoke runs passed six rendered chart checks,
  focus/rebasing/comparison/share/metric/year changes, reset, CSV/PNG save bridge
  and no external resource loads. Evidence: `outputs/dashboard-source-smoke.json`,
  `outputs/dashboard-macos-smoke.json`, `outputs/dashboard-tests.log`, and
  `outputs/dashboard-build-macos.log`. The source smoke preceded the last
  accessibility refinements; the final bundled smoke covers the current version.
- Real native Mac Save dialogs were separately exercised for CSV and PNG and
  the output bytes checked. Browser layout at **800x600** stacked the charts
  without horizontal page overflow; **1440x900** displayed two columns without
  overflow after responsive resizing settled. The native **1380x900** window was
  visually inspected. Current preview screenshots/exports remain in `outputs/`.
- Input files were not changed; raw CSV/codebook hashes and read-only modes
  were reverified. Generated datasets, screenshots, exports and application
  builds stay outside Git, per the existing project policy.

**Review status:** awaiting user feedback on the working first version. Full
screen-reader/contrast/user evaluation, Windows runtime handling and final
release/distribution checks are still Step 9.

## Step 8: Remaining views and shared interactions

**Discuss and decide:** the next view's charts and behaviour before implementing
it. Repeat the discussion-record-implement-review cycle for each remaining view;
agreement on one view does not approve every proposed extension.

**After decisions:** implement the remaining views, coordinated country selection,
shared controls, methods/source information, and agreed exports. Optional maps,
animation, and additional indicators require a recorded scope decision.

**Complete when:** all agreed research tasks are supported, filter and selection
state behaves consistently, and visual conventions and missing-data handling
remain consistent across the application.

**Decision record:** D021 also authorizes the remaining version-1 UI choices,
so implement Footprints & Comparisons and shared interactions for review in the
same first version. No separate per-control approval is required.

**Implementation/checks — 2026-11-02:** Footprints & Comparisons now includes
matched territorial/consumption paired dots, focus-country accounting history,
and same-eligible-cohort total/per-capita ranking with top-10/all-20 display.
The snapshot control is independent from the growth analysis period; selections
persist across views. Missing consumption data in 2024 produces an explicit
empty paired comparison while territorial ranking remains available. Data/methods
access, filtered CSV, PNG buttons and native Save dialogs work across both views.
Native radio navigation and labelled dropdowns provide keyboard alternatives to
chart clicks; HTML data tables provide a hover alternative. Plotly cloud sharing
is disabled. The Step 7 checks above cover the linked first-version application.
Ready for review; do not mark the user review or final release checks complete.

## Step 9: Evaluation and final releases

**Discuss and decide:** final acceptance tasks, usability-review method, supported
test environments, release contents, and any course report or attribution needs.

**After decisions:** check calculations, linked interactions, readability,
accessibility, startup/shutdown, exports, and offline operation if agreed. Build
and test `GreenDecoupling.app` and `GreenDecoupling.exe` on the supported systems.
Include the agreed data, local assets, instructions, and attribution. Add report
and demonstration material only as required by the course or agreed scope.

**Complete when:** the packaged releases pass the recorded acceptance tasks on
the target systems without a development Python installation. Identify any
required platform runtime. Record unresolved limitations honestly and keep final
submission copies separate from drafts.

**Decision record:** D002 establishes the two application formats. Other release
choices pending. D005 requires one submitted Windows executable with no separately
delivered support files. Final release implementation remains pending; initial
Mac window testing is recorded below.

**Window testing and fix — 2026-11-02:** the user requested testing in the
application window. Tested the native macOS Apple Silicon preview, both manually
and with rendered checks. This is not evidence of Windows compatibility.

- Manual country search, start/end changes, China/Germany comparisons, a third
  additional-country attempt and source-share selection updated the linked
  charts correctly. The comparison limit retained the first two and explained it.
- Found a real WebKit layout defect: responsive graphs could lose their host
  height after filter updates, restoring a hidden view, or resizing. Charts then
  overlapped later panels. A regression check reproduced the failure. Graph
  hosts now receive explicit heights from the figure specifications, updated
  with each figure, while retaining responsive width/plot sizing.
- Rebuilt `dist/GreenDecoupling.app`. The final packaged smoke run passed nine
  geometry checks: initial layout, updated growth controls, unavailable 2024
  pairs/all-20 ranking, restored pairs, both views at 800x600 and 1380x900, and
  reset. Checks require three visible graphs, positive usable heights, drawings
  inside their hosts/sections, and no horizontal page overflow. Failure reports
  include geometry diagnostics; report/export paths are resolved before startup.
- Packaged callbacks passed: country focus, selected-year rebasing, three-country
  trends, source share, view switching, missing consumption in 2024, territorial
  and per-capita rankings, all-20 display, CSV/PNG save bridge and reset. No
  external resource requests were observed.
- In the rebuilt window, manually selected 2024, per-capita and all 20; clicked
  the United States ranking bar and observed the shared focus and history update.
  Saved CSV and PNG using real native dialogs; cancelled another save and saw
  “Save cancelled.” The CSV contains exactly 20 rows for 2024 with missing
  consumption retained. The accessible table also shows unavailable values.
  Opened the methods panel and verified reset restores Germany, 1990–2022,
  empty comparisons, amount units, 2022 snapshot and default ranking settings.
- Keyboard view switching passed with left/right arrows once the radio control
  was focused. Under this Mac's keyboard-navigation settings, Option-Tab is
  needed to include native radio controls in focus traversal.
- All 21 data/dashboard unit/integration tests passed after the chart fix. The
  raw CSV and codebook SHA-256 hashes remain unchanged. Exported PNG signatures,
  dimensions and chunk checksums were validated; the chart layout was visually
  inspected after the fix.

Local evidence (generated, ignored by Git):
`outputs/layout-before-fix.json`, `outputs/layout-source-smoke.json`,
`outputs/layout-macos-smoke-final.json`, `outputs/dashboard-tests.log`,
`outputs/window-test-footprints-2024.csv`, `outputs/window-test-ranking-2024.png`,
and `outputs/window-test-corrected-layout.png`.

**Remaining:** no Windows VM/runtime was found on this Mac (no Parallels, VMware,
UTM, VirtualBox, QEMU or Wine environment). The Windows `.exe`, WebView2 dependency
delivery, missing-runtime handling and clean Windows-machine testing remain
unverified. Independent Mac testing, signing/notarization, final attribution,
formal accessibility/user evaluation and final submission acceptance remain open.
Do not mark Step 9 or either final deliverable complete.

## Template for subsequent decision and completion entries

Add entries under the relevant step; do not replace historical decisions.

```text
Decision ID and date:
Step and status:
Agreed choice and scope:
Reason and alternatives considered:
User agreement reference:
Open questions or explicitly accepted assumptions:

Implementation completed:
Checks performed, environment, and observed results:
Files or evidence:
Review outcome and remaining work:
```

## Next discussion

The data source, stack, four questions, default period, fixed top-20 cohort, and
core measures are agreed in D007-D013. D014 approves P005 and read-only preservation
of the original dataset; Step 5 is implemented, validated, and accepted for
progression by the user’s request to move on.
**Current: review the working version-1 dashboard (Steps 7-8).** D020 accepts
the paired comparison and D021 delegates remaining UI decisions. Both tabs are
implemented, with checks recorded above and specifications in
`docs/dashboard-design.md`. UI defaults are accepted for this iteration; gather
feedback from actual use rather than reopening every design decision.
Step 2's Windows/runtime verification and Step 3's final source-attribution checks
remain outstanding; do not mark them complete without evidence.
