## High-Level Architecture for the DM1 Prospective Data Collection Platform

This architecture describes a mobile-first, role-based platform for prospective data
collection in Myotonic Dystrophy Type 1, designed to be aligned with GDPR and
the upcoming European Health Data Space (EHDS), to use HL7 FHIR for clinical
interoperability, and to support research workflows via the OMOP Common Data
Model (CDM).

The focus is on:
- Strong separation of concerns between operational care, research, and identity.
- Privacy by design and secure processing for GDPR and EHDS.
- Standards-based data exchange (FHIR) and analytics (OMOP CDM).
- End-to-end traceability and auditable workflows.

---

### 1. Logical Component Overview

At a high level, the platform consists of the following logical layers:

1. Patient and site-facing applications
2. API and application services layer
3. Identity and access management (IAM)
4. Clinical data store (operational)
5. De-identification and data provisioning layer
6. Research environment and OMOP CDM
7. Observability, audit, and governance services

Each layer has clearly defined responsibilities and interfaces.

| Layer | Main responsibility | Recommended FOSS components | Local-first considerations |
|---|-------|-----------|----------|
| Patient and site-facing apps | Data capture and review by patients, caregivers, and site staff | Flutter or React Native for mobile; React + TypeScript for web | Mobile apps store data locally (SQLite or encrypted store) and sync over HTTPS when connectivity is available. |
| API and application services | Business logic, validation, and orchestration | FastAPI (Python) or NestJS (TypeScript) with PostgreSQL client libraries | Services can run on a single on-premise server or Kubernetes cluster; no dependency on proprietary cloud services. |
| Identity and access management | Authentication, authorization, and RBAC | Keycloak (OpenID Connect and OAuth 2.0) backed by PostgreSQL | Self-hosted IAM with local user store or institutional identity provider integration via open protocols. |
| Clinical data store | Operational clinical and study data | PostgreSQL, optionally with pgcrypto for field-level encryption | Runs on local or institutional infrastructure; backups and replicas kept under institutional control. |
| De-identification and provisioning | Transformation for research and secondary use | Apache Airflow or Prefect for pipelines; Python-based de-identification libraries | Pipelines execute in the institution’s environment; no raw data leaves without explicit governance approval. |
| Research environment and OMOP CDM | Pseudonymised analytics and cohort building | PostgreSQL OMOP instance; OHDSI WebAPI and Atlas | Researchers access via VPN or institutional network; data extracts can be generated on local analysis workstations. |
| Observability, audit, governance | Monitoring, logging, and policy enforcement | Prometheus, Grafana, Loki or OpenSearch, plus custom audit store | Metrics and logs remain within the institutional boundary; audit exports can be generated on demand for inspectors. |

---

### 2. Patient and Site-Facing Applications

#### 2.1 Patient Mobile App

- Native or cross-platform smartphone app for DM1 patients and caregivers.
- Capabilities:
	- User registration, login (via IAM), consent workflows.
	- ePROs, diaries, symptom and event reporting.
	- Notifications and reminders.
	- Limited self-service data views and summaries.
- Communication with backend:
	- All data sent via HTTPS to the API Gateway.
	- Data structures aligned to FHIR resources where feasible (e.g., Observation,
		QuestionnaireResponse, Condition, MedicationStatement, Encounter).

Recommended implementation is a Flutter or React Native application using an encrypted local store (for example, SQLite with application-level encryption) to support offline completion of forms, with background synchronisation to the backend when a secure connection is available.

#### 2.2 Site/Clinician Web Portal

- Browser-based application for clinical researchers and site staff.
- Capabilities:
	- View participant data (scoped by site).
	- Validate and annotate entries (e.g., serious adverse event flagging).
	- Manage and respond to data queries.
	- Monitor adherence and safety dashboards.
- Uses the same API layer and IAM as the mobile app, but with different roles and
	permissions (RBAC).

The portal can be implemented as a single-page application using React and TypeScript, built and served as static assets by an NGINX or Caddy instance colocated with the API services.

#### 2.3 Data Manager and Data Engineer Console

- Separate, access-controlled web interface for data managers and data engineers.
- Capabilities:
	- Configure forms, schedules, and edit checks.
	- Manage ETL jobs and exports.
	- View and triage system-level data quality issues.

This console can reuse the same React and TypeScript stack as the clinician portal, with separate routes and tighter RBAC policies enforced by Keycloak and the backend.

---

### 3. Identity and Access Management (IAM)

- Central IAM service implementing:
	- User authentication (patients, caregivers, clinicians, data managers,
		data engineers, auditors, administrators).
	- Role-based access control (RBAC) with scopes and attributes.
	- Support for multi-factor authentication where required.
- Technologies:
	- Keycloak as the primary IAM server, speaking OpenID Connect and OAuth 2.0 for token-based access to APIs.
	- Fine-grained claims and groups indicating role, site, study, and allowed operations.
- GDPR and EHDS alignment:
	- Support for subject access requests (who has access to what, when).
	- Explicit handling of consent scopes (research only, care and research, etc.),
		linked to authorization policies.

Keycloak is deployed as a self-hosted service backed by PostgreSQL, ensuring that identity data and audit logs remain under institutional control while still supporting federation with external identity providers where needed.

---

### 4. API Gateway and Application Services

#### 4.1 API Gateway

- Single entry point for all clients (mobile app, web portals, system-to-system
	integrations).
- Responsibilities:
	- TLS termination and network-level security controls.
	- Verification of access tokens and enforcement of scopes.
	- Rate limiting and basic request validation.

A practical FOSS choice for the gateway is Traefik or NGINX, configured to validate JSON Web Tokens (JWTs) issued by Keycloak and to route requests to the appropriate backend services.

#### 4.2 Application Services

Modular microservices or well-structured modular monolith, grouped by bounded
contexts:

- Patient Data Capture Service:
	- Receives and validates ePROs, observations, events.
	- Persists to the operational clinical data store.
	- Applies business rules and edit checks where appropriate.

- Study Configuration Service:
	- Manages questionnaires, schedules, edit checks, and versioning.
	- Exposes configuration to both patient and site applications.

- Query and Review Service:
	- Manages data queries between data managers, clinicians, and patients.
	- Tracks lifecycle of queries for audit purposes.

- Consent and Document Service:
	- Manages eConsent forms, versions, signatures, and withdrawal.
	- Interfaces with IAM to propagate consent-related access restrictions.

- Integration Service (FHIR facade):
	- Exposes a FHIR-based interface for interoperability with external systems
		(e.g., EHR, registries, other research platforms).
	- Maps internal data representations to FHIR resources and profiles.

All services write structured audit events to the observability and audit layer.

These services can be implemented as a small set of FastAPI (Python) or NestJS (TypeScript) applications, packaged into containers and orchestrated with Docker Compose or Kubernetes. PostgreSQL is used as the shared data store, and services communicate over internal HTTPS or mTLS-secured channels.

---

### 5. Clinical Data Store (Operational Layer)

This is the primary store for day-to-day operations and clinical study
management.

#### 5.1 Data Model

- Logical structure oriented around subjects, visits, forms, and events, but
	mapped as far as reasonable to FHIR resources:
	- Subject and enrollment: Patient, RelatedPerson, Group.
	- Data collection events and visits: Encounter.
	- Measurements and scores: Observation.
	- Questionnaires and answers: Questionnaire and QuestionnaireResponse.
	- Medications and changes: MedicationStatement, MedicationRequest.

#### 5.2 Identifiers and Pseudonymization

- Separation of direct identifiers into a dedicated Identity Store:
	- Identity Store: holds names, contact details, national identifiers.
	- Clinical Data Store: uses pseudonymous subject IDs and references only.
- The mapping between the two is access-controlled and audited.
- Supports the needs of EHDS by facilitating controlled re-use of health data
	under appropriate governance.

Both the Identity Store and Clinical Data Store can run on PostgreSQL, with strict network segmentation and role-based database access. On-premise deployment, combined with encrypted volumes and regular backups, supports a local-first operational model.

#### 5.3 Data Quality and Locking

- Edit checks and validation rules run on incoming data.
- Subject-, visit-, and study-level locking mechanisms for data freeze and
	database lock events.

---

### 6. De-identification and Data Provisioning Layer

This layer prepares data for research and secondary use while enforcing GDPR and
EHDS rules.

#### 6.1 De-identification and Anonymization

- Pipeline that transforms operational data into:
	- Pseudonymized research datasets (where a mapping exists but is tightly
		controlled).
	- Anonymized datasets for broader secondary use where allowed.
- Methods include:
	- Removal or masking of direct identifiers.
	- Generalization, aggregation, or noise addition for quasi-identifiers
		(depending on risk assessments).
	- Documentation of de-identification rules and parameters.

ETL and de-identification pipelines can be orchestrated with Apache Airflow or Prefect, using Python tasks that apply well-documented transformations and write into the OMOP warehouse.

#### 6.2 Governance Controls

- Data access approval workflows (e.g., via a Data Access Committee):
	- Requests specify purpose, scope, and duration of access.
	- Approved requests configure views or exports into the research
		environment.
- Full logging of what data was provisioned to whom, when, and for which
	purpose (supporting EHDS data access transparency requirements).

---

### 7. Research Environment and OMOP CDM

The research environment is logically separated from operational systems.

#### 7.1 OMOP CDM Warehouse

- Central research database implementing the OMOP Common Data Model.
- Receives data from the de-identification layer via ETL processes.
- Typical OMOP tables populated include:
	- PERSON (from pseudonymous subject information).
	- OBSERVATION, MEASUREMENT, CONDITION_OCCURRENCE, DRUG_EXPOSURE, VISIT_OCCURRENCE.
	- FACT_RELATIONSHIP to link custom constructs if needed.
- Vocabulary management:
	- Use standard OMOP vocabularies (SNOMED CT, RxNorm, LOINC, etc.) where
		applicable.
	- Map DM1-specific concepts and questionnaires to suitable concepts or
		custom vocabularies.

The OMOP warehouse is hosted on PostgreSQL, with the OHDSI WebAPI and Atlas stack deployed as FOSS components for cohort definition and study execution within the institutional boundary.

#### 7.2 ETL and Harmonization

- ETL jobs (or pipelines) perform:
	- Extraction from the operational clinical store.
	- Transformation and mapping to OMOP tables and concepts.
	- Loading into the OMOP warehouse.
- Versioning and audit:
	- ETL pipelines are version-controlled; each run is logged with parameters,
		code version, and data range.
	- Changes in vocabularies and mappings tracked over time.

#### 7.3 Analytics and Tools

- Researchers access the OMOP environment through controlled tools:
	- Cohort definition tools.
	- Statistical analysis environments (e.g., R, Python, SQL workbenches).
- Access is role-based and time-limited, mediated by the governance layer.

Analysis environments are provisioned as containerised R and Python workspaces (for example, RStudio Server and JupyterLab) running on institutional servers, connecting to the OMOP database over the internal network.

---

### 8. Observability, Audit, and Governance Services

#### 8.1 Audit Trail Service

- Central, append-only audit log capturing:
	- User authentication and authorization events.
	- Data creation, modification, and deletion events.
	- Configuration changes (forms, schedules, permissions, ETL configurations).
	- Data export and data access events.
- Supports auditor views and export for inspections.

#### 8.2 Monitoring and Logging

- Technical logs (system health, errors, performance) separated from audit
	logs but correlated via request IDs and timestamps.
- Alerts for anomalous behaviour (e.g., unusual access patterns, repeated
	failed logins).

Monitoring and logging can be implemented using Prometheus for metrics, Grafana for dashboards, and Loki or OpenSearch for log aggregation, all deployed as FOSS components alongside the application stack.

#### 8.3 Policy and Compliance Engine

- Encodes business and regulatory policies such as:
	- Consent constraints.
	- Data retention and deletion schedules.
	- Geographic and jurisdictional restrictions on data processing.
- Runs scheduled jobs to enforce retention (e.g., pseudonymized deletion after
	defined periods where permitted by regulations and study policy).

---

### 9. GDPR and EHDS Alignment Summary

- Lawful basis and consent:
	- Consent captured and versioned via the Consent and Document Service.
	- Linkage of consent status to access control and data provisioning.
- Data subject rights:
	- Facilities to export and, where appropriate, rectify personal data.
	- Logging to demonstrate how and when requests were fulfilled.
- Data minimization and purpose limitation:
	- Separate minimal operational set from research enrichment variables.
	- Clear documentation of which data flow into OMOP and for what purposes.
- EHDS-ready data sharing:
	- Standardized FHIR interfaces for clinical interoperability.
	- OMOP-based research data sets for secondary use under approved requests.
	- Transparent logging and governance for all secondary uses.

---

### 10. Next Steps for Detailing the Architecture

To move from this high-level architecture to an implementable design:

1. Define concrete FHIR profiles (DM1-specific where needed) and mapping rules
	 to OMOP concepts.
2. Specify the detailed RBAC matrix across applications, APIs, and data stores.
3. Design the audit trail schema and logging strategy in alignment with
	 regulatory expectations.
4. Select and validate technology stack components (IAM provider, database
	 technologies, ETL tools, monitoring stack).
5. Run a data protection impact assessment (DPIA) to validate GDPR and EHDS
	 compliance assumptions and refine controls.

