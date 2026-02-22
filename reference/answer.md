## Mobile App Concept for Prospective Data Collection in Myotonic Dystrophy Type 1

This document outlines a concept for a mobile application to support prospective data collection in patients with Myotonic Dystrophy Type 1 (DM1), with a strong focus on role-based access control (RBAC), data governance, and full traceability of actions. It is written from the perspective of a clinical data manager and aims to provide a blueprint that can later be translated into technical and regulatory specifications.

---

### 1. Overall Objectives

- Enable patients with DM1 to enter data regularly (e.g., symptoms, functional status, medication changes, PROs/HRQoL questionnaires) from their own devices.
- Ensure data is collected and stored in a way that supports clinical research and potentially regulatory-grade evidence (GCP/21 CFR Part 11–aligned where feasible).
- Implement RBAC so that each stakeholder (patient, clinical researcher, data engineer, auditor, data manager) only sees and does what they are allowed to.
- Make every relevant action traceable via an audit trail (who, what, when, where/from which device or IP, and why where appropriate).

---

### 2. Core User Roles and Responsibilities

#### 2.1 Patient

**Typical profile:** Individuals with DM1 (or their caregivers/proxies) using a smartphone or tablet.

**Key capabilities:**
- Register and provide informed consent/assent within the app, including acceptance of privacy notice and study data policy.
- Complete ePRO questionnaires and symptom diaries at scheduled intervals.
- Report ad hoc events (e.g., falls, hospitalizations, medication changes, adverse events).
- Review a personal summary of their own submitted data (e.g., timelines, symptom trends), with careful UI design to avoid misinterpretation as clinical advice.
- Manage their personal account (contact details, notification preferences, language settings).

**Access restrictions:**
- Can access only their own data (or data of the person they are legally authorized to represent).
- No access to other patients’ data or study-level analytics.
- No permission to edit after certain time windows, depending on protocol (e.g., allow correction within 24 hours, then lock to ensure data integrity).

#### 2.2 Clinical Researcher

**Typical profile:** Investigators, sub-investigators, study physicians, and research nurses at participating sites.

**Key capabilities:**
- View patient-level data for participants assigned to their site or under their care.
- Review and validate patient-reported data (e.g., mark records as clinically reviewed, add physician notes or classifications such as “serious adverse event”, “related to study drug”, etc.).
- Create and respond to queries on data (e.g., clarify an unexpected symptom entry with the patient via a messaging or reminder system managed by the study site).
- Monitor adherence: dashboards showing completion rates, late or missed entries, and patients with worsening symptom trends.

**Access restrictions:**
- Restricted to the participants assigned to their site or explicitly linked to their investigator team (site-based or practice-based scope).
- Cannot modify raw patient-entered values once locked; can only add annotations, queries, or clinical assessments.
- No access to system-level configuration, ETL pipelines, or technical logs.

#### 2.3 Data Manager

**Typical profile:** Central clinical data manager overseeing data quality and completeness across the study.

**Key capabilities:**
- Configure and manage eCRF/ePRO instruments within predefined templates (e.g., questionnaires, visit schedules, allowed ranges, missing-data rules).
- Set up edit checks and data validation rules, including automatic checks (range, consistency) and manual review workflows.
- Oversee and manage queries at the study level (create, assign, close queries; track outstanding issues).
- Run data quality reports (e.g., missingness by variable, protocol deviations, frequent corrections, suspicious patterns).
- Lock and unlock data at predefined milestones (e.g., visit-level locks, subject-level lock, interim analysis lock).

**Access restrictions:**
- No access to full identifying information if working in a pseudonymized context (configurable: may see subject codes but not direct identifiers if separation of duties is required).
- Cannot change the study protocol or legal consent texts; those changes follow a controlled change management process.
- Cannot directly edit patient-entered values; corrections go through a query-based mechanism.

#### 2.4 Data Engineer

**Typical profile:** Technical staff responsible for data pipelines, integration, and warehousing.

**Key capabilities:**
- Configure secure data export to analytical environments (e.g., CDISC SDTM/ADaM pipelines, research data warehouse, external statistical analysis environment).
- Manage ETL jobs and transformation scripts, including versioning and deployment (e.g., via CI/CD).
- Set up and maintain interfaces with external services (e.g., eConsent system, EHR integration, wearables, CDMS/EDC systems).
- Monitor system performance, job failures, and storage health.

**Access restrictions:**
- Preferably restricted to pseudonymized data for routine operations; access to re-identification keys only in strictly controlled procedures.
- No permission to manually manipulate clinical values directly in production databases.
- No direct ability to modify study configuration or clinical content; these are managed by data managers and clinical team.

#### 2.5 Auditor

**Typical profile:** Internal or external auditor (e.g., QA, regulatory authority, sponsor QA), often with limited time and highly specific information needs.

**Key capabilities:**
- Read-only access to the full audit trail for selected subjects, forms, or periods.
- View snapshots of study configurations and data as of specific dates (e.g., at the time of database lock or interim analysis).
- Export documentation of system validation, SOPs, and role definitions.
- Filter and review security-relevant events (e.g., failed login attempts, permission changes, data corrections).

**Access restrictions:**
- No ability to modify data, configurations, or system settings.
- Time-limited accounts with clearly defined scopes (e.g., study X only, date range Y–Z).

---

### 3. RBAC Model and Permissions

The RBAC model should be defined centrally and enforced at all access layers (mobile app, backend API, admin consoles, and data exports).

#### 3.1 Role Definitions

Suggested core roles:

- `PATIENT` (or `SUBJECT`)
- `CAREGIVER` (optional, with proxy entry rights)
- `CLINICAL_RESEARCHER`
- `DATA_MANAGER`
- `DATA_ENGINEER`
- `AUDITOR`
- `SYSTEM_ADMIN` (technical superuser; strictly limited and monitored)

Each role should map to specific permissions, for example:

- `VIEW_SELF_DATA`, `CREATE_SELF_ENTRY`, `CORRECT_SELF_ENTRY_WITHIN_TIME_WINDOW`
- `VIEW_SITE_SUBJECT_DATA`, `ANNOTATE_SITE_SUBJECT_DATA`, `CREATE_QUERY`, `RESPOND_TO_QUERY`
- `CONFIGURE_FORMS`, `CONFIGURE_EDIT_CHECKS`, `RUN_DATA_QUALITY_REPORTS`, `LOCK_DATA`, `UNLOCK_DATA`
- `CONFIGURE_EXPORTS`, `RUN_ETL_JOBS`, `VIEW_TECHNICAL_LOGS`
- `VIEW_AUDIT_TRAIL`, `VIEW_SYSTEM_CONFIG_SNAPSHOTS`

Implementation-wise, this can be achieved by:

- A central authorization service (e.g., OAuth2/OpenID Connect with scopes/claims or a role/permission table in the backend).
- Role and permission assignments stored with effective dates and logged when changed.
- Fine-grained scopes for APIs (e.g., endpoints for patient data reject any call without a role or scope that explicitly permits that operation).

#### 3.2 Principle of Least Privilege

- By default, users start with the minimum set of permissions needed for their function.
- Elevated permissions (e.g., temporary auditor access, data lock/unlock rights) should require documented approval and appear clearly in the audit trail.
- Site-specific scoping is critical for researchers: they can only access participants assigned to their site or cohort.

---

### 4. Data Governance and Privacy by Design

The system should follow privacy and data protection principles from the start (e.g., GDPR, HIPAA where applicable):

#### 4.1 Data Minimization and Purpose Limitation

- Collect only data necessary for the study protocol and clearly document why each data element is collected.
- Separate optional data (e.g., lifestyle variables) from core variables, with explicit consent and clear labelling.

#### 4.2 Pseudonymization and Separation of Identifiers

- Store direct identifiers (name, contact, national ID numbers) in a separate, access-controlled module or service.
- Use study-specific subject identifiers in the clinical data tables.
- Limit access to re-identification keys to a very small group (e.g., principal investigator, specific data protection officer), with additional justification and approval.

#### 4.3 Consent and Legal Basis

- Implement an eConsent workflow embedded in or tightly coupled to the app: versioned consent forms, timestamps, and confirmation of understanding.
- Ensure that all downstream uses of data (e.g., for secondary research) are aligned with consent options and regulatory requirements.
- Provide mechanisms for withdrawal of consent: clearly define what happens to existing data (e.g., keep for safety reasons but no further collection; delete certain classes of data if allowed).

#### 4.4 Retention and Archiving

- Define retention periods for raw data, audit trails, and system logs that comply with regulatory requirements (often several years after study end).
- Archive data in a format suitable for reuse (e.g., CDISC standards where applicable) and document the transformations.

---

### 5. Full Traceability and Audit Trail

Traceability is fundamental for clinical research, especially for safety-related data.

#### 5.1 Audit Trail Content

For each relevant action, record at least:

- Who performed it (user ID and role at the time of the action).
- What was done (e.g., created entry, modified value, answered query, changed permission, changed configuration).
- When it happened (timestamp with timezone and synchronized clock; ideally UTC).
- Where it originated (device identifier, IP address, and possibly location if justified and consented).
- Why (a free-text reason or reason code for significant modifications, such as data changes or permission changes).

#### 5.2 Events to Track

Examples of events that should be audit-trailed:

- Data capture events (creation, updates, corrections, deletions if allowed).
- Query lifecycle (open, assign, respond, close, re-open).
- Role or permission changes for any user.
- Data lock/unlock actions, database freeze and unfreeze.
- Import/export jobs (who initiated them, what scope of data was included).
- Authentication events (logins, failed logins, multi-factor enrollment or changes).

#### 5.3 Technical Considerations

- Store the audit trail in an append-only structure; avoid allowing direct updates or deletes.
- Use versioning for data records: each change creates a new version; historical versions remain available to authorized roles.
- Provide an auditor-facing UI to filter, search, and export audit trail segments for inspection.

---

### 6. Patient-Facing Design Considerations for DM1

Because this app is aimed at individuals with Myotonic Dystrophy Type 1, the user interface and interaction model should account for potential cognitive, motor, and fatigue-related challenges.

#### 6.1 Accessibility and Usability

- Simplified screens with limited information per page and large, easily tappable controls.
- Clear, non-technical language for questions and instructions, tested with people living with DM1 and their caregivers.
- Optional caregiver/proxy mode to allow a family member or caregiver to support data entry while maintaining clear attribution.
- Configurable reminder schedules (notifications for daily diaries, scheduled visit questionnaires) with options to snooze and reschedule.

#### 6.2 Data Entry Workflows

- Use validated instruments where possible (e.g., disease-specific PRO/HRQoL questionnaires) implemented faithfully.
- Provide save-and-return functionality so patients are not forced to complete long forms in a single sitting.
- Allow photo or document uploads if they are part of the protocol (e.g., discharge summaries), with appropriate privacy warnings.

#### 6.3 Feedback and Visualization

- Offer simple trend views (e.g., symptom severity over weeks/months) while clearly communicating that this is not direct medical advice.
- Provide clear instructions for what to do if certain serious symptoms occur (e.g., contact the study site, emergency numbers), without replacing local medical guidance.

---

### 7. Data Flows and Integrations (High Level)

- Mobile app (patient and caregiver front-end): data capture, consent, notifications.
- Backend API: RBAC enforcement, data validation, business logic, and audit trail writing.
- Clinical data store: structured storage of patient-entered data and clinician annotations.
- Identity and access management service: authentication, role assignments, and session management.
- Analytical/ETL layer: transformation into analysis-ready datasets (e.g., CDISC) with logging and versioning.
- External integrations (optional):
	- EHR systems for baseline data imports (if feasible).
	- Wearables or activity trackers.
	- Third-party eConsent or document management systems.

Each step should have clearly documented interfaces and mapping rules, with change control and validation procedures.

---

### 8. Next Steps from a Clinical Data Manager Perspective

To move from concept to implementation, suggested next steps are:

1. Translate this role and governance model into a formal requirements specification (user requirements, functional requirements, and non-functional requirements).
2. Define the initial set of instruments (questionnaires, visit schedule, data items) to be implemented in the app, including coding (e.g., CDISC terminology where appropriate).
3. Work with data engineers and developers to design the backend RBAC structure and audit trail schema in detail.
4. Align with QA and regulatory teams on validation strategy, testing plans, and documentation templates.
5. Pilot the app with a small group of DM1 patients and site staff to test usability, data completeness, and workflows before broader rollout.

This conceptual design provides a foundation that prioritizes data governance, patient usability, and regulatory-grade traceability, while giving each role (patient, clinical researcher, data engineer, data manager, and auditor) clearly defined, controlled capabilities.

