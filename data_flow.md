## End-to-End Data Flow for the DM1 Prospective Data Collection Platform

This document traces the complete lifecycle of data within the Myotonic Dystrophy Type 1 (DM1) prospective data collection platform, from initial capture on patient and clinician devices through operational processing, de-identification, and loading into the Observational Medical Outcomes Partnership Common Data Model (OMOP CDM) research warehouse. Each stage describes the data transformations applied, the systems involved, the governance controls enforced, and the standards that govern the exchange. The document is intended to serve as a reference for Clinical Data Management (CDM), data engineering, data protection, and regulatory review.

---

### 1. Data Origination

#### 1.1 Patient Mobile Application

Data enter the platform when a patient or caregiver completes an electronic patient-reported outcome (ePRO), a symptom diary entry, an event report, or a medication log on the mobile application. The application presents instruments defined by the DM1 Questionnaire profile, enforcing skip logic, required fields, and answer constraints at the point of entry.

Completed forms are structured as DM1 QuestionnaireResponse resources, each linked to the specific Questionnaire version and to the patient's pseudonymous identifier. Observations such as clinical measurements are represented as DM1 Observation resources coded with Logical Observation Identifiers Names and Codes (LOINC). Medication entries are structured as DM1 MedicationStatement resources coded with the Anatomical Therapeutic Chemical (ATC) classification.

Data are stored locally in an encrypted store (SQLite with application-level encryption) on the device. This local-first approach ensures that data capture is not interrupted by connectivity loss. The mobile application queues completed resources for synchronisation.

#### 1.2 Site and Clinician Web Portal

Clinical researchers and site staff enter data through the browser-based portal. Activities include validating and annotating patient-submitted entries, flagging serious adverse events, responding to data queries, and recording clinician-reported assessments. The portal produces the same Fast Healthcare Interoperability Resources (FHIR)-aligned data structures as the mobile application, ensuring a uniform data pipeline regardless of the originating interface.

#### 1.3 Data Manager and Data Engineer Console

Data managers configure instruments, schedules, and edit checks through a dedicated console. Data engineers manage extract-transform-load (ETL) jobs and exports. Configuration changes produce versioned artefacts tracked under the change management process. These artefacts influence data flow by determining which instruments are active, which validation rules apply, and how ETL pipelines transform operational data.

---

### 2. Synchronisation and Transport

#### 2.1 Device-to-Backend Synchronisation

When network connectivity is available, the mobile application initiates a background synchronisation over HTTPS (TLS 1.2 or higher). The synchronisation protocol transmits FHIR-aligned resource bundles to the Application Programming Interface (API) gateway. Each request carries a JSON Web Token (JWT) issued by Keycloak, containing the user's identity, role, site scope, and consent claims.

The synchronisation is idempotent: resources carry unique identifiers that allow the backend to detect and discard duplicate submissions, ensuring that intermittent connectivity does not produce duplicate records.

#### 2.2 Portal-to-Backend Communication

The clinician portal and data manager console communicate with the backend through the same API gateway and the same authentication mechanism. All requests are authenticated, authorised, and rate-limited identically regardless of the originating client.

#### Governance Checkpoint: Transport Security

- All data in transit are encrypted with TLS.
- Every request is authenticated via a JWT validated by the API gateway.
- Token claims enforce role-based access control (RBAC) scopes, ensuring that each client can only submit or retrieve data permitted by its role and site assignment.
- Requests that fail authentication or authorisation are rejected and logged as security events.

---

### 3. API Gateway

The API gateway is the single entry point for all client-to-backend communication. It performs the following operations in sequence for every inbound request.

| Step | Operation | Detail |
|------|-----------|--------|
| 1 | TLS termination | Decrypts the incoming HTTPS connection and forwards the request to internal services over mTLS-secured channels. |
| 2 | Token verification | Validates the JWT signature against Keycloak's public keys, checks token expiry, and extracts claims. |
| 3 | Scope enforcement | Compares the requested operation against the scopes encoded in the token. Rejects requests that exceed the user's permissions. |
| 4 | Rate limiting | Applies per-client and per-endpoint rate limits to protect backend services from abuse or misconfigured clients. |
| 5 | Request routing | Forwards the validated request to the appropriate application service based on the resource type and operation. |

The gateway is implemented using Traefik or NGINX, configured to interoperate with Keycloak for token validation.

#### Governance Checkpoint: Gateway Enforcement

- The gateway produces a structured audit event for every request, recording the actor identity, the operation, the target resource, and the outcome (permitted or denied).
- Failed authorisation attempts trigger alerts in the observability layer.

---

### 4. Application Services Layer

Validated requests reach the application services, which are organised by bounded context.

#### 4.1 Patient Data Capture Service

This service receives FHIR-aligned resource bundles from patients, caregivers, and clinicians. It performs the following processing steps.

**Structural validation.** The service validates each resource against the active DM1 FHIR profile (for example, DM1 QuestionnaireResponse, DM1 Observation, DM1 MedicationStatement). Resources that fail validation are rejected with a structured error response, and the rejection is logged.

**Edit checks.** Business rules configured by the data manager (range checks, cross-field consistency, mandatory field enforcement) are applied. Violations generate data queries that are routed back to the submitting user or to the site for resolution.

**Consent verification.** The service checks the submitter's consent status against the Consent and Document Service. Data submitted outside the scope of active consent are flagged and withheld from further processing until the consent situation is resolved.

**Persistence.** Validated resources are written to the operational PostgreSQL database (Clinical Data Store) using pseudonymous subject identifiers. Direct identifiers are never written to this store; they reside exclusively in the Identity Store.

**Audit event emission.** A structured audit event is generated for each successful write, recording the resource type, the pseudonymous subject identifier, the submitting user, the timestamp in Coordinated Universal Time (UTC), and the operation type.

#### 4.2 Query and Review Service

When edit checks or manual review identify data issues, this service creates and manages data queries. Each query records the affected resource, the nature of the discrepancy, the responsible party (patient, caregiver, or site clinician), and the resolution timeline. Query lifecycle events (creation, response, resolution, cancellation) are logged in the audit trail.

#### 4.3 Consent and Document Service

This service manages the eConsent lifecycle: presenting versioned consent forms, recording digital signatures, tracking granular consent options (core data collection, optional data elements, secondary research use, external sharing), and propagating consent status to the Identity and Access Management (IAM) layer so that consent directly influences authorisation decisions across the platform. Withdrawal events trigger downstream flags that prevent further data collection for the affected participant and ensure that ETL and OMOP loading processes respect the withdrawal.

#### 4.4 Study Configuration Service

Manages questionnaires, visit schedules, edit check rules, and their versioning. Changes to study configuration are subject to the change management process and produce audit trail entries. Active configurations are served to both patient and site applications to ensure uniform data capture.

#### 4.5 Integration Service (FHIR Facade)

Exposes a FHIR-compliant interface for interoperability with external systems, including electronic health records (EHRs), disease registries, and national health data infrastructures. Inbound data from external sources are mapped to the platform's FHIR profiles and validated before entering the operational store. Outbound data are mapped from internal representations to standard FHIR resources and profiles, with mappings version-controlled and documented.

#### Governance Checkpoint: Application Layer

- All data writes are validated against active FHIR profiles and edit checks before persistence.
- Consent status is verified at every data ingestion event.
- Every service emits structured audit events to the append-only audit log.
- Data queries establish a traceable resolution workflow for every identified discrepancy.

---

### 5. Clinical Data Store (Operational Layer)

The operational PostgreSQL database holds all day-to-day clinical and study management data.

#### 5.1 Data Model

The logical structure is oriented around subjects, visits, forms, and events, mapped to FHIR resources.

| FHIR Resource | Operational Role | Key Identifiers |
|---------------|-----------------|-----------------|
| Patient | Enrolled participant record | Pseudonymous study identifier |
| RelatedPerson | Caregiver or proxy | Pseudonymous identifier linked to Patient |
| Encounter | Visit or diary period | Encounter identifier, visit type, protocol visit number |
| Questionnaire | Active instrument definition | Canonical URL and version |
| QuestionnaireResponse | Completed instrument submission | Response identifier, linked Questionnaire version, Encounter, Patient |
| Observation | Clinical measurement or derived score | LOINC code, value, linked Encounter and Patient |
| Condition | Diagnosis, comorbidity, complication | Systematized Nomenclature of Medicine Clinical Terms (SNOMED CT) code, linked Patient |
| MedicationStatement | Patient-reported medication use | ATC code, linked Patient |
| MedicationRequest | Clinician-prescribed medication | ATC code, linked Patient and Encounter |
| AdverseEvent | Adverse event record | Event identifier, seriousness classification, linked Patient |
| Consent | Informed consent record | Consent status, scope categories, linked Patient |
| AuditEvent | Audit trail entry | Actor, action, object, timestamp |

#### 5.2 Identifier Separation

Direct identifiers (names, contact details, national identifiers) are stored in a physically separate Identity Store, also on PostgreSQL but with strict network segmentation and restricted access. The Clinical Data Store references participants only through pseudonymous identifiers. The mapping between the two stores is access-controlled, logged, and available only to roles with explicit authorisation.

#### 5.3 Data Quality and Locking

Edit checks and validation rules run on all incoming data. The platform supports subject-level, visit-level, and study-level locking mechanisms. When a lock is applied, the affected data become read-only, and any modification attempt is rejected and logged. Locking events serve as governance milestones that mark data freeze and database lock for regulatory purposes.

#### Governance Checkpoint: Operational Store

- No direct identifiers are present in the Clinical Data Store.
- The Identity Store is network-segmented with access restricted to authorised roles only.
- All data modifications are recorded in the append-only audit trail with before and after values.
- Data locking prevents unauthorised modifications after freeze events.

---

### 6. De-identification and Data Provisioning Layer

This layer transforms operational data into research-ready datasets while enforcing General Data Protection Regulation (GDPR) and European Health Data Space (EHDS) requirements.

#### 6.1 Pipeline Architecture

ETL and de-identification pipelines are orchestrated by Apache Airflow or Prefect, executing Python tasks within the institution's infrastructure. Each pipeline run is version-controlled and logged with the following metadata.

| Metadata Element | Description |
|-----------------|-------------|
| Pipeline version | Git commit hash of the pipeline code executed |
| Vocabulary version | Athena release date of the OMOP vocabularies applied |
| Source data range | Start and end timestamps of the operational data window extracted |
| De-identification parameters | Specific masking, generalisation, and noise rules applied |
| Execution timestamp | UTC timestamp of the pipeline run |
| Operator identity | Pseudonymous identifier of the data engineer who initiated or approved the run |

#### 6.2 De-identification Methods

The pipeline applies a sequence of transformations depending on the target dataset type.

**Pseudonymised datasets** (where a controlled mapping to the original subject exists) undergo removal of direct identifiers (already absent from the Clinical Data Store but verified), generalisation of quasi-identifiers (for example, reducing date of birth precision, aggregating geographic data), and retention of the pseudonymous subject identifier for longitudinal linkage within the OMOP warehouse.

**Anonymised datasets** (for broader secondary use where no re-identification should be possible) undergo additional suppression, noise addition, and aggregation techniques calibrated to the re-identification risk assessment documented in the Data Protection Impact Assessment (DPIA).

#### 6.3 Consent and Withdrawal Enforcement

Before extracting any participant's data, the pipeline checks the current consent status. Participants who have withdrawn consent are excluded from the extraction. Participants whose consent scope does not cover secondary research use are excluded from research datasets. These checks are encoded in the pipeline logic and verified in automated tests.

#### Governance Checkpoint: De-identification Layer

- Every pipeline run is version-controlled with full provenance metadata.
- De-identification parameters are documented and auditable.
- Consent status is verified before data extraction.
- No data leave the institutional boundary without explicit governance approval.
- Pipeline execution logs are written to the audit trail.

---

### 7. FHIR-to-OMOP Mapping and Loading

#### 7.1 Source-to-FHIR Mapping Verification

Before data enter the OMOP pipeline, the source-to-FHIR mapping is verified. Each data element in the study data specification has a documented mapping to a FHIR resource, element, value type, and terminology binding. Sample FHIR bundles generated from synthetic data are validated against the active DM1 FHIR profiles to confirm structural and semantic correctness.

#### 7.2 FHIR-to-OMOP Transformation

The ETL pipeline implements a second mapping layer that transforms FHIR resources into OMOP CDM tables. The mapping is designed and documented using Observational Health Data Sciences and Informatics (OHDSI) tools.

| FHIR Resource | Target OMOP Table | Mapping Logic |
|---------------|-------------------|---------------|
| Patient | PERSON | Pseudonymous identifier, year of birth, gender concept mapped from AdministrativeGender. |
| Encounter | VISIT_OCCURRENCE | Visit type concept from project value set, period start and end, care site from serviceProvider. |
| Condition | CONDITION_OCCURRENCE | SNOMED CT code resolved to OMOP standard concept via vocabulary tables. |
| MedicationStatement, MedicationRequest | DRUG_EXPOSURE | ATC code mapped to RxNorm standard concept. Start and end dates from effective period. |
| Observation (measurements) | MEASUREMENT | LOINC code resolved to OMOP standard concept. Value and unit mapped. |
| Observation (ePROs, scores) | OBSERVATION (OMOP) | LOINC or project code resolved to OMOP concept. QuestionnaireResponse items decomposed to individual records. |
| QuestionnaireResponse | OBSERVATION (OMOP) | Individual items extracted, each coded and linked to originating instrument and visit. |
| AdverseEvent | CONDITION_OCCURRENCE or OBSERVATION (OMOP) | Classification determines target domain. |
| (Free text annotations) | NOTE | Preserved where clinically significant, with natural language processing as a future enhancement. |
| (Cross-resource links) | FACT_RELATIONSHIP | Explicit relationships such as adverse event to resolution, or questionnaire response to visit. |

#### 7.3 Vocabulary Resolution

Each source code carried in a FHIR resource is resolved to an OMOP standard concept identifier through the vocabulary tables. The resolution follows a defined precedence.

1. If a direct mapping from the source code to a standard OMOP concept exists, the standard concept is applied.
2. If the source code maps to a non-standard OMOP concept, the pipeline follows concept relationships to identify the appropriate standard concept.
3. If no mapping exists, the value is loaded with a concept identifier of zero and flagged for review by the CDM team.

Concept mapping for terms without direct vocabulary matches is supported by Usagi, the OHDSI semi-automated mapping tool. A domain expert reviews, accepts, or rejects suggested mappings, and approved mappings are loaded into the source-to-concept tables for consistent ETL application.

#### 7.4 Custom Concept Handling

DM1-specific data elements that lack standard vocabulary coverage (for example, the Myotonic Dystrophy Health Index, disease-specific functional scales) are assigned local custom concepts drawn from a reserved identifier range. Custom concepts are stored in the OMOP vocabulary tables as source concepts, distinguished from standard concepts by their vocabulary identifier, and tracked in a project concept registry. At each vocabulary update, custom concepts are reviewed for potential replacement by newly published standard concepts.

#### Governance Checkpoint: Mapping and Loading

- Mapping specifications are version-controlled and jointly reviewed by CDM and data engineering.
- WhiteRabbit profiling and Rabbit in a Hat mapping documents provide auditable design artefacts.
- Unmapped values (concept identifier zero) are flagged for systematic review.
- Custom concepts are governed through a documented lifecycle with convergence toward standard vocabularies.

---

### 8. OMOP CDM Research Warehouse

#### 8.1 Warehouse Structure

The OMOP CDM warehouse is a separate PostgreSQL instance, logically and physically isolated from the operational Clinical Data Store. It contains the standard OMOP tables (PERSON, VISIT_OCCURRENCE, CONDITION_OCCURRENCE, DRUG_EXPOSURE, MEASUREMENT, OBSERVATION, NOTE, FACT_RELATIONSHIP) populated by the ETL pipeline, along with the vocabulary tables managed through Athena downloads.

#### 8.2 Researcher Access

Researchers access the OMOP warehouse through controlled, role-based mechanisms.

| Access Channel | Tool | Purpose |
|----------------|------|---------|
| Cohort definition | OHDSI Atlas and WebAPI | Define study cohorts using standard OMOP concepts, validate data coverage, and generate cohort tables. |
| Statistical analysis | RStudio Server, JupyterLab | Execute R and Python analyses against the OMOP database within containerised workspaces on institutional servers. |
| Ad hoc queries | SQL workbenches | Run structured queries against OMOP tables for data exploration and quality assessment. |

Access is mediated by the IAM layer: researchers submit a data access request specifying purpose, scope, duration, and analytical environment. The Data Access Committee reviews and approves requests against the DPIA, consent scope, and institutional policy. Approved access is time-limited and logged.

#### 8.3 Data Extracts and External Sharing

Where approved, de-identified or anonymised data extracts may be generated from the OMOP warehouse for external researchers, disease registries, or EHDS health data access bodies. Each extract is logged with the recipient identity, purpose, scope, approval reference, and date. Data shared across borders are subject to additional safeguards: verification of adequate data protection at the recipient, data sharing agreements, limitation to the minimum data necessary, and full transparency logging.

#### Governance Checkpoint: Research Warehouse

- The OMOP warehouse is isolated from the operational environment.
- All researcher access is approved, time-limited, and logged.
- Data extracts for external use are governed by the data access request procedure.
- Cross-border sharing follows EHDS-compatible transparency and safeguard requirements.

---

### 9. FHIR Interoperability Flow

#### 9.1 Inbound Data

External systems (EHRs, registries, national health data infrastructures) may push data to the platform through the Integration Service's FHIR facade. Inbound resources are mapped to the platform's DM1 FHIR profiles, validated, and processed through the same application services pipeline as internally captured data. Authentication and authorisation follow the same IAM model, with external systems assigned dedicated service accounts with scoped permissions.

#### 9.2 Outbound Data

The platform can expose selected data through the FHIR facade for consumption by external systems. Outbound resources are mapped from internal representations to standard FHIR resources and profiles, with terminology bindings preserved. Access is scoped and logged identically to internal API access.

#### 9.3 Registry and EHDS Integration

Alignment with European rare disease registries (including the European Reference Network for Rare Neuromuscular Diseases, EURO-NMD) and EHDS mechanisms is supported through the coding strategy. The platform's data carry Orphanet identifiers (ORPHA:273 for DM1), SNOMED CT, LOINC, ATC, and International Classification of Diseases (ICD) codes that facilitate mapping to registry-required fields and national minimum data sets.

#### Governance Checkpoint: Interoperability

- FHIR interface access is authenticated, scoped, and logged through the same IAM infrastructure.
- Mappings between internal and external representations are version-controlled and tested.
- External sharing follows the data access request procedure and is fully logged.

---

### 10. Observability, Audit, and Compliance

#### 10.1 Audit Trail

Every stage of the data flow generates structured audit events written to append-only PostgreSQL tables. Audit entries record the actor identity, role at the time of action, the action performed, the object affected (with before and after values where applicable), the UTC timestamp, the originating device or IP address, and, for data corrections, a mandatory reason field. No role in the platform has permission to alter or delete audit records through the application layer.

#### 10.2 Monitoring

Technical monitoring (system health, performance, error rates) is implemented using Prometheus for metrics and Grafana for dashboards. Log aggregation uses Loki or OpenSearch. Technical logs are correlated with audit events through request identifiers and timestamps but are stored separately and have distinct retention schedules.

#### 10.3 Alerting

Anomalous patterns, such as unusual access frequency, repeated authentication failures, or attempts to access resources outside the user's scope, trigger automated alerts routed to the system administration and security teams. Alerts are logged and, where they indicate a potential data governance incident, escalated through the incident response process.

#### 10.4 Compliance Enforcement

A policy engine encodes consent constraints, retention schedules, geographic processing restrictions, and deletion rules. Scheduled jobs enforce retention (deleting or archiving data whose retention period has expired), flag data affected by consent withdrawal, and verify that processing activities remain within the boundaries defined by the DPIA and applicable law.

---

### 11. End-to-End Data Flow Summary

The following table summarises the complete path of a single data element from capture to research use, identifying the system, transformation, and governance control at each stage.

| Stage | System | Data Form | Transformation | Governance Control |
|-------|--------|-----------|----------------|-------------------|
| 1. Capture | Mobile app or web portal | FHIR-aligned resource (local) | Instrument logic, skip rules, client-side validation | Encrypted local storage, user authentication |
| 2. Transport | HTTPS to API gateway | FHIR bundle over TLS | None (encrypted transit) | JWT authentication, scope enforcement |
| 3. Gateway | Traefik or NGINX | Validated request | Token verification, rate limiting, routing | Audit event for every request |
| 4. Validation | Patient Data Capture Service | FHIR resource | Profile validation, edit checks, consent verification | Rejection and logging of invalid data |
| 5. Persistence | Clinical Data Store (PostgreSQL) | Pseudonymised FHIR-aligned record | Write to operational tables | Append-only audit trail, data locking |
| 6. Identity separation | Identity Store (PostgreSQL) | Direct identifiers only | Network-segmented storage | Restricted access, audit logging |
| 7. De-identification | Airflow or Prefect pipeline | Pseudonymised or anonymised extract | Masking, generalisation, noise addition | Consent check, version-controlled pipeline, full provenance |
| 8. Vocabulary mapping | ETL pipeline | OMOP-coded record | Source code to OMOP standard concept resolution | Mapping review, unmapped value flagging |
| 9. OMOP loading | OMOP CDM warehouse (PostgreSQL) | OMOP CDM tables | Insert into PERSON, VISIT_OCCURRENCE, CONDITION_OCCURRENCE, DRUG_EXPOSURE, MEASUREMENT, OBSERVATION, NOTE, FACT_RELATIONSHIP | Isolated database, access request approval |
| 10. Research use | Atlas, RStudio, JupyterLab | Cohorts, analyses, extracts | Cohort definition, statistical analysis | Time-limited access, purpose-bound, logged |
| 11. External sharing | FHIR facade or data extract | FHIR resources or flat files | Mapping to external profiles or formats | Data sharing agreement, minimum necessary, transparency log |

---

### 12. Data Subject Rights Flows

#### 12.1 Subject Access Request

A data subject exercises the right of access under GDPR Article 15. The request is received and the subject's identity is verified. Relevant data are extracted from the operational Clinical Data Store (excluding system audit records that do not constitute personal data of the requester). The response is provided within the legally mandated timeframe. The handling of the request is logged in the audit trail.

#### 12.2 Rectification

A data subject requests correction of inaccurate data. The correction is applied through the platform's data correction workflow, with the audit trail recording the original value, the corrected value, and the reason for the change. If the corrected data have already been loaded into the OMOP warehouse, the ETL pipeline is re-executed for the affected records.

#### 12.3 Withdrawal and Erasure

A participant withdraws consent through the mobile application or through the study site. The withdrawal event is recorded in the Consent and Document Service, propagated to the IAM layer, and flagged in the operational store. No further data are collected. Existing data may be retained where legally required (for example, safety reporting). The ETL pipeline excludes the participant from future OMOP loads. Existing records in the OMOP warehouse are handled according to the retention policy and the data access agreements under which they were provisioned. The participant is informed of the practical effects of withdrawal.

---

### Document Control

This document is version-controlled alongside the project's technical and governance artefacts. It reflects the data flow design at the outset of the three-month project period and will be refined as architecture implementation progresses and the DPIA is completed.

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 0.1 | 2026-03-01 | Clinical Data Management | Initial draft tracing end-to-end data flow, governance checkpoints, and OMOP mapping pipeline |
