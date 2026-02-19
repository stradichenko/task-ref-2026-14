## Proposal for a Dynamic Analysis System for the DM1 Multi-Modal Dataset

### 1. Purpose and Scope

This document proposes the design of a dynamic analysis system for a database containing clinical, genomic, and proteomic data from 200 patients with Myotonic Dystrophy Type 1 (DM1), collected across 25 hospitals and entered by 13 different personnel. The system is intended to serve clinical researchers, biostatisticians, data managers, and domain specialists who need to work with this multi-modal dataset on a daily basis.

It addresses four capabilities that are essential for a dataset of this complexity: responsive query performance over heterogeneous tables, systematic exploration of biologically relevant correlations across data modalities, automated and on-demand generation of reports and dashboards, and architectural adaptability to evolving scientific questions, regulatory requirements, and data sources.

The starting point is the existing database as provided. The proposal describes the storage, access control, orchestration, and analytical layers that should be built around it, selecting technologies that are mature, open source, and well-suited to clinical research data. PostgreSQL is proposed as the relational engine for both operational and research workloads, the OMOP Common Data Model (CDM) as the standardized research schema, Keycloak for identity and access management, and Airflow or Prefect for pipeline orchestration. These choices are justified throughout the document in the context of the specific requirements of the DM1 dataset.

---

### 2. Architectural Principles

#### 2.1 Separation of operational and analytical workloads

The most fundamental design decision is to ensure that analytical queries never compete with the transactional workload that supports data capture, validation, and clinical workflows. The proposed architecture achieves this by maintaining two distinct PostgreSQL instances: an operational store that supports day-to-day data entry and management, and an OMOP CDM warehouse dedicated to research and analysis. A dedicated analytical layer draws from the OMOP warehouse and, where necessary, from read replicas of the operational store. This means that a researcher running a complex join across clinical diagnoses, CTG repeat lengths, and proteomic intensity profiles does not degrade the experience of a data entry operator at a hospital site.

In practice, all analytical queries are routed through a read-only connection pool pointed at the OMOP instance or at a streaming replica of the operational database. Write access to analytical artefacts—saved queries, materialized views, derived tables, report definitions—is managed through a separate schema or database that the analysis layer owns, so that researchers can persist intermediate results without touching source data.

#### 2.2 Governance-aware access

Every analytical query must execute within a governance framework that controls who can see which data and that logs all access for audit purposes. The proposed system uses Keycloak as its identity and access management layer: tokens carry role and site claims that the analysis components inspect before granting access to datasets or dashboards. A clinical researcher with site-scoped permissions sees only data from their hospital unless a broader access grant has been approved by a data access committee. An auditor can review which queries were executed, by whom, and over which patient subsets, because the analysis layer writes structured events to an append-only audit trail. This design ensures that enabling dynamic exploration does not create a governance blind spot.

#### 2.3 Reproducibility and versioning

Analytical work in a clinical research context must be reproducible. The system therefore treats queries, transformation scripts, cohort definitions, and report templates as versioned artefacts stored in git alongside the ETL and data quality code. Every report or dashboard panel references a specific version of its underlying query logic, and every materialized view records the data cut date and pipeline version from which it was built. This makes it possible, at any point, to reconstruct the exact dataset and logic behind a published finding or a regulatory submission.

---

### 3. Fast Query Performance

#### 3.1 Indexing strategy

The OMOP CDM warehouse proposed in Section 2.1, hosted on PostgreSQL, is the primary target for analytical queries. To support responsive performance on the kinds of queries that clinical researchers and biostatisticians commonly run, the system requires a purposeful indexing strategy rather than relying on default primary key indexes alone.

For the core OMOP tables—PERSON, VISIT_OCCURRENCE, CONDITION_OCCURRENCE, MEASUREMENT, OBSERVATION, DRUG_EXPOSURE—composite B-tree indexes are created on the columns most frequently used in filters and joins: person_id combined with the relevant date column (condition_start_date, measurement_date, visit_start_date), and concept_id fields that encode diagnoses, lab tests, medications, and DM1-specific questionnaire items. For genomic and proteomic extension tables that store variant calls and protein quantifications, indexes on sample identifiers, gene symbols, and protein accessions ensure that cross-modal joins resolve efficiently.

Where queries frequently filter by site or by data collection period, partial indexes scoped to specific site identifiers or date ranges can further reduce scan costs. The team reviews slow query logs on a monthly cadence using pg_stat_statements and EXPLAIN ANALYZE output, and adjusts indexes in response to actual usage patterns rather than speculative assumptions.

#### 3.2 Materialized views for common analytical patterns

Certain analytical patterns recur frequently enough to justify pre-computation. Materialized views in PostgreSQL serve this purpose well: they store the result of a complex query as a physical table, can be refreshed on a schedule, and are queryable with the same SQL interface as any other table.

For the DM1 dataset, the team defines materialized views for several high-value patterns. A patient-level summary view joins demographic attributes, disease severity indicators (CTG repeat length, muscular impairment rating scale scores), current medication status, most recent laboratory results, and sample availability flags into a single wide table that analysts can query without writing multi-table joins each time. A longitudinal measurement view pivots repeated measurements (laboratory values, ePRO scores, proteomic markers) into a time-series format indexed by patient and visit, which is the natural shape for trajectory analysis. A site-level completeness view aggregates missingness and data quality metrics per hospital, updated daily, and serves as the foundation for operational dashboards.

These materialized views are refreshed by scheduled Airflow or Prefect tasks that run during low-traffic windows, typically overnight. The refresh logic is version-controlled alongside the ETL code, and each refresh is logged with its start time, duration, row counts, and any errors encountered. Analysts are informed of the freshness of each view through metadata columns or a dedicated catalogue table.

#### 3.3 Connection pooling and query routing

To handle concurrent analytical sessions without overwhelming the database, the design places PgBouncer as a connection pooler in front of the OMOP warehouse. PgBouncer maintains a pool of persistent connections to PostgreSQL and multiplexes client sessions across them, which prevents the connection exhaustion that can occur when multiple researchers open long-lived notebook sessions simultaneously.

For queries that are particularly expensive—such as genome-wide scans across all variant records or full proteomic correlation matrices—the architecture routes them to a dedicated read replica kept in sync via PostgreSQL streaming replication. This ensures that heavy exploratory workloads do not affect the responsiveness of routine dashboard queries or scheduled report generation.

---

### 4. Exploration of Biologically Relevant Correlations

#### 4.1 Cross-modal data integration

The scientific value of the DM1 dataset lies largely in its multi-modal nature: the ability to relate clinical phenotypes (disease severity, symptom progression, treatment response) to molecular profiles (genomic variants, CTG repeat expansions, proteomic signatures). The analysis system must make cross-modal exploration practical rather than heroic.

At the database level, this is achieved through a carefully designed entity-relationship schema in which patients serve as the central linkage entity: clinical observations, genomic samples, and proteomic runs all carry foreign keys that trace back to a patient identifier. The materialized patient-level summary view described in Section 3.2 pre-joins the most commonly needed attributes from all three domains, so that a researcher can begin exploratory analysis with a single SELECT statement rather than constructing a chain of joins across half a dozen tables.

For more targeted investigations, the team provides a library of parameterized SQL templates and Python functions that encapsulate common cross-modal patterns. Examples include: retrieving all proteomic intensity values for a given protein across patients stratified by CTG repeat length category; comparing adverse event rates between patients with and without a specific genomic variant; and correlating longitudinal ePRO trajectories with baseline proteomic cluster assignments. These templates are stored in the project repository, documented with usage examples, and designed to accept cohort filters, date ranges, and variable selections as parameters.

#### 4.2 Interactive notebook environment

For exploratory work that goes beyond pre-built templates, the proposed system provisions containerized JupyterLab and RStudio Server instances that connect to the OMOP warehouse through read-only database credentials scoped by role. These environments are pre-configured with the libraries that the team uses most frequently: pandas, SQLAlchemy, scikit-learn, statsmodels, lifelines (survival analysis), and plotly for Python; tidyverse, survival, limma, DESeq2, and ggplot2 for R. Bioconductor packages for proteomic and genomic analysis—MSstats, VariantAnnotation, clusterProfiler—are also available.

Notebooks are the natural medium for the kind of iterative, hypothesis-driven exploration that characterizes translational research. A biostatistician can pull a cohort of patients with severe phenotypes, examine their proteomic profiles for differentially abundant proteins, check whether those proteins map to pathways already implicated in DM1 pathology, and document the entire reasoning chain in a single notebook that can be reviewed by collaborators or attached to a publication. Because the notebook connects to a governed, versioned data source and the environment itself is containerized, the analysis is reproducible by anyone with equivalent access.

#### 4.3 Cohort definition and characterization via OHDSI tools

For clinical researchers who prefer graphical interfaces over code, the OHDSI Atlas application—proposed for deployment on top of the OMOP warehouse—provides a powerful cohort definition and characterization capability. Researchers can define patient cohorts using inclusion and exclusion criteria expressed in terms of diagnoses, measurements, drug exposures, and temporal relationships, and then examine the characteristics of those cohorts—demographics, comorbidity profiles, treatment patterns—without writing SQL.

The analysis system integrates Atlas into the broader workflow by allowing cohort definitions created in Atlas to be exported as JSON specifications and reused in downstream Python or R analyses. This bridges the gap between clinical researchers who think in terms of patient populations and biostatisticians who need programmatic access to those same populations for statistical modelling. Cohort definitions, like queries and report templates, are stored in version control so that the exact population used in any analysis can be reconstructed.

#### 4.4 Statistical and machine learning workflows

Beyond descriptive exploration, the system supports structured analytical workflows for hypothesis testing, predictive modelling, and unsupervised pattern discovery. These workflows are implemented as modular Python or R scripts that consume data from the OMOP warehouse or from materialized views and produce standardized output artefacts: tables, figures, model objects, and performance metrics.

For the DM1 dataset, relevant workflows include survival analysis relating time-to-event outcomes (such as onset of cardiac conduction abnormalities or loss of ambulation) to baseline genomic and proteomic features; mixed-effects models accounting for the hierarchical structure of the data (patients nested within sites); and clustering analyses that group patients by multi-modal similarity to identify potential disease subtypes. Each workflow is parameterized so that it can be re-run on updated data, alternative cohort definitions, or different variable selections without rewriting code.

When machine learning models are trained—for example, a classifier that predicts disease progression category from a combination of clinical and proteomic features—the system logs model metadata (algorithm, hyperparameters, training data version, performance on held-out data) in a lightweight model registry. This ensures that models used in clinical decision support or in publications can be traced back to their training conditions and reproduced if challenged.

---

### 5. Reports and Dashboards

#### 5.1 Operational dashboards via Grafana

Grafana is proposed as the primary dashboarding tool for data quality and study operations monitoring. As an open source platform with native PostgreSQL support, it is well-suited to serving automatically refreshed dashboards accessible to data managers, site coordinators, and study leadership.

Key dashboard panels include: enrolment progress by site and over time; form completion rates and missingness heatmaps for critical variables; data query volumes and resolution times stratified by site and severity; distribution summaries for key clinical endpoints and biomarkers, updated with each ETL cycle; and site-level performance scorecards that highlight hospitals requiring additional support. These panels query the materialized views described in Section 3.2, which means they load in seconds rather than running expensive aggregations on demand.

Grafana dashboards are defined as code using Grafana's provisioning mechanism and stored in the project repository. This allows dashboard definitions to be reviewed, versioned, and deployed consistently across environments. Access to each dashboard is governed by roles managed in Keycloak: a site coordinator sees panels scoped to their hospital, while a data manager or study lead sees cross-site summaries.

#### 5.2 Research dashboards and self-service exploration via Apache Superset

For analytical dashboards that go beyond operational monitoring—interactive charts, ad-hoc filtering, cross-tabulations, and exportable visualizations—Apache Superset is proposed as a complementary tool. Superset connects to the OMOP PostgreSQL warehouse through a read-only SQL connection and provides a browser-based interface where researchers can build charts, combine them into dashboards, and share them with colleagues, all without writing code.

Superset is particularly well-suited to the kind of exploratory data visualization that precedes formal statistical analysis. A clinical researcher can, for example, create a scatter plot of CTG repeat length against a proteomic biomarker, colour-code it by disease severity category, filter it to a specific age range, and save the result as a dashboard that automatically updates when the underlying data are refreshed. Because Superset enforces row-level security through database roles mapped to claims from the Keycloak identity layer, the governance guarantees described in Section 2.2 are preserved.

#### 5.3 Automated and scheduled reports

Certain reports must be generated on a fixed schedule and distributed to defined recipients: monthly data quality summaries for the steering committee, quarterly enrolment and safety reports for regulatory authorities, and periodic cohort characterizations for the scientific advisory board. The analysis system automates these using Airflow or Prefect DAGs that execute parameterized Python or R scripts, render the output as PDF or HTML documents using tools such as Quarto or Jupyter nbconvert, and distribute the results via email or deposit them in a governed document store.

Each automated report is tied to a specific version of its generating script, a specific data cut, and a specific set of parameters. The execution log records when the report was generated, which data version it used, and whether any warnings or errors occurred during rendering. This level of traceability is important for regulatory submissions and for maintaining trust in the numbers presented to governance bodies.

---

### 6. Adaptability to Evolving Requirements

#### 6.1 Schema evolution and migration management

Scientific questions, regulatory expectations, and data sources change over the life of a multi-year clinical research programme. The analysis system must accommodate these changes without breaking existing queries, dashboards, or reports. The team manages schema evolution through a disciplined migration workflow using tools such as Alembic (for SQLAlchemy-managed schemas) or Flyway (for raw SQL migrations). Each migration is a versioned, reversible script that modifies the database schema in a controlled way: adding new columns or tables, renaming fields, adjusting constraints, or creating new materialized views.

When a new data modality is introduced—for example, imaging biomarkers or wearable sensor data—the process follows a well-defined pattern: the data engineering team designs the new tables and relationships, the data quality team extends the validation suite with checks appropriate to the new domain, the ETL team adds extraction and transformation logic, and the analysis team creates or updates materialized views and templates. Because each of these steps is expressed as code and managed through version control, the entire chain can be reviewed, tested in a staging environment, and deployed as a coordinated release.

#### 6.2 Configuration-driven pipelines

To minimize the amount of code that must change when requirements evolve, the system favours configuration over hard-coding wherever practical. ETL pipelines read their source-to-target mappings, vocabulary versions, and transformation rules from JSON or YAML configuration files rather than embedding them in procedural logic. Report templates accept parameters that control which variables, cohorts, date ranges, and stratification factors are included. Dashboard definitions are stored as declarative specifications that can be modified by analysts without touching application code.

This configuration-driven approach means that many common changes—adding a new questionnaire to the study, extending an existing dashboard with a new panel, or adjusting a plausibility range for a laboratory test—can be made by editing a configuration file and triggering a pipeline re-run, rather than by modifying, reviewing, and deploying new code. The boundary between configuration and code is documented, so that team members know which changes they can make independently and which require a development cycle.

#### 6.3 Modular and composable analytical components

The analytical layer is designed as a set of loosely coupled, composable components rather than a monolithic application. Each component—a cohort extraction function, a statistical model, a visualization template, a report section—has a well-defined interface (inputs, outputs, parameters) and can be developed, tested, and versioned independently. This modularity makes it straightforward to replace or extend individual components as scientific methods evolve or as new tools become available.

For example, if the team decides to adopt a new dimensionality reduction technique for multi-modal clustering, they implement it as a new module that accepts the same patient-by-feature matrix produced by the existing data extraction components and outputs cluster assignments in the same format consumed by downstream visualization and reporting components. The rest of the pipeline does not need to change. Similarly, if a new regulatory requirement mandates a specific format for safety reports, only the report rendering component needs to be updated, not the data extraction or statistical logic.

#### 6.4 Extensibility for new data modalities and external sources

The DM1 dataset may, over time, grow to incorporate additional data types beyond clinical observations, genomic variants, and proteomic quantifications. Wearable device data, imaging, electrophysiology, or patient-generated health data from connected apps are plausible extensions. The analysis system accommodates this growth through the same pattern used for the initial three domains: new data are stored in domain-specific tables linked to the central patient entity, new materialized views integrate them into the analytical layer, and new templates and dashboard panels expose them to researchers.

External data sources—national registries, published reference cohorts, publicly available molecular databases—can also be integrated in a controlled way. The team defines connectors that pull external reference data into staging tables, applies quality checks comparable to those used for internal data, and then links or joins external records to the DM1 dataset through standardized identifiers (OMOP concept IDs, gene symbols, protein accessions). Each external source is documented with its provenance, update frequency, and licence terms, so that analysts understand the origin and limitations of every data element available in the analysis environment.

---

### 7. Implementation Roadmap

The dynamic analysis capabilities described in this proposal do not need to be delivered all at once. A phased approach over approximately three months allows the team to deliver early value while building toward the full system.

During the first month, the team focuses on foundations: loading the provided database into the PostgreSQL operational store, designing the OMOP CDM schema and initial ETL mappings, defining the indexing strategy, deploying Keycloak with the role model, and establishing the notebook environment with read-only access to the development database. This gives biostatisticians and clinical researchers an early sandbox in which to validate the data model against real analytical questions.

During the second month, as the OMOP warehouse is populated and the ETL pipelines stabilize, the team deploys Grafana dashboards for data quality monitoring, configures Apache Superset with initial chart templates, creates the core materialized views, and begins building the library of parameterized SQL templates and analytical modules. Integration with Atlas for cohort definition is validated end-to-end.

During the third month, the team automates scheduled report generation, conducts performance testing under realistic concurrent query loads, and documents the full analytical catalogue—available materialized views, templates, dashboards, and report definitions—so that the research team can work independently once the system enters routine operation.

Throughout all three months, every analytical artefact is version-controlled, every access is governed by Keycloak roles, and every query against patient data is logged. The result is a dynamic analysis system that is not only powerful and flexible, but also auditable, reproducible, and built with governance as a first-class concern from the outset.
