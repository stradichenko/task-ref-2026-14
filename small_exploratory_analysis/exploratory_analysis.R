#!/usr/bin/env Rscript
# ══════════════════════════════════════════════════════════════════════════════
# Exploratory Statistical Analysis of Clinical Variables Over Time
# ══════════════════════════════════════════════════════════════════════════════
#
# Context
# -------
# We are building a dynamic analysis system for a database containing clinical,
# genomic, and proteomic data from 200 patients with Myotonic Dystrophy Type 1
# (DM1), collected across 25 hospitals and entered by 13 different personnel.
#
# This script demonstrates the kind of exploratory work the analytical layer
# would support — progressing from simple descriptive summaries to longitudinal
# modelling and time-to-event analysis.  We use the publicly available
# `random.cdisc.data` package (pharmaverse) which provides synthetic CDISC ADaM
# datasets that mirror the structure of a real multi-centre clinical trial.
#
# Datasets used
# -------------
#   cadsl    — Subject-Level Analysis (ADSL): demographics, treatment arms
#   cadvs    — Vital Signs Analysis  (ADVS): BP, pulse, weight … per visit
#   cadlb    — Laboratory Analysis   (ADLB): ALT, CRP, IGA … per visit
#   cadaette — Time-to-AE Analysis   (ADAETTE): survival / event data
#
# Outputs  : 4 PDF plots saved to ./plots/
# Requires : tidyverse, survival, random.cdisc.data  (all in the Nix shell)
# ══════════════════════════════════════════════════════════════════════════════

# ── 0. Setup ─────────────────────────────────────────────────────────────────

# Install helper packages if not already present (gridExtra, broom, scales)
for (pkg in c("gridExtra", "broom", "scales")) {
  if (!requireNamespace(pkg, quietly = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org", quiet = TRUE)
  }
}

suppressPackageStartupMessages({
  library(tidyverse)
  library(survival)
  library(random.cdisc.data)
  library(gridExtra)
  library(broom)
  library(scales)
})

# Reproducibility
set.seed(42)

# Output directory — resolve script location robustly
script_dir <- tryCatch(
  dirname(normalizePath(sys.frame(1)$ofile)),
  error = function(e) {
    # Fallback: use commandArgs to find script path (works with Rscript)
    args <- commandArgs(trailingOnly = FALSE)
    file_arg <- grep("^--file=", args, value = TRUE)
    if (length(file_arg) > 0) {
      dirname(normalizePath(sub("^--file=", "", file_arg)))
    } else {
      normalizePath("small_exploratory_analysis")
    }
  }
)
plot_dir <- file.path(script_dir, "plots")
dir.create(plot_dir, showWarnings = FALSE, recursive = TRUE)

cat("══════════════════════════════════════════════════════════════\n")
cat("  Exploratory Analysis — Clinical Variables Over Time\n")
cat("══════════════════════════════════════════════════════════════\n\n")

# ── 1. Load cached CDISC datasets ───────────────────────────────────────────

data("cadsl");    adsl    <- cadsl
data("cadvs");    advs    <- cadvs
data("cadlb");    adlb    <- cadlb
data("cadaette"); adaette <- cadaette

cat(sprintf("  ADSL    : %d subjects  × %d variables\n", nrow(adsl), ncol(adsl)))
cat(sprintf("  ADVS    : %d records   × %d variables\n", nrow(advs), ncol(advs)))
cat(sprintf("  ADLB    : %d records   × %d variables\n", nrow(adlb), ncol(adlb)))
cat(sprintf("  ADAETTE : %d records   × %d variables\n", nrow(adaette), ncol(adaette)))
cat("\n")

# ── Subsample to 200 patients (mirroring DM1 study size) ────────────────────
# The cached data has 400 subjects; we subsample to match the 200-patient
# scenario described in the project context.

selected_ids <- adsl %>%
  distinct(USUBJID) %>%
  slice_sample(n = 200) %>%
  pull(USUBJID)

adsl    <- adsl    %>% filter(USUBJID %in% selected_ids)
advs    <- advs    %>% filter(USUBJID %in% selected_ids)
adlb    <- adlb    %>% filter(USUBJID %in% selected_ids)
adaette <- adaette %>% filter(USUBJID %in% selected_ids)

cat(sprintf("  Subsampled to %d patients (DM1 study size).\n\n", n_distinct(adsl$USUBJID)))


# ══════════════════════════════════════════════════════════════════════════════
# PLOT 1 — Demographic Overview by Treatment Arm
# ══════════════════════════════════════════════════════════════════════════════
#
# Rationale
# ---------
# The first step in any clinical analysis is understanding *who* is in the
# study.  In a multi-centre DM1 trial we need to verify that treatment arms
# are balanced with respect to sex and age — imbalances could confound
# downstream analyses of vital signs, biomarkers, or time-to-event endpoints.
#
# What this shows
# ---------------
# Left panel  : patient counts by treatment arm, coloured by sex.
# Right panel : age density curves overlaid by arm to check distributional
#               balance across groups.
# ──────────────────────────────────────────────────────────────────────────────

cat("▸ Plot 1 : Demographic overview …\n")

# Prepare summary table
demo_summary <- adsl %>%
  count(ARM, SEX, name = "n_patients") %>%
  mutate(ARM = fct_reorder(ARM, n_patients, .fun = sum))

p1_left <- ggplot(demo_summary, aes(x = ARM, y = n_patients, fill = SEX)) +
  geom_col(position = "dodge", width = 0.7, colour = "grey30", linewidth = 0.3) +
  scale_fill_manual(values = c("F" = "#E07B91", "M" = "#6BAED6"),
                    labels = c("F" = "Female", "M" = "Male")) +
  labs(x = NULL, y = "Number of patients", fill = "Sex") +
  theme_minimal(base_size = 11) +
  theme(axis.text.x = element_text(angle = 25, hjust = 1),
        legend.position = "top")

p1_right <- ggplot(adsl, aes(x = AGE, fill = ARM, colour = ARM)) +
  geom_density(alpha = 0.25, linewidth = 0.6) +
  labs(x = "Age (years)", y = "Density", fill = "Treatment arm",
       colour = "Treatment arm") +
  theme_minimal(base_size = 11) +
  theme(legend.position = "top")

# Combine side by side
p1 <- gridExtra::grid.arrange(
  p1_left, p1_right, ncol = 2,
  top = grid::textGrob(
    "Plot 1 - Demographic Overview by Treatment Arm",
    gp = grid::gpar(fontsize = 13, fontface = "bold")
  )
)

ggsave(file.path(plot_dir, "plot_1_demographics.pdf"), p1,
       width = 11, height = 5, dpi = 300)
cat("  ✓ Saved to plots/plot_1_demographics.pdf\n\n")


# ══════════════════════════════════════════════════════════════════════════════
# PLOT 2 — Vital Signs Trajectories Over Time (Systolic Blood Pressure)
# ══════════════════════════════════════════════════════════════════════════════
#
# Rationale
# ---------
# Myotonic Dystrophy Type 1 is a multi-systemic disorder with well-documented
# cardiovascular involvement — cardiac conduction defects and, in some cohorts,
# altered blood pressure regulation.  Monitoring systolic blood pressure (SBP)
# over scheduled visits is therefore clinically meaningful.
#
# What this shows
# ---------------
# Individual patient trajectories (thin grey lines) overlaid with the group
# mean ± 95 % CI ribbon, stratified by treatment arm.  This "spaghetti + mean
# trajectory" design lets us simultaneously gauge within-patient variability
# and between-arm trends.
# ──────────────────────────────────────────────────────────────────────────────

cat("▸ Plot 2 : Vital signs trajectories (SBP) …\n")

sbp <- advs %>%
  filter(PARAMCD == "SYSBP",
         AVISIT != "",           # drop unscheduled
         !is.na(AVAL),
         !is.na(AVISITN)) %>%
  select(USUBJID, ARM, AVISIT, AVISITN, AVAL)

# Mean + CI per arm per visit
sbp_summary <- sbp %>%
  group_by(ARM, AVISIT, AVISITN) %>%
  summarise(
    mean_val = mean(AVAL, na.rm = TRUE),
    se       = sd(AVAL, na.rm = TRUE) / sqrt(n()),
    .groups  = "drop"
  ) %>%
  mutate(lo = mean_val - 1.96 * se,
         hi = mean_val + 1.96 * se)

p2 <- ggplot() +
  # Individual trajectories (background)
  geom_line(data = sbp,
            aes(x = AVISITN, y = AVAL, group = USUBJID),
            alpha = 0.08, linewidth = 0.3, colour = "grey50") +
  # Mean ribbon
  geom_ribbon(data = sbp_summary,
              aes(x = AVISITN, ymin = lo, ymax = hi, fill = ARM),
              alpha = 0.25) +
  # Mean line
  geom_line(data = sbp_summary,
            aes(x = AVISITN, y = mean_val, colour = ARM),
            linewidth = 0.9) +
  geom_point(data = sbp_summary,
             aes(x = AVISITN, y = mean_val, colour = ARM),
             size = 1.8) +
  facet_wrap(~ ARM, nrow = 1) +
  scale_x_continuous(breaks = sort(unique(sbp_summary$AVISITN))) +
  labs(
    title    = "Plot 2 - Systolic Blood Pressure Trajectories Over Scheduled Visits",
    subtitle = "Individual traces (grey) with group mean ± 95 % CI, by treatment arm",
    x = "Analysis visit number",
    y = "Systolic BP (Pa)",
    colour = "Arm", fill = "Arm"
  ) +
  theme_minimal(base_size = 11) +
  theme(legend.position = "none",
        strip.text = element_text(face = "bold"))

ggsave(file.path(plot_dir, "plot_2_sbp_trajectories.pdf"), p2,
       width = 12, height = 5, dpi = 300)
cat("  ✓ Saved to plots/plot_2_sbp_trajectories.pdf\n\n")


# ══════════════════════════════════════════════════════════════════════════════
# PLOT 3 — Laboratory Biomarker Change from Baseline (ALT & CRP)
# ══════════════════════════════════════════════════════════════════════════════
#
# Rationale
# ---------
# In DM1, hepatic and inflammatory markers merit close surveillance.  Alanine
# aminotransferase (ALT) is a standard liver function marker; C-reactive
# protein (CRP) captures systemic inflammation, which is increasingly studied
# in muscular dystrophies.  Showing *change from baseline* (CHG) rather than
# raw values lets us focus on within-patient shifts — the natural framing for
# a longitudinal study and for the materialized views proposed in the dynamic
# analysis system.
#
# What this shows
# ---------------
# Box-plots of CHG by visit, faceted by parameter and treatment arm, with
# a reference line at zero (no change).  This reveals both the central
# tendency and spread of treatment effects over time.
# ──────────────────────────────────────────────────────────────────────────────

cat("▸ Plot 3 : Lab biomarker change from baseline …\n")

lab_chg <- adlb %>%
  filter(PARAMCD %in% c("ALT", "CRP"),
         AVISIT != "",
         !is.na(CHG),
         !is.na(AVISITN)) %>%
  select(USUBJID, ARM, PARAMCD, PARAM, AVISIT, AVISITN, CHG) %>%
  mutate(AVISIT = fct_reorder(AVISIT, AVISITN))

p3 <- ggplot(lab_chg, aes(x = AVISIT, y = CHG, fill = ARM)) +
  geom_hline(yintercept = 0, linetype = "dashed", colour = "grey40") +
  geom_boxplot(outlier.size = 0.7, outlier.alpha = 0.4,
               linewidth = 0.35, width = 0.7,
               position = position_dodge(width = 0.8)) +
  facet_wrap(~ PARAM, scales = "free_y", ncol = 1) +
  labs(
    title    = "Plot 3 - Change from Baseline in ALT and CRP Over Visits",
    subtitle = "Box-plots by treatment arm; dashed line = no change from baseline",
    x = "Scheduled visit",
    y = "Change from baseline",
    fill = "Treatment arm"
  ) +
  theme_minimal(base_size = 11) +
  theme(axis.text.x = element_text(angle = 35, hjust = 1, size = 8),
        legend.position = "top",
        strip.text = element_text(face = "bold", size = 11))

ggsave(file.path(plot_dir, "plot_3_lab_chg_baseline.pdf"), p3,
       width = 11, height = 8, dpi = 300)
cat("  ✓ Saved to plots/plot_3_lab_chg_baseline.pdf\n\n")


# ══════════════════════════════════════════════════════════════════════════════
# PLOT 4 — Kaplan-Meier Curves: Time to First Adverse Event
# ══════════════════════════════════════════════════════════════════════════════
#
# Rationale
# ---------
# Time-to-event analysis is the most information-rich way to compare safety
# profiles across treatment arms.  The ADAETTE dataset records time to first
# adverse event; the Kaplan-Meier estimator gives us non-parametric survival
# curves and the log-rank test provides a formal between-arm comparison.
# In the proposed dynamic analysis system, this type of analysis would be
# exposed as a parameterized module that researchers can invoke from a
# notebook, specifying the event of interest, stratification variables, and
# covariates.
#
# What this shows
# ---------------
# Kaplan-Meier survival curves (P(no AE yet)) stratified by treatment arm,
# with 95 % confidence bands, number-at-risk table, and log-rank p-value
# annotation.
# ──────────────────────────────────────────────────────────────────────────────

cat("▸ Plot 4 : Kaplan-Meier — time to first adverse event …\n")

# Pick the first event parameter available in the dataset
tte_params <- adaette %>% distinct(PARAMCD, PARAM)
cat("  Available TTE parameters:\n")
print(tte_params, n = Inf)

# Select time-to-first-AE parameter (clinically most relevant)
selected_param <- if ("AETTE1" %in% tte_params$PARAMCD) {
  "AETTE1"
} else {
  tte_params %>% filter(grepl("first", PARAM, ignore.case = TRUE)) %>%
    slice(1) %>% pull(PARAMCD)
}

tte_data <- adaette %>%
  filter(PARAMCD == selected_param,
         !is.na(AVAL),
         !is.na(CNSR)) %>%
  select(USUBJID, ARM, AVAL, CNSR, PARAM) %>%
  distinct(USUBJID, .keep_all = TRUE) %>%
  mutate(
    event    = 1 - CNSR,           # CNSR=0 → event, CNSR=1 → censored
    time_wks = AVAL / 7            # convert days → weeks for readability
  )

event_label <- tte_data %>% pull(PARAM) %>% unique() %>% first()

cat(sprintf("  Selected parameter : %s  (%s)\n", selected_param, event_label))
cat(sprintf("  Events / N         : %d / %d\n", sum(tte_data$event), nrow(tte_data)))

# Fit survival model
surv_obj <- Surv(time = tte_data$time_wks, event = tte_data$event)
km_fit   <- survfit(surv_obj ~ ARM, data = tte_data)

# Log-rank test
lr_test  <- survdiff(surv_obj ~ ARM, data = tte_data)
lr_pval  <- pchisq(lr_test$chisq, df = length(lr_test$n) - 1, lower.tail = FALSE)

cat(sprintf("  Log-rank p-value   : %.4f\n\n", lr_pval))

# Build a tidy data frame from the survfit object for ggplot
km_tidy <- broom::tidy(km_fit) %>%
  mutate(
    # Extract arm label from the strata string  "ARM=..."
    ARM = str_remove(strata, "^ARM=")
  )

# Number-at-risk table (at selected time points)
risk_times <- seq(0, max(km_tidy$time, na.rm = TRUE), length.out = 6) %>% round(1)
risk_summary <- summary(km_fit, times = risk_times)

risk_tbl <- tibble(
  time = risk_summary$time,
  n.risk = risk_summary$n.risk,
  ARM = str_remove(risk_summary$strata, "^ARM=")
)

# KM plot
p4_main <- ggplot(km_tidy, aes(x = time, y = estimate, colour = ARM, fill = ARM)) +
  geom_step(linewidth = 0.8) +
  geom_rect(
    aes(xmin = time,
        xmax = lead(time, default = max(time)),
        ymin = conf.low, ymax = conf.high),
    alpha = 0.10, colour = NA
  ) +
  annotate("text", x = max(km_tidy$time) * 0.65, y = 0.15,
           label = sprintf("Log-rank p = %.4f", lr_pval),
           size = 3.5, fontface = "italic", colour = "grey30") +
  scale_y_continuous(labels = scales::percent_format(), limits = c(0, 1)) +
  labs(
    title    = "Plot 4 - Kaplan-Meier Estimate: Time to First Adverse Event",
    subtitle = paste0(event_label, "  |  stratified by treatment arm"),
    x = "Time (weeks)",
    y = "Event-free probability",
    colour = "Treatment arm", fill = "Treatment arm"
  ) +
  theme_minimal(base_size = 11) +
  theme(legend.position = "top")

# Number-at-risk as a mini table beneath the plot
p4_risk <- ggplot(risk_tbl, aes(x = time, y = ARM, label = n.risk)) +
  geom_text(size = 3) +
  labs(x = "Time (weeks)", y = NULL, title = "Number at risk") +
  theme_minimal(base_size = 9) +
  theme(
    panel.grid = element_blank(),
    plot.title = element_text(size = 9, face = "bold"),
    axis.text.y = element_text(face = "bold")
  )

p4 <- gridExtra::grid.arrange(p4_main, p4_risk, ncol = 1, heights = c(4, 1))

ggsave(file.path(plot_dir, "plot_4_km_time_to_ae.pdf"), p4,
       width = 10, height = 7, dpi = 300)
cat("  ✓ Saved to plots/plot_4_km_time_to_ae.pdf\n\n")


# ══════════════════════════════════════════════════════════════════════════════
# Summary
# ══════════════════════════════════════════════════════════════════════════════

cat("══════════════════════════════════════════════════════════════\n")
cat("  All plots saved to: ", plot_dir, "\n")
cat("──────────────────────────────────────────────────────────────\n")
cat("  Plot 1 — Demographic overview        (descriptive)\n")
cat("  Plot 2 — SBP trajectories over time  (longitudinal)\n")
cat("  Plot 3 — ALT & CRP change from BL    (longitudinal/safety)\n")
cat("  Plot 4 — KM time to first AE         (survival / inferential)\n")
cat("══════════════════════════════════════════════════════════════\n")
cat("\nDone.\n")
