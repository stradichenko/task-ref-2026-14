## Data Quality and Uniformity Evaluation Plan for the DM1 Multi-Modal Dataset

### 1. Purpose and Scope

This document sets out, in practical and operational terms, how to evaluate and improve the quality and uniformity of a multi-modal dataset comprising clinical, genomic, and proteomic data from 200 patients with Myotonic Dystrophy Type 1 (DM1), collected across 25 hospitals and entered by 13 personnel. It is written from the perspective of a clinical data management function responsible for turning a raw, heterogeneous dataset into a cleaned, analysis-ready resource, in collaboration with analysts, domain experts, and site personnel.

The plan pursues five main aims. 
First, it describes how to detect and correct structural and semantic inconsistencies, duplicates, and lack of normalization, so that the dataset behaves as a coherent whole rather than as a collection of loosely related files. 
Second, it outlines how to identify and remediate data entry errors and implausible values, including the clinically meaningful range checks and edit rules to be applied. 
Third, it defines a framework for characterizing and addressing missingness patterns and cross-form discordances, with particular attention to how these affect interpretation of DM1 outcomes. 
Fourth, it specifies how to quantify site- and user-level variation in data quality, enabling targeted training and process improvement. 
Finally, it explains how to ensure that all cleaning operations remain auditable and reproducible, using version control, audit trails, and standardized query workflows.

---

### 2. Preparation: Inventory, Metadata, and Environment

#### 2.1 Data inventory and source characterization
The first task is to gain a complete and structured overview of what data exist and how they relate to one another. In practice, this means building an inventory that lists, for every source file or database table, whether it belongs to the clinical, genomic, or proteomic domain, what its intended purpose is, and how it links to other tables. To visualize these relationships and dependencies, it is recommended to create a relational schema diagram.

On the clinical side, the inventory typically includes demographics, diagnoses, medications, visit or encounter records, ePRO instruments, clinician-reported scales, and adverse event logs. For each of these, the team records which column acts as the primary key, which columns function as foreign keys to other tables (for example, patient identifiers, visit identifiers, site identifiers), and which controlled vocabularies should apply (for example, ICD-10 or SNOMED CT for diagnoses, ATC codes for medications, and LOINC for laboratory measurements). A similar exercise is carried out for genomic data, where the focus is on identifying variant call files, annotation tables, and per-sample metadata, and for proteomic data, where the team records which files hold raw mass spectrometry signals, which contain processed peptide or protein-level intensities, and where any normalization logs are stored.

As the inventory is developed, the team explicitly documents expected cardinalities (for example, one patient to many visits; one sample to one genomic library to many variants) and checks whether the current data obey these relationships. This information feeds directly into later structural integrity checks and helps the team decide which joins and linkage strategies are safe to use in downstream analyses.

#### 2.2 Metadata and codebook alignment

Once the inventory exists, the next step is to ensure that the documentation about each variable matches what is actually present in the dataset. The data management team consolidates all available data dictionaries, case report forms, laboratory manuals, genomic and proteomic processing standard operating procedures, and any mapping documents that already exist for previous studies or pilot work. For every variable in every table, the team then creates or updates a codebook entry that records the variable name and label, its domain (clinical, genomic, or proteomic), the table it belongs to, and its intended type.

For numerical variables this description includes permitted ranges and units; for categorical variables it includes the list of expected categories and their coding schemes; for derived variables it captures the derivation logic and dependencies. Simple profiling queries in SQL or pandas scripts are then used to compare the documented expectations with the reality of the data. When mismatches are found—for example, a variable that the codebook describes as a numeric value in mmol/L but which in practice contains a mix of text values and different units—these become explicit issues that must be resolved with the relevant domain experts. This alignment process is critical, because many of the later quality checks will be based on the ranges, categories, and derivations defined here.

#### 2.3 Technical environment and tools

Before detailed checks begin, the data management and technical teams set up an environment that supports both exploratory work and repeatable pipelines. A common pattern for this kind of project is to load the raw data into a PostgreSQL database or an equivalent relational store that will function as the working hub for profiling and cleaning. On top of this, analysts typically use Python, with libraries such as pandas and SQLAlchemy, in combination with Jupyter notebooks for interactive exploration. As soon as the main checks are identified, they are migrated into structured validation suites using pandera for DataFrame schema and constraint definitions together with pytest for execution, which allows validations to be expressed as code, version controlled, and executed automatically.

For visualization and site-level comparisons, Grafana—already part of the platform's observability stack—is connected to the same PostgreSQL database to serve data quality dashboards. In addition, the team prepares domain-specific tools: for genomic data, this often means using bcftools and plink together with Python or R libraries to perform variant-level quality control and to assess sample concordance; for proteomic data, it can involve setting up R-based pipelines using Bioconductor packages such as MSstats to examine intensity distributions, missingness, and batch effects. Where clinical data are or will be mapped to an OMOP Common Data Model instance, OHDSI tools such as Achilles and the DataQualityDashboard are installed so that quality checks can be re-run on the standardized model.

---

### 3. Relational versus Non-Relational Storage and Its Implications for Data Quality

#### 3.1 Overview of the two paradigms

In broad terms, database systems fall into two families. Relational databases—PostgreSQL, MySQL, Oracle, SQL Server—organize data into tables with fixed schemas, enforce referential integrity through primary and foreign key constraints, and expose a declarative query language (SQL) that supports complex joins, aggregations, and transactional guarantees (ACID properties). Non-relational (NoSQL) databases—document stores such as MongoDB, wide-column stores such as Apache Cassandra, key-value stores such as Redis, and graph databases such as Neo4j—relax one or more of these constraints in exchange for flexible schemas, horizontal scalability, or optimized access patterns for specific workloads.

Each paradigm carries distinct consequences for data quality. With a relational database, many quality rules can be pushed into the storage layer itself: column types, NOT NULL constraints, UNIQUE indexes, CHECK constraints, and foreign key relationships all act as a first line of defence against malformed or inconsistent data. A non-relational store, by contrast, typically delegates these responsibilities to application code, which means that quality enforcement depends entirely on the discipline and completeness of the software layer above the database.

#### 3.2 Why a relational database is preferred for the DM1 platform

For a multi-modal clinical research dataset of the kind described in this plan—200 patients, 25 hospitals, 13 data entry personnel, with tightly linked clinical, genomic, and proteomic tables—a relational database is the preferred foundation. Several characteristics of the project make this choice decisive.

**Referential integrity across domains.** The DM1 dataset is built around well-defined entities (patients, visits, samples, variants, protein quantifications, consent records) connected by explicit relationships with known cardinalities. A relational database enforces these relationships at the engine level: it is not possible to insert a visit record that references a nonexistent patient, or a variant that points to a nonexistent genomic library, unless the constraint is explicitly bypassed. In a document store, these cross-collection references would need to be validated by application logic, and any gap in that logic would silently introduce orphaned or dangling records—precisely the structural integrity problems described in Section 4.1 of this document.

**Schema enforcement and type safety.** Clinical and regulatory data require strict typing: dates must be dates, numeric lab results must be numeric, coded fields must draw from controlled vocabularies. A relational schema declares these types once, and the database rejects any value that does not conform. In a schema-less document store, a single malformed record—a string where a number is expected, a date in an unexpected format—can enter the system without error and propagate downstream, where it may only surface as a subtle analytical artefact weeks or months later. The cost of retroactive detection and repair far exceeds the cost of upfront enforcement.

**Transactional consistency and audit trails.** The governance framework for this project requires that every data modification be atomic and fully traceable. Relational databases provide ACID transactions, which guarantee that a correction to a clinical value and the corresponding entry in the audit trail either both succeed or both fail. This is essential for regulatory compliance and for the append-only audit model described in the cleaning and traceability procedures. Most document and key-value stores offer weaker consistency models—eventual consistency, or transactions scoped to a single document—which complicate the implementation of reliable, cross-table audit logging.

**Mature tooling for quality and analytics.** The ecosystem around relational databases is particularly well-suited to clinical data management. SQL is the lingua franca for profiling queries, completeness calculations, cross-table concordance checks, and the kinds of site-level and user-level comparisons that drive the monitoring described in this plan. Tools such as the OHDSI DataQualityDashboard, Achilles, and Atlas all assume a relational backend (specifically PostgreSQL for OMOP CDM). Similarly, pandera and Great Expectations integrate naturally with tabular, typed data extracted from relational stores. Moving to a non-relational store would require significant additional engineering to replicate capabilities that already exist and are well-tested in the relational world.

**FHIR and OMOP alignment.** Although FHIR resources are often serialized as JSON, the platform's architecture uses a relational operational schema internally and exposes FHIR at the boundary through a facade layer. The OMOP Common Data Model is itself a relational schema. Maintaining a relational store at the centre of the pipeline means that ETL to OMOP is a relational-to-relational transformation—straightforward to express in SQL or dbt—rather than a document-to-relational mapping that would require additional extraction, flattening, and type coercion logic, each step introducing new opportunities for data quality degradation.

#### 3.3 Where non-relational approaches may complement the relational core

This does not mean that non-relational technologies have no role in the platform. Specific, bounded use cases may benefit from them. For example, raw genomic files (VCF, BAM, FASTQ) and mass spectrometry output are large, semi-structured artefacts that are best stored in object storage (such as MinIO or an S3-compatible service) rather than as rows in a relational table; metadata and quality flags for these artefacts are then stored relationally and linked to the object storage paths. Similarly, caching layers (Redis), full-text search indexes (OpenSearch), and real-time event streaming (Apache Kafka) are non-relational components that can sit alongside the relational core for specific performance or architectural needs without undermining the data quality guarantees that the relational schema provides.

The guiding principle is that all data whose correctness, completeness, and traceability are subject to the quality checks defined in this plan should reside in, or be governed by, the relational database. Non-relational stores may participate in the broader platform as auxiliaries, but they do not replace the relational layer for any data that will be validated, queried, audited, or reported as part of the data management function.

---

### 4. Data Quality Dimensions, Metrics, and Checks

#### 4.1 Structural integrity and conformance

The first dimension evaluated is structural integrity: whether the dataset conforms to the agreed schema and respects basic relational rules. This begins with checking key constraints. For every table, the uniqueness of the declared primary key is verified using simple SQL queries or pandas groupings, and any instances of duplicate keys are catalogued for follow-up. Foreign key relationships—such as visit records that should always link to a known patient, or sample records that should always link to a valid patient and possibly a visit—are assessed by counting how many child records have no corresponding parent. These simple counts immediately show whether parts of the dataset have become detached from their intended hierarchy.

Data types and formats are then examined systematically. Each column is parsed according to its declared type, and the proportion of values that fail to parse as dates, numerics, or booleans is logged. Coded fields such as diagnosis or medication codes are scanned for mixed encodings—for example, a column that sometimes contains numerical codes and sometimes raw text descriptions. At this stage the clinical data management function can already propose specific remediation actions: redefining column types in the working database, splitting columns that mix codes and descriptions, or creating staging fields where raw text is mapped to codes.

Finally, structural conformance is checked against external standards. Clinical codes are joined to reference tables drawn from SNOMED CT, ICD-10, ATC, or LOINC, and the proportion of codes that match a valid entry is recorded. For genomic variants, the team can use regular expressions and external annotation resources to check whether HGVS expressions are syntactically valid and whether reported rsIDs exist. Where mismatches are found, they are flagged as either transcription errors to be corrected, legacy codes that require mapping, or genuinely novel entries that need clinical review. All of these checks are implemented as pandera schemas and pytest test suites, so they can be re-run consistently as the dataset evolves.

#### 4.2 Uniformity, normalization, and standardization

Even when the structure of the dataset is sound, the same concept can be represented in multiple ways, which complicates analysis. The uniformity checks therefore look for inconsistent units, scales, coding schemes, and naming conventions. For each quantitative variable, especially laboratory results and biomarker measurements, the team enumerates all units present in the data and examines their frequencies. If the same test appears in both mg/dL and mmol/L, for example, clinical reference tables are used to define unambiguous conversion factors, and exploratory plots are used to verify that converted values fall into plausible ranges.

For categorical variables such as sex, race, and binary indicators, the team extracts the distinct values and their counts, then constructs mapping tables that translate all observed variants to approved standard categories. In practice, this means deciding that values such as "M", "Male", and "male" will all be converted to a single canonical representation, and determining how to handle unexpected free text responses. These mapping tables become an explicit artefact in the data management repository and are maintained as part of the study configuration.

Identifiers also receive careful attention. Patient IDs that sometimes appear with leading zeros and sometimes without, or site identifiers that change format over time, can quietly break linkage between tables. The data management team writes dedicated scripts to normalize identifier formats across all domains, and they introduce validation checks to ensure that only normalized forms appear in downstream tables. Wherever a transformation is applied—converting units, collapsing categories, or regularizing identifiers—the scripts retain both the original and normalized values where appropriate and log the transformation so that it can be audited later.

#### 4.3 Duplicate detection (patients, samples, records)

The duplicate detection workstream proceeds in layers. The team first searches for exact duplicates, where all key fields in a record match another record. These can often be removed or merged with minimal risk, provided that the original ingestion logs are checked. Next, they look for near-exact duplicates, such as records that share the same patient identifier, visit date, and site, but differ only in non-critical fields like free-text comments. These are reviewed to decide whether they reflect true repeated events or double entry of the same event.

To capture more subtle cases, the team applies probabilistic record linkage, using libraries such as recordlinkage or Dedupe in Python. Here, combinations of demographic attributes (date of birth, sex), site identifiers, and enrollment dates are used to generate similarity scores between pairs of records that might represent the same individual but with slightly different identifiers. Candidate matches are then triaged by clinical data managers, sometimes in consultation with site staff.

For genomic and proteomic samples, the data itself can help resolve duplication and mislabeling. The team computes pairwise genotype concordance between samples using tools like plink, or correlations between proteomic intensity profiles, to detect samples that are implausibly similar or identical despite being labeled as different individuals. When duplicates or swaps are confirmed, a controlled process is used to decide which record will serve as the master, how other records will be linked or retired, and how this decision is recorded. All merges and retirements are logged in a dedicated audit table that captures which identifiers were involved, who made the decision, when, and for what reason.

#### 4.4 Missingness and completeness

Missingness can be managed if patterns are understood. The data management team begins by calculating simple completeness metrics at the variable level, expressing the proportion of non-missing values for each field. Variables that correspond to core endpoints or key covariates are classified as high-priority, and any that show high levels of missingness are flagged for special attention. Less critical fields are still tracked, but may be deprioritized if resources are limited.

The analysis is then stratified by site, by data entry personnel, and by time. Completion rates per site and per user, broken down by month or by protocol visit window, are plotted so that systematic gaps become visible. For example, the team might discover that a particular laboratory test is never reported from three of the 25 hospitals, indicating either a local practice difference or a configuration problem in the data collection system. Heatmaps of missingness across variables and patients, generated using pandas or dedicated R packages such as naniar, help to reveal patterns where clusters of variables are often missing together, suggesting underlying workflow issues.

At this stage, the data manager works with clinicians and statisticians to distinguish missingness that is expected by design—such as questions that are only asked if a prior response is positive—from missingness that reflects protocol deviations or system failures. Thresholds are defined for when a variable or a site should trigger a formal issue, for instance when a critical variable is missing in more than a pre-agreed percentage of records. These thresholds then feed into dashboards and routine reports that monitor completeness over time.

#### 4.5 Plausibility, outliers, and data entry errors

To guard against data entry errors and implausible values, the team implements a combination of rule-based and statistical checks. Clinical experts help define biologically plausible ranges for vital signs, laboratory results, age, BMI, and DM1-specific scales. These ranges are encoded as edit rules in SQL or Python and then formalized as pandera schemas and pytest suites so they can be run automatically. Logical rules are added to enforce internal consistency, such as ensuring that the age at diagnosis does not exceed the age at last visit, that visit dates do not lie in the future relative to the data extract, and that pregnancy status, where relevant, is consistent with recorded sex and age.

For quantitative variables, descriptive statistics and robust outlier measures (such as interquartile ranges or median absolute deviation–based z-scores) are computed per site and batch. Proteomic intensity distributions are examined per run and per sample to identify spectra that are unusually low or high, or that display patterns suggestive of technical artefacts. The team uses histograms, boxplots, and time-series plots in notebooks or dashboards to review these patterns with clinicians, geneticists, and proteomics experts.

Additional attention is paid to subtle anomalies, such as heaping around round numbers that could indicate guessing or habitual rounding by data entry personnel, and to users who appear to enter data at implausibly high speeds or with repetitive patterns. When suspicious values or patterns are identified, the response strategy is predefined: simple probable typos are queried back to the site for confirmation and correction; clearly impossible values may be censored or excluded in analysis datasets, with the original preserved in the raw layer; and more complex issues are escalated to the principal investigator or domain specialists.

#### 4.6 Cross-form and cross-modal discordances

Because this dataset spans multiple forms and modalities, it is important to look for inconsistencies across them rather than only within single tables. Clinical cross-form concordance is assessed by comparing diagnoses recorded at baseline with those that appear later in problem lists, discharge summaries, or adverse event forms. Medication lists maintained by clinicians are reconciled against ePRO-reported changes, and serious events reported by patients are checked against hospitalization records or clinician notes where available. When the same concept appears in several places, discrepancies are turned into structured issues that can be followed up.

Temporal consistency is another focus. The team checks that disease onset dates make sense relative to sample collection dates, that samples are not labeled as collected before enrollment or after documented withdrawal unless a specific justification exists, and that longitudinal trends in key biomarkers are clinically plausible. Sudden, dramatic changes in otherwise stable measurements may indicate either real clinical events or data errors; part of the data management role is to ensure that such cases are surfaced rapidly so that the clinical team can determine which is which.

Cross-modal comparisons provide additional quality signals. For example, sex recorded in the clinical data can be compared with genetically inferred sex based on chromosome coverage or sex-linked markers in the genomic data. Known molecular signatures associated with DM1 may also be used in a cautious way to check whether the proteomic and genomic patterns roughly align with clinical severity classifications. Automated scripts implement these comparisons and write any discordances into a dedicated table of patient-level flags. Each flag includes enough context for a clinical data manager to decide whether to open a formal query, request re-analysis of molecular data, or simply document the discrepancy as unresolved but understood.

#### 4.7 Site and personnel performance

Given the multi-centre nature of the dataset, the data management team needs visibility into how data quality varies across the 25 hospitals and among the 13 data entry personnel. To achieve this, they construct a set of site- and user-level indicators. For each site, the team calculates completeness rates for key forms and variables, counts how often edit checks fail per hundred records, and measures the time between a query being raised and being resolved. For individual personnel accounts, they track the volume of records entered or edited and derive simple proxies for error rates based on how often their entries trigger validation failures or later corrections.

These metrics are exposed through Grafana dashboards connected to PostgreSQL and are regularly reviewed in coordination meetings. Sites that perform well help define best practices, while those with persistent issues are offered targeted training or process support. Importantly, the purpose of these metrics is not punitive but corrective: they provide the evidence base needed to adjust workflows, refine edit checks, or allocate additional support where it will have the greatest impact on overall data quality.

---

### 5. Correction, Cleaning, and Traceability Procedures

#### 5.1 Governance and audit trail

All corrective actions taken on the dataset must be embedded within a governance framework that is consistent with the broader data management plan and regulatory requirements. This means that no primary data value—whether clinical, genomic, or proteomic—should be overwritten silently. Instead, any change is recorded with the original and new values, the identity and role of the person who made the change, the time at which the change occurred, and a brief explanation of why it was necessary. In practical terms, this is implemented as an append-only audit table in the operational database, with strict access controls and reporting views designed for auditors and quality assurance teams.

From a tooling perspective, the same principles that underpin RBAC and audit trails in the prospective data collection platform apply here: updates are performed through controlled interfaces that automatically log the required metadata, rather than through ad hoc direct edits in the database. This ensures that every cleaning step remains traceable and that reconstructed histories can be produced on demand.

#### 5.2 Query management workflow

Discrepancies identified by the checks in Section 3 are not resolved informally; they are routed through a structured query management workflow. The team maintains a centralized query log that captures all issues, including missing critical data, implausible values, cross-form discordances, suspected duplicates, and anomalies in genomic or proteomic profiles. Each entry in this log receives a unique query identifier, links to the relevant patient or sample and site, specifies the domain (clinical, genomic, or proteomic), and summarizes the underlying rule or check that triggered the issue.

Queries are also classified by severity—critical, major, or minor—and assigned a suggested due date. Responsibility for responding is clearly assigned to a site contact or a specific data entry person. The log records status transitions such as open, answered, resolved, and closed, along with timestamps. When a correction is made to address a query, the query identifier is referenced in the audit trail so that it is always possible to reconstruct which issue motivated a particular change. This approach scales from a small DM1 dataset to much larger registries while preserving transparency.

#### 5.3 Standard operating procedures for corrections

Standard operating procedures (SOPs) define how different types of issues should be corrected. For straightforward clinical data entry errors—for example, a transcription mistake or a mis-click—the SOP typically authorizes the site to correct the value directly, provided a clear reason is recorded and the original value remains visible in the audit history. For ambiguous or high-impact cases, such as a change to a primary endpoint or a reclassification of a serious adverse event, the SOP may require consultation with the principal investigator or data monitoring committee before a change is approved.

For genomic and proteomic data, the procedures tend to focus on sample-level decisions. If quality control analyses suggest that a sample has been swapped, contaminated, or processed incorrectly, the default action is not to delete the data but to mark the sample as failing QC and to exclude it from downstream analyses. Relabeling samples may be permitted when a mislabeling can be established unambiguously, but only after multi-person review and documentation. Sample- and feature-level QC flags (for example, PASS or FAIL status) are stored alongside the data so analysts can filter accordingly.

When confirmed duplicates are found, a controlled merge process is followed. Rules specify which record becomes the master, how conflicting values are resolved, and how identifiers of retired records are preserved as aliases. These merges are performed in a way that preserves linkages to all relevant tables and fully documents the rationale and approvals involved.

#### 5.4 Versioning and releases

To maintain reproducibility, the team treats cleaned datasets as versioned artefacts. Each analysis dataset, whether used for an interim analysis, a publication, or an extract shared with collaborators, is tied to a specific snapshot of the source data and a specific version of the cleaning and transformation logic. A simple but effective practice is to stamp each dataset with a data cut date and a code version identifier corresponding to a tag in a git repository.

Alongside the datasets, the team maintains a human-readable changelog that summarizes major changes between releases—for example, when a new set of range checks was introduced, when a batch of duplicates was resolved, or when a group of samples was excluded after failing genomic QC. All scripts, normalization maps, and pandera schemas and pytest validation suites are stored in version control so that any release can be regenerated if needed and its provenance can be inspected.

---

### 6. Reporting and Continuous Improvement

#### 6.1 Routine data quality reporting

Once the initial round of checks and corrections is established, data quality monitoring becomes a routine activity rather than a one-off project. On a recurring schedule—often monthly for a dataset of this size—the team generates standardized reports that summarize key completeness, plausibility, and consistency metrics, stratified by site and by data entry personnel. These reports also present statistics on query volumes, distinguishing between open, recently answered, and fully resolved issues, so that stakeholders can see where bottlenecks remain.

The reports are circulated to clinical leadership, data management, and site coordinators, and they form a standing agenda item for governance meetings. Over time, this creates a feedback loop in which sites can see the effect of their improvements and where the central team can track whether new issues emerge as additional data are collected.

#### 6.2 Feedback loop with sites and technical teams

The findings from data quality monitoring are most valuable when they lead directly to concrete changes. When certain variables repeatedly trigger edit checks or generate many queries, the data management team can work with form designers to clarify wording, adjust response options, or revise instructions. If specific thresholds are found to be either too strict or too permissive, those checks can be refined to reduce noise while still catching true errors. Training materials for sites and data entry staff are updated in light of recurring problems, with emphasis placed on the data elements that most influence the interpretability of DM1 outcomes.

Not all issues are human; some are technical. For example, synchronization failures between mobile data capture and the central database, or user interface behaviours that encourage accidental skipping of items, can only be resolved by the development team. The data management group therefore channels such systemic issues into a formal ticketing system, tracks their resolution, and verifies through subsequent data quality reports that the underlying problems have indeed been fixed.

#### 6.3 Alignment with downstream models (FHIR, OMOP)

Finally, because the broader DM1 platform uses FHIR for interoperability and OMOP as a research data model, data quality is reassessed after mapping. As clinical, genomic, and proteomic data are transformed into FHIR resources and OMOP tables, the team re-runs appropriate quality tools, for example FHIR validators on resource bundles and the OHDSI DataQualityDashboard on the OMOP instance. Differences between pre- and post-mapping metrics are examined carefully: if the mapping process introduces new missingness, changes code distributions, or creates structural anomalies, these issues are traced back either to the ETL logic or to misunderstandings about the source data.

By treating mapping as another transformation layer subject to the same discipline of explicit rules, validations, and auditability, the data management team ensures that improvements made in the original DM1 dataset are preserved all the way through to the analysis environment. This, in turn, increases confidence that any downstream findings are grounded in data that are not only rich and multi-modal, but also coherent, well-documented, and fit for their intended purposes.

