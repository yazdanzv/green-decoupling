# Green Decoupling

Information Visualization, Winter Semester 2026/27. Group 16: Yazdan Zandiyevakili
and Ben Barth.

This is the starting structure for the team's course project. The original team
proposal is preserved in [Project Plan.pdf](docs/proposal/Project%20Plan.pdf).
Implementation, data downloads, and analysis have not started in this scaffold.
The course is project-only, so no assignment directories are needed.

## Project scope

The proposal asks how nations have grown their economies while lowering domestic
CO₂ emissions since 1990, exploring renewable energy transitions and the shifting
of industry and carbon footprints abroad. Its three areas of visual exploration
are:

- Changes in carbon intensity alongside renewable energy adoption and changes in
  manufacturing and service sectors.
- Differences between territorial and consumption-based emissions.
- Relationships among trade, energy mixes, population density, and purchasing
  power.

These are research questions, not established findings. The planned interactive
dashboard will support exploration of these relationships; causal explanations
will require evidence beyond correlations.

## Folder structure

```text
green-decoupling/
├── README.md
├── .gitignore
├── docs/
│   └── proposal/          Original team proposal; add course briefs separately in docs/
├── config/               Dataset selections and application configuration
├── data/
│   ├── raw/
│   │   ├── owid/         Unmodified OWID downloads and source metadata
│   │   └── wdi/          Unmodified World Bank exports and source metadata
│   └── processed/        Reproducible cleaned and merged datasets
├── src/
│   ├── data/             Loading, cleaning, joining, and validation code
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
into the university workspace as a Git submodule. No programming framework has
been selected yet. Generated datasets and outputs are ignored by Git; final
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
git submodule update --init --recursive -- 2026-WS/information-visualization/projects/green-decoupling
```

Commit and push project changes from inside this project directory. After pushing,
commit the updated submodule reference in the university repository to record the
project version used there. Setup and run instructions will be added once the
implementation stack is selected.

## Dataset selection

The team's proposal identifies the following sources. Their current schemas,
coverage, and licensing still need to be checked before implementation.

| Proposed source | Intended role | Local location |
| --- | --- | --- |
| Our World in Data CO₂ and Greenhouse Gas Emissions Dataset (`owid-co2-data.csv`) | Emissions and available energy-related measures | `data/raw/owid/` |
| World Bank World Development Indicators (WDI) | Economic, industrial, trade, and demographic indicators | `data/raw/wdi/` |

The exact indicator codes, units, energy measures, and usable country-year range
remain to be selected. Renewable energy coverage in particular must be verified
against the chosen source variables.

For each download, record its source URL, retrieval date, version or release if
available, license, and variable definitions alongside the raw file. Preserve raw
downloads unchanged. Keep the original proposal unchanged as well; write revisions
as separate files.

## Suggested first steps

1. Add the official course project brief and any rubric or AI-use policy under
   `docs/` when available; those requirements take precedence over this scaffold.
2. Verify source metadata and select indicators for emissions, GDP, renewable
   energy, sector composition, trade, population density, and purchasing power.
   Save the selections and units under `config/`.
3. Define a country-year merge, initially considering ISO country codes and year.
   Document aggregate exclusions, code mappings, missing values, duplicate keys,
   and temporal coverage. Check that GDP and emissions definitions are compatible
   before deriving carbon intensity.
4. Implement data preparation in `src/data/` and checks in `tests/`, writing
   reproducible results to `data/processed/`.
5. Sketch dashboard views around the three research questions, then implement
   them in `src/visualization/`. Use accessible colors, clear units, and visible
   handling of missing data. Keep design notes in `docs/`.
6. Record setup and run commands here once the team chooses a stack. Develop the
   report in `reports/drafts/` and keep final submission copies in `reports/final/`.
