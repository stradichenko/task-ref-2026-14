## Dynamic Analysis System for the DM1 Multi-Modal Dataset — Summary

### 1. Purpose

This document summarises the design of a dynamic analysis system for a database containing clinical, genomic, and proteomic data from 200 patients with Myotonic Dystrophy Type 1 (DM1), collected across 25 hospitals and entered by 13 different personnel. The system targets four capabilities: fast queries over heterogeneous tables, exploration of biologically relevant correlations across data modalities, generation of reports and dashboards, and adaptability to evolving requirements. All proposed technologies are open source: PostgreSQL for storage, OMOP CDM for the research schema, Keycloak for access control, and Airflow or Prefect for orchestration.

---

### 2. Architectural Principles

**Separation of workloads.** Two PostgreSQL instances are maintained: an operational store for data entry and management, and an OMOP CDM warehouse for research. Analytical queries run against the warehouse or read replicas, so they never interfere with data capture at hospital sites.

**Governance-aware access.** Keycloak issues tokens carrying role and site claims. The analysis layer inspects these before granting access, and logs every query to an append-only audit trail. Researchers see only the data their role permits.

**Reproducibility.** Queries, cohort definitions, transformation scripts, and report templates are versioned in git. Every materialized view and report records its data cut date and code version, so any result can be reconstructed.

---

### 3. Fast Query Performance

**Indexing.** Composite B-tree indexes are created on the OMOP tables most used in analytical joins and filters (person_id + date columns, concept_id fields). Genomic and proteomic extension tables are indexed on sample identifiers, gene symbols, and protein accessions. Slow query logs are reviewed monthly and indexes adjusted accordingly.

**Materialized views.** Three pre-computed views accelerate common patterns: a patient-level summary joining demographics, disease severity, medications, lab results, and sample flags across all three domains; a longitudinal measurement view in time-series format for trajectory analysis; and a site-level completeness view for operational dashboards. Views are refreshed nightly by Airflow or Prefect and their freshness is tracked in a catalogue table.

**Connection pooling and routing.** PgBouncer pools connections to the OMOP warehouse, preventing exhaustion from concurrent notebook sessions. Particularly expensive queries (genome-wide scans, full proteomic correlation matrices) are routed to a streaming read replica.

---

### 4. Exploration of Biologically Relevant Correlations

**Cross-modal integration.** The patient entity is the central linkage point across clinical, genomic, and proteomic tables. The patient-level materialized view lets researchers begin cross-modal exploration with a single query. A library of parameterized SQL templates and Python functions encapsulates common patterns, such as stratifying proteomic intensities by CTG repeat category or comparing adverse event rates by genomic variant.

**Interactive notebooks.** Containerized JupyterLab and RStudio Server instances connect to the warehouse via read-only, role-scoped credentials. Environments ship with pandas, scikit-learn, statsmodels, lifelines, plotly, tidyverse, survival, limma, DESeq2, MSstats, VariantAnnotation, and clusterProfiler, among others.

**OHDSI Atlas.** For researchers who prefer graphical tools, Atlas provides cohort definition and characterization without SQL. Cohort definitions can be exported as JSON and reused in downstream Python or R scripts.

**Statistical and ML workflows.** Modular, parameterized scripts support survival analysis, mixed-effects models (patients nested within sites), multi-modal clustering, and predictive classifiers. Trained models are logged in a lightweight registry with algorithm, hyperparameters, data version, and performance metrics.

---

### 5. Reports and Dashboards

**Grafana** serves operational and data quality dashboards: enrolment progress, form completion rates, missingness heatmaps, query volumes, biomarker distributions, and site-level scorecards. Dashboards are defined as code and access is role-scoped.

**Apache Superset** provides self-service research dashboards with interactive charts, ad-hoc filtering, and exportable visualizations. Row-level security is enforced through database roles mapped to Keycloak claims.

**Automated reports.** Airflow or Prefect DAGs execute parameterized Python or R scripts on a fixed schedule, render output as PDF or HTML via Quarto or nbconvert, and distribute results to defined recipients. Each report is tied to a script version, data cut, and parameter set.

---

### 6. Adaptability to Evolving Requirements

**Schema evolution.** Alembic or Flyway manages versioned, reversible migration scripts. Adding a new data modality follows a repeatable pattern: new tables, new validation checks, new ETL logic, new materialized views and templates—all expressed as code and deployed as a coordinated release.

**Configuration over code.** ETL mappings, report parameters, and dashboard definitions are stored as JSON or YAML configuration files. Common changes—adding a questionnaire, adjusting a plausibility range, extending a dashboard—require editing a configuration file and triggering a re-run, not a full development cycle.

**Modular components.** Each analytical component (cohort extraction, statistical model, visualization template, report section) has a defined interface and can be replaced or extended independently. New methods or regulatory formats are accommodated by updating individual modules without altering the rest of the pipeline.

**Extensibility.** New data modalities (wearables, imaging, electrophysiology) and external sources (registries, molecular databases) are integrated through the same pattern: domain-specific tables linked to the patient entity, quality checks, materialized views, and dashboard panels. External sources are documented with provenance and licence terms.

---

### 7. Implementation Roadmap

**Month 1 — Foundations.** Load the database into PostgreSQL, design the OMOP schema and initial ETL, define indexes, deploy Keycloak, and stand up the notebook environment as an early analytical sandbox.

**Month 2 — Core capabilities.** Populate the OMOP warehouse, deploy Grafana and Superset dashboards, create materialized views, build the SQL template and analytical module library, and validate Atlas integration end-to-end.

**Month 3 — Automation and hardening.** Automate scheduled reports, conduct performance testing under concurrent load, and document the full analytical catalogue so the research team can operate independently.

Throughout all phases, every artefact is version-controlled, every access is governed by Keycloak, and every query against patient data is logged.
