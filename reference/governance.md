## Initial Governance Documentation for the DM1 Prospective Data Collection Platform

This document establishes the governance framework for the prospective data collection platform targeting Myotonic Dystrophy Type 1 (DM1). It is intended as a living artefact, drafted early in the project lifecycle and refined as the technical architecture, regulatory landscape, and operational processes mature. It consolidates the data management plan outline, the structure for a Data Protection Impact Assessment (DPIA), consent requirements, data flow governance, audit trail policy, retention rules, and procedures for data access requests and subject rights. Throughout, the framework assumes alignment with the General Data Protection Regulation (GDPR), the emerging European Health Data Space (EHDS), and the platform's standards-based architecture using Fast Healthcare Interoperability Resources (FHIR) and the Observational Medical Outcomes Partnership Common Data Model (OMOP CDM).

### Scope and Applicability

This governance framework applies to all personal data and health data processed within the DM1 platform, from the point of capture on a patient's mobile device or a clinician's web portal through to de-identified research datasets stored in the OMOP CDM warehouse. It covers data at rest, data in transit, derived data, audit records, and metadata. It applies equally to all roles defined in the platform's role-based access control (RBAC) model: patients, caregivers, clinical researchers, data managers, data engineers, auditors, and system administrators.

The framework is binding on all individuals and organisations participating in the operation of the platform, including hosting institutions, participating clinical sites, and any third parties who receive data extracts under approved access agreements.

### Regulatory and Standards Context

#### General Data Protection Regulation

The GDPR provides the primary legal framework for processing personal data within the European Economic Area. For this platform, the most relevant provisions concern lawful basis for processing, data minimisation, purpose limitation, data subject rights, pseudonymisation, data protection by design and by default, the obligation to conduct a DPIA for high-risk processing, and the requirements for international data transfers. The platform is designed so that these obligations can be met through a combination of architectural controls, procedural safeguards, and documented policies.

#### European Health Data Space

The EHDS regulation, once fully enacted, will introduce specific rules for the primary and secondary use of electronic health data across the European Union. The platform anticipates these requirements by adopting interoperability standards (FHIR for clinical exchange, OMOP CDM for research), by maintaining clear separation between operational and research data environments, and by implementing transparent logging of all secondary data uses. Governance processes described here are intended to be compatible with EHDS obligations regarding data access bodies, conditions for secondary use, and data quality labelling.

#### Clinical Research Standards

Where the data collected through the platform are intended to support regulatory submissions or to meet Good Clinical Practice (GCP) expectations, the governance framework also considers the principles of ICH E6(R2), the requirements for electronic records and electronic signatures (drawing on 21 CFR Part 11 concepts where relevant), and the general expectation that clinical data systems must be validated, auditable, and secure.

### Data Management Plan Outline

The data management plan is the operational companion to this governance document. It describes what data are collected, how they are handled, and who is responsible at each stage. The following sections will be elaborated as the study protocol and technical implementation stabilise.

#### Study Objectives and Data Requirements

The data management plan begins with a clear statement of the study's objectives and the data needed to meet them. For this platform, the primary purpose is prospective collection of patient-reported outcomes (PROs), symptom diaries, adverse events, concomitant medications, clinician assessments, and visit-related data from individuals with DM1 and their caregivers. Each data element is documented in the study data specification, including its definition, permissible values, units, derivation rules, and handling of missing data.

#### Instruments and Schedules

Electronic instruments, including electronic patient-reported outcomes (ePROs), clinician-reported forms, and visit schedules, are version-controlled and configured centrally through the study configuration service. The data management plan specifies visit windows, diary frequencies, conditional logic, language variants, and the mapping between form fields and FHIR resources. Changes to instruments follow the change management process described later in this document.

#### Coding and Terminology Strategy

The platform uses standard terminologies wherever feasible. Systematized Nomenclature of Medicine Clinical Terms (SNOMED CT) and Logical Observation Identifiers Names and Codes (LOINC) are the primary coding systems for clinical observations and laboratory-style measurements. OMOP standard vocabularies are used in the research warehouse. The data management plan documents which source variables map to which standard concepts, where local or custom concepts are necessary, and how vocabulary updates are handled over time.

#### Data Quality and Edit Checks

Data quality is enforced through a combination of automated edit checks (range checks, cross-field consistency rules, protocol-driven constraints) and manual review workflows (queries raised by data managers or clinical reviewers). The data management plan describes the full set of edit checks, their severity (soft warning versus hard block), and the process for adding, modifying, or disabling checks during the study.

#### Data Locking and Freezing

Subject-level, visit-level, and study-level locking mechanisms prevent further modification of data after defined milestones. The data management plan specifies the criteria and approval process for each lock level, the roles authorised to perform lock and unlock operations, and the audit trail entries generated by these actions.

### Data Protection Impact Assessment Structure

A DPIA is required under Article 35 of the GDPR because the platform involves systematic processing of health data on a large scale, the use of new technologies for data collection and research, and the potential for cross-border data sharing under EHDS. The DPIA will follow a structured approach, and the sections below outline the assessment framework.

#### Description of Processing

This section of the DPIA describes the nature, scope, context, and purposes of the processing. It covers the types of personal data collected (health data, identifiers, device metadata, behavioural data from app usage), the categories of data subjects (DM1 patients, caregivers, clinical researchers, site staff), the data flows from mobile devices through the operational store to the OMOP research warehouse, and the technologies involved (mobile applications, PostgreSQL databases, Keycloak for Identity and Access Management (IAM), FHIR facade, extract-transform-load (ETL) pipelines, and observability tooling).

#### Necessity and Proportionality

The DPIA assesses whether the processing is necessary and proportionate to the stated purposes. For each data element, the assessment confirms that collection is justified by the study protocol or by a legitimate operational need (such as authentication or audit). Optional data elements are clearly separated and require explicit consent. The assessment also confirms that less intrusive alternatives were considered and, where feasible, adopted.

#### Risk Identification and Assessment

Risks are identified across several dimensions: risks to data subjects (unauthorised disclosure of health data, re-identification from pseudonymised datasets, denial of rights), risks to data integrity (unauthorised modification, loss of audit trail, corruption during ETL), and risks to availability (system outages affecting patient care pathways, loss of research data). Each risk is assessed for likelihood and severity, taking into account both the sensitivity of DM1 health data and the vulnerability of the patient population.

#### Measures to Address Risks

For each identified risk, the DPIA documents the technical and organisational measures in place or planned. These include pseudonymisation and separation of identifiers, encryption at rest and in transit, RBAC enforcement through Keycloak and application-level checks, append-only audit logging, automated de-identification pipelines with documented parameters, data access approval workflows, retention enforcement, and incident response procedures. Where residual risk remains above an acceptable threshold, the DPIA identifies additional controls or records the decision to accept the risk with justification.

#### Consultation

The DPIA includes records of consultation with the Data Protection Officer (DPO), with data subjects or their representatives where appropriate, and with any supervisory authority if required under GDPR Article 36. The consultation log documents who was consulted, when, what input they provided, and how it was addressed.

### Consent Framework

#### Lawful Basis for Processing

The primary lawful basis for processing personal data in this platform is explicit consent of the data subject (GDPR Article 6(1)(a) and Article 9(2)(a) for special category health data), given through an electronic consent (eConsent) workflow embedded in the mobile application and clinician portal. Where processing is necessary for reasons of public interest in the area of public health or for scientific research purposes, additional or alternative legal bases under Articles 9(2)(i) and 9(2)(j) may be invoked, subject to appropriate safeguards and as documented in the DPIA.

#### eConsent Workflow

Consent is captured electronically within the platform. The eConsent workflow presents the participant with a versioned information sheet and consent form, confirms understanding through acknowledgement steps, records a timestamped digital signature, and stores the consent record in the application database. The Consent and Document Service manages form versions, tracks which version each participant signed, and propagates consent status to the IAM layer so that consent directly influences what data a user or service may access.

#### Granularity of Consent

Consent is structured to allow participants to agree separately to core study data collection, optional data elements (such as lifestyle or wearable data), secondary use of data for research beyond the primary study objectives, and sharing of de-identified data with external researchers or through EHDS mechanisms. Each consent option is stored independently and can be modified or withdrawn at any time.

#### Withdrawal of Consent

Participants may withdraw consent at any time through the mobile application or by contacting their study site. The governance framework defines the consequences of withdrawal clearly and in advance: no further data collection occurs for that participant, existing data may be retained where legally required (for example, for safety reporting or regulatory obligations), and the participant's records are flagged in the system so that downstream processes (ETL, OMOP loading, research extracts) respect the withdrawal. The withdrawal event is recorded in the audit trail, and the participant is informed of the practical effects.

### Data Flow Governance

#### Operational Data Flow

Data originate on patient mobile devices and clinician web portals. All communication with the backend occurs over HTTPS through the API gateway, which terminates TLS, verifies access tokens issued by Keycloak, and enforces scopes. The Patient Data Capture Service validates incoming data against configured edit checks and persists them to the operational PostgreSQL database, which uses pseudonymous subject identifiers. Direct identifiers are stored in a separate Identity Store with restricted access. Every write operation generates a structured audit event.

#### De-identification and Research Data Flow

Data move from the operational store to the research environment through a controlled de-identification and provisioning layer. Orchestrated pipelines (managed by tools such as Apache Airflow or Prefect) apply pseudonymisation, masking, generalisation, or noise addition according to documented parameters. The output is loaded into the OMOP CDM warehouse, a separate PostgreSQL instance. Each pipeline run is version-controlled and logged, including the exact logic, vocabulary versions, and source data ranges used. Data access to the OMOP environment is governed by the data access request procedure described below.

#### FHIR Interoperability Flow

The Integration Service exposes a FHIR facade for interoperability with external systems such as electronic health records (EHRs), disease registries, and national health data infrastructures. Data exchanged through this interface are mapped between internal representations and FHIR resources and profiles. The mappings are version-controlled, tested, and documented in the data management plan. Access to the FHIR interface is authenticated and scoped through the same IAM infrastructure as all other platform services.

#### Cross-Border and External Sharing

Where data are shared across borders or with external parties, additional safeguards apply. These include verification that the recipient operates under an adequate level of data protection (or that appropriate contractual clauses are in place), limitation of shared data to the minimum necessary for the stated purpose, and full logging of what data were shared, with whom, when, and under which approval. These controls are designed to be compatible with EHDS requirements for transparent secondary use.

### Audit Trail Policy

#### Scope

The audit trail captures every action that creates, modifies, or deletes data or configuration within the platform. It also captures authentication events, authorisation decisions, data exports, consent events, and administrative actions such as role assignments and system configuration changes.

#### Content

Each audit trail entry records the identity of the actor (user identifier and role at the time of the action), the action performed, the object affected (with before and after values where applicable), the timestamp in Coordinated Universal Time (UTC), the originating device or IP address, and, where required by policy, the reason for the action. For data corrections, a mandatory reason field ensures that the rationale is preserved alongside the change.

#### Storage and Immutability

Audit records are stored in append-only tables in PostgreSQL, designed to prevent modification or deletion of entries. Access to the raw audit tables is restricted to the auditor role and, in read-only mode, to the system administrator role. No role in the platform has permission to alter or delete audit records through the application layer. Backup and archival procedures for audit data are aligned with the retention policy.

#### Access and Export

Authorised auditors can view, filter, and export audit trail segments through a dedicated interface. Export formats support regulatory inspection needs. The audit trail is also available for internal quality reviews, incident investigations, and compliance monitoring.

### Retention and Archiving Policy

#### Retention Periods

Retention periods are defined for each category of data processed by the platform. Clinical study data (including patient-reported outcomes, clinician annotations, and derived variables) are retained for a minimum period determined by the study protocol, applicable regulations, and institutional policy, typically at least fifteen years after study completion for data supporting regulatory submissions. Audit trail records are retained for the same period as the data they document, or longer if required by law. Technical logs (system health, performance metrics) are retained for a shorter operational period, typically one to two years, unless they are relevant to an ongoing investigation.

#### Archival

At the end of active use, data are archived in a format suitable for long-term preservation and potential reuse. Where applicable, archived datasets follow recognised standards. Archive integrity is verified through checksums and periodic validation. Access to archived data follows the same governance rules as access to active data.

#### Deletion

When retention periods expire, data are deleted in accordance with a documented deletion procedure. Deletion is logged in the audit trail. Pseudonymised research datasets in the OMOP warehouse follow their own retention schedule, which may differ from the operational data schedule and is documented in the data access agreements under which they were provisioned.

### Data Access Request Procedure

#### Internal Research Access

Researchers within the participating institutions may request access to de-identified datasets in the OMOP CDM warehouse. Requests are submitted through a defined process that specifies the purpose of access, the scope of data needed (which subjects, which variables, which time period), the intended duration of access, and the analytical environment where the data will be used. Requests are reviewed and approved by a Data Access Committee or equivalent governance body, taking into account the DPIA, consent scope, and institutional policies.

#### External Research Access

External researchers or organisations may request access under similar conditions, with additional requirements for data sharing agreements, assessment of the recipient's data protection practices, and, where applicable, approval by a supervisory authority or EHDS health data access body. External access is always to de-identified or anonymised datasets, never to identifiable operational data.

#### Subject Access Requests

Under GDPR Article 15, data subjects have the right to obtain confirmation of whether their personal data are being processed, access to a copy of those data, and information about the purposes, categories, recipients, retention periods, and safeguards applicable to their data. The platform supports subject access requests through a documented procedure: the request is received and verified (identity confirmation), the relevant data are extracted from the operational store (excluding audit records that do not constitute personal data of the requester), and the response is provided within the legally required timeframe. The handling of each request is logged in the audit trail.

#### Rectification and Erasure

Data subjects may also request rectification of inaccurate data or, in certain circumstances, erasure of their data. Rectification is handled through the platform's data correction workflow, with audit trail entries documenting the original value, the corrected value, and the reason. Erasure requests are assessed against legal obligations that may require continued retention (for example, safety reporting requirements), and the outcome is communicated to the data subject with a clear explanation.

### Role-Based Access Control Governance

#### Permission Matrix

The platform enforces a detailed RBAC model implemented through Keycloak for authentication and coarse-grained role assignment, and through application-level checks for fine-grained permission enforcement. The full permission matrix, covering eleven permission categories and thirty-seven individual permissions across seven roles, is maintained as a versioned configuration artefact and visualised in the accompanying RBAC matrix document. Any change to the permission matrix follows the change management process and is reflected in the audit trail.

#### Principle of Least Privilege

All users are assigned the minimum set of permissions necessary for their function. Elevated permissions, such as temporary auditor access or data lock and unlock rights, require documented approval, have a defined expiry, and generate audit trail entries when granted and when revoked.

#### Site Scoping

Clinical researchers are scoped to the participants enrolled at their site or under their direct care. Data managers have study-wide access to pseudonymised data but are restricted from direct identifiers unless separation of duties permits otherwise. Data engineers operate on pseudonymised data and have no permission to edit clinical values in production. These scoping rules are enforced at the API level and verified during validation testing.

#### Periodic Review

Role assignments and permission configurations are reviewed at defined intervals, at minimum quarterly and after any significant change to the study protocol, team composition, or regulatory requirements. Reviews are documented and any resulting changes follow the standard change management process.

### Change Management

#### Scope of Controlled Changes

Changes to study configuration (instruments, schedules, edit checks), to the RBAC model, to consent forms, to ETL and de-identification pipeline logic, to FHIR mappings, and to governance documents themselves are subject to a formal change management process.

#### Process

A change request is initiated by the responsible party (typically Clinical Data Management (CDM) for study configuration and governance, data engineering for ETL and pipeline changes, or the system administrator for infrastructure changes). The request documents the proposed change, its rationale, impact assessment, and testing plan. It is reviewed and approved by the appropriate authority (CDM lead, DPO, study sponsor, or a combination depending on the nature of the change). Approved changes are implemented in a test environment, validated, and promoted to production. The change, its approval, and its deployment are recorded in the audit trail and in a change log maintained alongside the governance documentation.

#### Emergency Changes

In exceptional circumstances, changes may be implemented on an expedited basis to address safety concerns, critical system failures, or regulatory directives. Emergency changes still require documentation and retrospective approval, and they are clearly flagged in the change log and audit trail.

### Incident Response

#### Definition

A data governance incident includes any unauthorised access to personal data, any breach of the confidentiality, integrity, or availability of the platform, any failure of RBAC enforcement, any loss or corruption of audit trail records, and any situation where data processing occurs outside the boundaries defined by consent, the DPIA, or applicable law.

#### Response Process

When an incident is detected or reported, the response follows a defined sequence: containment (limiting further exposure or damage), assessment (determining the scope, severity, and affected data subjects), notification (informing the DPO, and where required the supervisory authority and affected data subjects, within the timeframes mandated by GDPR Articles 33 and 34), remediation (addressing the root cause and restoring normal operations), and review (documenting lessons learned and updating controls to prevent recurrence).

#### Logging and Accountability

All incident response actions are documented and stored alongside the audit trail. Post-incident reviews are shared with relevant governance stakeholders and, where appropriate, inform updates to the DPIA, the data management plan, or this governance document itself.

### Governance Review Schedule

This governance framework is reviewed at defined intervals to ensure it remains aligned with the evolving regulatory landscape, the technical state of the platform, and the operational realities of the study. The initial review schedule is as follows.

Monthly reviews during the first three months of the project, coinciding with milestone-based assessments described in the project plan, focus on refining the DPIA, consent language, and retention rules as the technical implementation stabilises.

Quarterly reviews thereafter assess the continued adequacy of RBAC configurations, audit trail completeness, data access procedures, and incident response readiness.

Annual reviews, or reviews triggered by significant regulatory changes (such as the formal enactment of EHDS implementing acts or revisions to national data protection guidance), address the governance framework as a whole and its alignment with the broader legal and institutional context.

Each review is documented, and any resulting changes follow the change management process described above.

### Document Control

This document is version-controlled alongside the project's technical artefacts. The current version reflects the state of governance planning at the outset of the three-month project period. It is expected to undergo significant refinement during Months 1 and 2 as the architecture is implemented and the DPIA is completed, and to reach a level suitable for ethics committee and data protection authority review by the end of Month 3.

| Version | Date | Author | Summary of Changes |
|---|--|----|--------|
| 0.1 | 2026-03-01 | Clinical Data Management | Initial draft aligned with architecture and technology selections |
