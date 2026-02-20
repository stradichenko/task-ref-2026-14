# Task Ref. 2026-14

This project comes with a **fully reproducible environment** — all the tools you
need (R, RStudio, Python, tidyverse, Pandoc, LaTeX, etc.) are defined in a
single file and will be installed automatically. You don't need to install them
yourself.

---

## What's included

Once the environment is running you will have:

| Tool | Version / Details |
|------|-------------------|
| **R** | With tidyverse, remotes, devtools pre-loaded |
| **RStudio** | Ready to launch (Linux only — see macOS note below) |
| **random.cdisc.data** | Auto-installed on first run |
| **Python** | 3.11 with pip and virtualenv |
| **Bash** | Available as default shell |
| **Pandoc + LaTeX** | For rendering the report to PDF |

---

## Documents

### Three-Month Action Plan (PDF Report)

The main deliverable is a comprehensive action plan for the Clinical Data
Manager position, rendered from Markdown to PDF via Pandoc and LaTeX.

| Artefact | Location |
|:---------|:---------|
| **Source** | [report.md](report.md) |
| **Rendered PDF** | `report.pdf` (generated locally — see instructions below) |

#### How to render the report

Inside the Nix environment:

```sh
nix develop
pandoc report.md \
  -o report.pdf \
  --pdf-engine=xelatex \
  --toc \
  --number-sections \
  -V geometry:margin=2.5cm \
  -V fontsize=11pt \
  -V documentclass=article
```

Alternatively, if you have Pandoc and a LaTeX distribution installed:

```sh
pandoc report.md -o report.pdf --pdf-engine=xelatex
```

The report references images from `rbac/`, `raci/`, `gantt/`, `risk_matrix/`,
and `data_flow/` — make sure to run the command from the project root.

---

### Exploratory Analysis of Clinical Variables Over Time

A narrative R Markdown walkthrough that progresses from demographic summaries to
Kaplan-Meier survival analysis, using synthetic CDISC data in the context of a
DM1 multi-centre study.

| View | Link |
|:-----|:-----|
| **GitHub Pages** (recommended) | <https://stradichenko.github.io/task-ref-2026-14/exploratory_analysis.html> |
| **Rendered Markdown** (GitHub) | [small_exploratory_analysis/exploratory_analysis.md](small_exploratory_analysis/exploratory_analysis.md) |
| **Source Rmd** | [small_exploratory_analysis/exploratory_analysis.Rmd](small_exploratory_analysis/exploratory_analysis.Rmd) |

> **Local preview:** `nix develop`, then
> `Rscript -e 'rmarkdown::render("small_exploratory_analysis/exploratory_analysis.Rmd")'`
> and open the resulting HTML in your browser.

---

## Setup guide (step by step)

### 1 · Install the Nix package manager

Nix is a small program that manages all the software for this project. It
doesn't change anything else on your computer. Pick your operating system below.

<details>
<summary><strong>Linux (Ubuntu, Fedora, Debian, etc.)</strong></summary>

Open a **Terminal** and paste:

```sh
sh <(curl -L https://nixos.org/nix/install) --daemon
```

Follow the on-screen prompts (you may need to type your password). When it
finishes, **close and re-open your terminal**.
</details>

<details>
<summary><strong>macOS</strong></summary>

Open **Terminal** (search for "Terminal" in Spotlight) and paste:

```sh
sh <(curl -L https://nixos.org/nix/install)
```

Follow the on-screen prompts. When it finishes, **close and re-open your
terminal**.

> **Note:** RStudio cannot be built through Nix on macOS. You can install it
> separately with `brew install --cask rstudio` (if you use Homebrew) or
> download it free from <https://posit.co/download/rstudio-desktop/>.
> Everything else (R, Python, packages) works normally.
</details>

<details>
<summary><strong>Windows</strong></summary>

Nix doesn't run directly on Windows. The easiest path is **WSL2** (Windows
Subsystem for Linux), which gives you a real Linux inside Windows.

1. Open **PowerShell as Administrator** and run:
   ```powershell
   wsl --install
   ```
2. Restart your computer when prompted.
3. Open the new **Ubuntu** app from the Start Menu.
4. Inside Ubuntu, install Nix:
   ```sh
   sh <(curl -L https://nixos.org/nix/install) --daemon
   ```
5. Close and re-open the Ubuntu terminal.

From here on, follow the same steps as Linux (below) inside that Ubuntu window.
</details>

### 2 · Enable Flakes (one-time setup)

Flakes are an opt-in Nix feature we rely on. Run this once:

```sh
mkdir -p ~/.config/nix
echo "experimental-features = nix-command flakes" >> ~/.config/nix/nix.conf
```

### 3 · Get the project

If you haven't already, clone (download) this repository:

```sh
git clone <URL-of-this-repo>
cd task-ref-2026-14
```

*(Replace `<URL-of-this-repo>` with the actual link you were given.)*

### 4 · Enter the environment

```sh
nix develop
```

**The first time this will take a while** (it downloads and builds R, Python,
RStudio, and all packages). Subsequent runs are nearly instant because
everything is cached.

When it finishes you will see:

```
Environment ready.
  R          : R version …
  Python     : Python 3.11.…
  Bash       : GNU bash, version …
  RStudio    : run 'rstudio' to launch
  R packages : tidyverse, remotes, devtools, random.cdisc.data
```

You're all set!

### 5 · Daily use

| I want to… | Command |
|---|---|
| Enter the environment | `nix develop` (from the project folder) |
| Open RStudio | `rstudio` (once inside the environment) |
| Run an R script | `Rscript my_script.R` |
| Run a Python script | `python3 my_script.py` |
| Leave the environment | `exit` or press `Ctrl+D` |

---

## Troubleshooting

| Problem | Fix |
|---|---|
| `nix: command not found` | Close and re-open your terminal after installing Nix. |
| `error: experimental Nix feature 'flakes' is disabled` | Run the "Enable Flakes" step above. |
| Build fails on macOS mentioning RStudio | This is expected — RStudio is Linux-only via Nix. Install it separately (see macOS note above). The rest of the environment will work fine. |
| Very slow first run | Normal — Nix is downloading everything. Next time it will be instant. |
| `permission denied` during Nix install | Make sure you run the installer with `--daemon` and enter your password when asked. |
