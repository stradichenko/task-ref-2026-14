# Task Ref. 2026-14

Clinical Data Management for Myotonic Dystrophy Type 1 (DM1) -
Three-Month Research Action Plan for IGTP.

This project comes with a **fully reproducible environment** - all the tools you
need (R, RStudio, Python, tidyverse, Pandoc, LaTeX, etc.) are defined in a
single Nix flake and will be installed automatically.

## Documents

### Three-Month Action Plan (PDF Report)

The main deliverable is a 5-page action plan covering data quality, dynamic
analysis, mobile app design, regulatory compliance, and work organisation.

| Artefact | Location |
|:---|:---|
| **Report source** | [report.md](report.md) |
| **Annex source** | [annex.md](annex.md) |
| **Rendered PDFs** | `report.pdf`, `annex.pdf` (generated locally) |

#### How to render

Inside the Nix environment:

```sh
nix develop
pandoc report.md -o report.pdf --pdf-engine=xelatex
pandoc annex.md -o annex.pdf --pdf-engine=xelatex
```

The report and annex reference images from `architecture/`, `data_flow/`,
`gantt/`, `raci/`, `rbac/`, `risk_matrix/`, and `small_exploratory_analysis/` -
run the command from the project root.

---

### Exploratory Analysis

An interactive R Markdown report progressing from demographic summaries to
Kaplan-Meier survival analysis, using synthetic CDISC data.

| View | Link |
|:---|:---|
| **GitHub Pages** (recommended) | <https://stradichenko.github.io/task-ref-2026-14/exploratory_analysis.html> |
| **Rendered Markdown** (GitHub) | [small_exploratory_analysis/exploratory_analysis.md](small_exploratory_analysis/exploratory_analysis.md) |
| **Source Rmd** | [small_exploratory_analysis/exploratory_analysis.Rmd](small_exploratory_analysis/exploratory_analysis.Rmd) |

```sh
nix develop
Rscript -e 'rmarkdown::render("small_exploratory_analysis/exploratory_analysis.Rmd", output_dir = "docs")'
```

---

### Architecture Diagram

Available as PNG (for the PDF report/annex) and `.drawio` (editable in
[app.diagrams.net](https://app.diagrams.net) or the VS Code Draw.io extension).
Both are generated from the same JSON config:

```sh
python3 architecture/architecture_map.py       # -> architecture_map.png
python3 architecture/architecture_drawio.py    # -> architecture_map.drawio
```

---

## Reproducible environment

### What's included

| Tool | Details |
|:--|:------|
| **R** | 4.4.1 with tidyverse, remotes, devtools, random.cdisc.data |
| **RStudio** | Ready to launch (Linux only - see macOS note) |
| **Python** | 3.11 with pip and virtualenv |
| **Pandoc + LaTeX** | For rendering Markdown to PDF |
| **Bash** | Default shell |

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

#### 3. Clone and enter

```sh
git clone https://github.com/stradichenko/task-ref-2026-14.git
cd task-ref-2026-14
nix develop
```
