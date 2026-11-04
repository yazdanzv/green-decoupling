# Green Decoupling

Information Visualization, Winter Semester 2026/27. Group 16: Yazdan Zandiyevakili
and Ben Barth.

This repository contains the team's course project. The original team
proposal is preserved in [Project Plan.pdf](docs/proposal/Project%20Plan.pdf).
The first interactive dashboard and reproducible data preparation are implemented.
Both tabs contain the six agreed charts, linked country selection, year/metric
controls, accessible data tables, and native CSV/PNG saves. A local macOS preview
is built and tested; final release work remains.
The course is project-only, so no assignment directories are needed.

Follow [plan.md](plan.md) for the staged workflow and decision log. Discuss each
stage and record its agreed decisions there before implementing that stage.

## Project scope

The current agreed scope uses **only the Our World in Data CO₂ and Greenhouse
Gas Emissions Dataset (`owid-co2-data.csv`)**. The original proposal combined OWID
and World Bank WDI to investigate growth, energy transitions, and carbon
outsourcing. That proposal is preserved unchanged; decision D007 in `plan.md`
supersedes its two-source integration strategy.

The four agreed core questions (D009 in `plan.md`) are:

- Which countries have grown their economies while reducing territorial CO₂?
- How do footprints and trends change under consumption-based accounting?
- How do country rankings differ between total and per-capita emissions?
- Which fuel and industrial sources account for observed emissions changes,
  where the reported components support that accounting?

The accepted design direction is approximately six linked chart panels in two
tabs: Growth & Emissions, and Footprints & Comparisons. The shared default period
is **1990-2022 inclusive** (D010). Emissions-only views may offer newer available
years with visible coverage labels. The core measure definitions are approved
in D013; the version-1 chart specifications and interactions are recorded in
[docs/dashboard-design.md](docs/dashboard-design.md), accepted under D015-D021. Do not import another
analytical dataset to fill missing variables. Questions about renewable adoption,
manufacturing, and general trade profiles must be revised if their required
variables are absent. These remain research questions, not findings; correlations
and emissions-accounting differences alone do not establish causal explanations.

The agreed cohort is the top **20** eligible countries/territories by total
territorial CO₂ in **2022**, fixed across years and metric changes (D012).
The selected names, ISO codes, ranking values, and snapshot hash are recorded in
`config/analysis_selection.json`. Eligibility is assessed separately for each question (D011).
The per-question missing-data rules are documented and accepted in P004/D013.
Comparisons must use matching years and expose unavailable values.

The agreed measures are endpoint GDP/emissions changes and baseline-100 trends,
territorial/consumption totals and their difference, total/per-capita rankings,
and four source groups: coal, oil, gas, and a derived fossil/industrial remainder
(`co2 - coal_co2 - oil_co2 - gas_co2`). The remainder is not the dataset's published
`other_industry_co2` variable. See `plan.md` for units and calculation conditions.

## Folder structure

```text
green-decoupling/
├── README.md
├── plan.md                Stages, agreed decisions, and verification records
├── requirements.txt       Pinned direct application dependencies
├── .gitignore
├── docs/
│   └── proposal/          Original team proposal; add course briefs separately in docs/
├── config/               Dataset selections and application configuration
├── data/
│   ├── raw/
│   │   └── owid/         Read-only original OWID snapshot and source metadata
│   └── processed/        Reproducible prepared data and derived measures
├── src/
│   ├── data/             Loading, cleaning, transformation, and validation code
│   └── visualization/    Interactive views, controls, and application code
├── tests/                Data checks and application tests
├── outputs/              Generated figures, screenshots, and exports
└── reports/
    ├── drafts/           Working report and presentation material
    └── final/            Final submission copies
```

Empty directories contain `.gitkeep` files so the scaffold can be tracked in Git.
The project has its own public repository at
[yazdanzv/green-decoupling](https://github.com/yazdanzv/green-decoupling) and is linked
into the university workspace as a Git submodule. The agreed stack is Python,
pandas, Plotly, Dash, pywebview, and PyInstaller. Generated datasets and outputs are ignored by Git; final
submission files belong in `reports/final/`.

## Get the project

Clone the standalone repository:

```sh
git clone https://github.com/yazdanzv/green-decoupling.git
cd green-decoupling
```

When working from the university workspace, initialize the linked project from
the workspace root:

```sh
git submodule update --init --recursive -- 2026-WS/visual-data-science/projects/green-decoupling
```

Commit and push project changes from inside this project directory. After pushing,
commit the updated submodule reference in the university repository to record the
project version used there. Development and prototype commands appear below.

## Dataset selection

The selected source is the OWID CO₂ dataset. The preserved snapshot schema,
core codebook units, cohort, and coverage have been checked. Underlying-source
attribution and redistribution terms must still be completed before release;
see `config/data_sources.json`. Do not add a second analytical dataset.

| Selected source | Intended role | Local location |
| --- | --- | --- |
| Our World in Data CO₂ and Greenhouse Gas Emissions Dataset (`owid-co2-data.csv`) | Emissions and available economic, population, and energy-related measures | `data/raw/owid/` |

The prepared metadata records published column definitions, units, source names,
formulas, and the fixed cohort. Availability is assessed separately for each
question and year.

The preliminary snapshot inspection and four agreed core questions are
recorded under Step 3 in [plan.md](plan.md). The 1990-2022 shared default is agreed;
the top-20 cohort is selected and verified. Core measures and per-question
missing-data rules are accepted in D013; the full source audit remains open.
The snapshot's GDP ends in 2022, consumption-based CO₂ in 2023, and territorial
CO₂ in 2024, so linked views must make their different coverage explicit.

For each download, record its source URL, retrieval date, version or release if
available, license, and variable definitions alongside the raw file. Preserve raw
downloads unchanged. Keep the original proposal unchanged as well; write revisions
as separate files.

## Current stage

Steps 7-8: the first complete dashboard is ready for user review. The six chart
specifications and remaining version-1 UI defaults are documented and accepted
under the user's delegated approval (D021). Test evidence is recorded in
[plan.md](plan.md). Windows build/runtime delivery, final source attribution,
and final release acceptance remain open. The Windows submission must be one
`.exe`, including or installing its dependencies; the Mac deliverable is an
`.app`. Add the official course brief and policies under `docs/` when available.

## Rebuild the prepared data

With the pinned original snapshot already present and the Python environment set
up as below, run from the project root:

```sh
.venv/bin/python -m src.data.prepare
```

This reads `config/analysis_selection.json` and the preserved raw CSV/codebook,
verifies their hashes and read-only permissions, and writes:

- `data/processed/country_year.csv`: fixed 20-country grid, 1990-2024, published
  inputs, accounting gap, derived source residual/shares, and availability flags.
- `data/processed/metadata.json`: units, definitions, hashes, cohort, source links,
  and outstanding release-attribution requirements.
- `outputs/data-validation.json`: executed validation and missingness by year,
  measure, and country.

The default remains 1990-2022. GDP is missing after 2022; consumption emissions
are missing after 2023. Empty CSV fields remain missing. The pipeline never fills
or substitutes analytical observations. `src/data/measures.py` calculates changes
and indexed series for the selected endpoints, and uses the same eligible cohort
for both total/per-capita rankings. Ties share the minimum rank; categories use
unrounded changes with strict comparisons and no significance threshold.

The original files in `data/raw/owid/` have mode `0444`; that folder and
`data/raw/` have mode `0555` on the development Mac. The pipeline only reads them
and fails if permissions, hashes, units, or consequential validation checks fail.
The owner can deliberately change permissions; hashes provide a separate
integrity check. **Git does not preserve these read-only permission bits.**

Raw downloads and generated tables are deliberately excluded from Git. On another
machine, obtain the exact snapshot identified in `data/raw/owid/source.json`
using the recorded URLs, verify its hashes against that file and the cohort
configuration, then apply read-only permissions. A newer live download is not
an automatic replacement for the approved snapshot. On macOS/Linux, protect an
already verified snapshot with:

```sh
python3 - <<'PY'
from pathlib import Path
raw = Path('data/raw/owid')
for path in raw.iterdir():
    path.chmod(0o444)
raw.chmod(0o555)
raw.parent.chmod(0o555)
PY
```

The data preparation and permission checks have been executed on macOS only.

## Run and build the dashboard

Use Python 3.12. On macOS, after obtaining/protecting the pinned raw snapshot:

```sh
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m src.data.prepare
.venv/bin/python src/visualization/desktop.py
```

The native desktop window opens a loopback-only local server and shuts it down
when the window closes. It uses the prepared CSV and metadata; it never writes
to those analytical inputs. To use a normal browser during development:

```sh
.venv/bin/python -m src.visualization.app --port 8050
```

Then open `http://127.0.0.1:8050`. All scripts, styles, fonts and chart assets are
local. The Plotly cloud-sharing button is disabled. PNG buttons and filtered CSV
exports use a native Save dialog in the desktop app, or a browser download when
running in a browser.

To reproduce the exact tested Mac dependency environment instead, install from
`config/requirements-macos-arm64.lock.txt`. This is macOS-specific, not a Windows
lock file. Run the calculation, callback, export and server-shutdown tests:

```sh
.venv/bin/python -m unittest discover -s tests -v
```

Build and check the macOS application (the build script retains its original
prototype filename for command compatibility):

```sh
.venv/bin/python config/build_prototype.py
dist/GreenDecoupling.app/Contents/MacOS/GreenDecoupling --smoke-report outputs/dashboard-macos-smoke.json
```

The build bundles the prepared dataset, metadata, local CSS/JS and Python
libraries. The smoke run verifies six rendered charts and linked interactions,
checks chart containment and horizontal overflow after filter/view changes and
at 800x600 and 1380x900 in both views,
checks for external resource loads, tests native export bytes in
`outputs/smoke-exports/`, writes JSON, then closes. It uses an automatic test
output folder; real native Save dialogs were separately checked on the Mac.
For manual review, open `dist/GreenDecoupling.app` in Finder. This Apple Silicon
build is a **local preview**; independent-machine, Intel Mac, signing/notarization
and final distribution checks have not been performed.

The Windows build path is prepared but **not yet executed or tested**. After
preparing the same data on a development machine, PowerShell commands are:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe config/build_prototype.py
.\dist\GreenDecoupling.exe --smoke-report outputs\dashboard-windows-smoke.json
```

The Windows path uses PyInstaller `--onefile` but currently expects WebView2 to
be present. Bundled/integrated runtime delivery and the missing-runtime case
remain unimplemented and untested. The single-file submission requirement is
therefore **not yet verified**. Network-disconnected startup has not been tested;
the executed Mac checks observed no external resource requests during normal use.
