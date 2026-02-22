<h1 align="center">Task Ref. 2026-14</h1>

## Clinical Data Management for Myotonic Dystrophy Type 1 (DM1) - Three-Month Research Action Plan for IGTP. - Gary J. Espitia S.

All the documentation is presented within a **fully reproducible environment** - all the tools you need (R, RStudio, Python, tidyverse, Pandoc, LaTeX, etc.) are defined in a single Nix flake.

This report presents a three-month action plan to design, build, and validate a minimum viable platform for prospective data collection in Myotonic Dystrophy Type 1 (DM1). The platform is conceived as mobile-first, respects a clear role-based governance model, and is aligned with the General Data Protection Regulation (GDPR) and the European Health Data Space (EHDS). For clinical interoperability it adopts Fast Healthcare Interoperability Resources (FHIR), while the research analytics layer relies on the Observational Medical Outcomes Partnership Common Data Model (OMOP CDM). Every component in the stack is Free and Open-Source Software (FOSS) and follows a local-first philosophy, so that no proprietary dependency constrains future evolution.


### Setup (step by step)

#### 1. Install the Nix package manager

<details>
<summary><strong>Linux (Ubuntu, Fedora, Debian, etc.)</strong></summary>

```sh
sh <(curl -L https://nixos.org/nix/install) --daemon
```

Close and re-open your terminal when done.
</details>

<details>
<summary><strong>macOS</strong></summary>

```sh
sh <(curl -L https://nixos.org/nix/install)
```

> **Note:** RStudio is Linux-only via Nix. Install it separately with
> `brew install --cask rstudio` or from <https://posit.co/download/rstudio-desktop/>.
</details>

<details>
<summary><strong>Windows (via WSL2)</strong></summary>

1. Open **PowerShell as Administrator**: `wsl --install`
2. Restart, then open the **Ubuntu** app.
3. Inside Ubuntu: `sh <(curl -L https://nixos.org/nix/install) --daemon`
</details>

#### 2. Enable Flakes (one-time)

```sh
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

#### 3. Clone and enter the nix environment

```sh
git clone https://github.com/stradichenko/task-ref-2026-14.git
cd task-ref-2026-14
nix develop
```

## Documents

#### How to render
Inside the Nix environment:

```sh
pandoc report.md -o report.pdf --pdf-engine=xelatex
pandoc annex.md -o annex.pdf --pdf-engine=xelatex
```


| Artefact | Location |
|:---|:---|
| **Report source** | [report.md](report.md) |
| **Annex source** | [annex.md](annex.md) |
| **Rendered PDFs** | [`report.pdf`](report.pdf), [`annex.pdf`](annex.pdf) (generated locally) |



The report and annex reference images from `architecture/`, `data_flow/`,
`gantt/`, `raci/`, `rbac/`, `risk_matrix/`, and `small_exploratory_analysis/`.

---

### Exploratory Analysis

Interactive R Markdown report progressing from demographic summaries to Kaplan-Meier survival analysis, using synthetic CDISC data.

| View | Link |
|:---|:---|
| **GitHub Pages** (recommended) | <https://stradichenko.github.io/task-ref-2026-14/exploratory_analysis.html> |
| **Source Rmd** | [small_exploratory_analysis/exploratory_analysis.Rmd](small_exploratory_analysis/exploratory_analysis.Rmd) |

```sh
Rscript -e 'rmarkdown::render("small_exploratory_analysis/exploratory_analysis.Rmd", output_dir = "docs")'
```

---

### Architecture Diagram

Available as [PNG](architecture/architecture_map.png) (for the PDF report/annex) and `.drawio` (editable in
[app.diagrams.net](https://app.diagrams.net) or the VS Code Draw.io extension).

![Architecture Diagram](architecture/architecture_map.png)

**Platform Architecture Map.** Zoned view of all system components-Client, API & Identity, Operational Data, Processing & ETL, Research & Analytics, and External & Interoperability-with Identity & Access Management and Observability as cross-cutting concerns. Data-flow sequence numbers indicate the order of interactions. 