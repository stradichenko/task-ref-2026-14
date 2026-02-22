# Exploratory Analysis of Clinical Variables Over Time

> A proof-of-concept for the DM1 Dynamic Analysis System.

This directory contains an **R Markdown narrative analysis** that progressively
explores clinical variables from simple descriptive plots to time-to-event
modelling, using publicly available synthetic CDISC data.

## Read the analysis

| Format | Link |
|:---|:---|
| **GitHub Pages** (best experience) | [View online](https://stradichenko.github.io/task-ref-2026-14/exploratory_analysis.html) |
| **Source** | [exploratory_analysis.Rmd](exploratory_analysis.Rmd) |

> The GitHub Pages version includes a floating table of contents, code folding,
> and full-resolution figures. It is automatically re-deployed on every push to
> `master` via a [GitHub Actions workflow](../.github/workflows/pages.yml).

## Reproduce locally

```bash
# From the project root, enter the Nix shell
nix develop

# Render the R Markdown document
Rscript -e 'rmarkdown::render("small_exploratory_analysis/exploratory_analysis.Rmd")'
```

## What's inside

| File                         | Purpose                                          |
|:-----------|:-----------------|
| `exploratory_analysis.Rmd`   | Source document (narrative + code)                |
| `figures/`                   | Plot PNGs embedded in the annex PDF               |

## Analysis progression

1. **Demographic overview** -- baseline balance check (descriptive)
2. **SBP trajectories** -- vital signs over scheduled visits (longitudinal)
3. **ALT & CRP change from baseline** -- safety biomarkers over time (longitudinal)
4. **Kaplan-Meier curves** -- time to first adverse event (inferential)
