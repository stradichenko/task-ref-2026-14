## Minimal FHIR Profile Set for the DM1 Prospective Data Collection Platform

This document specifies the minimal set of Fast Healthcare Interoperability Resources (FHIR) profiles required to represent the study data and patient context for the prospective data collection platform targeting Myotonic Dystrophy Type 1 (DM1). It defines, for each profile, the base resource, the constrained elements, the required terminology bindings, the extensions introduced, and the relationships to other profiles in the set. The profile set is designed to be the smallest coherent collection that allows every item in the study data specification to be expressed in FHIR without semantic loss, while remaining compatible with the downstream extract-transform-load (ETL) pipeline into the Observational Medical Outcomes Partnership Common Data Model (OMOP CDM) research warehouse.

The profiles described here are aligned with the architecture's operational data model, the coding strategy defined in the standards and terminologies document, and the governance framework's requirements for pseudonymisation, consent linkage, and audit. Where applicable, profiles derive from or reference existing international specifications, including HL7 FHIR R4 (release 4.0.1), the International Patient Summary (IPS), and HL7 Europe base profiles.

### Design Principles

The profile set is governed by a small number of principles that balance regulatory alignment, interoperability, and practical study operations.

| Principle | Description |
|----------|-------------|
| Minimal constraint | Enforce only those rules needed for data quality, interoperability, and downstream mapping. Optional or site-specific elements are left flexible so that protocol amendments and site variability do not require constant profile changes. |
| Pseudonymisation by default | Exclude direct identifiers from all operational FHIR resources. Participants are referenced only through pseudonymous study identifiers, with direct identifiers confined to the separate Identity Store, supporting General Data Protection Regulation (GDPR) and European Health Data Space (EHDS) alignment. |
| Terminology-first coding | Bind every coded element to value sets based on standard terminologies (Systematized Nomenclature of Medicine Clinical Terms (SNOMED CT), Logical Observation Identifiers Names and Codes (LOINC), Anatomical Therapeutic Chemical (ATC), International Classification of Diseases (ICD), Orphanet) or well-governed project value sets, marked as required where analytical consistency is critical. |
| Reuse before invention | Prefer existing international profiles and implementation guides (for example International Patient Summary and HL7 Europe base profiles) as bases, adding extensions only when no suitable core element or standard extension exists. |
| Explicit version control | Assign each profile a canonical URL and version, managed alongside the study configuration and instruments, and enforce validation against the active version in the FHIR facade under the governance change management process. |

### Profile Catalogue

The following sections describe each profile in the minimal set. For each profile, the description covers the base resource, the purpose within the platform, the key structural constraints, the terminology bindings, any extensions, and the references to other profiles.

| Profile | Base resource | Primary role |
|---------|--------------|--------------|
| DM1 Patient | Patient | Enrolled study participant with pseudonymous identifier, demographics, and consent linkage. |
| DM1 RelatedPerson | RelatedPerson | Caregiver or representative authorised to act on behalf of a participant. |
| DM1 Encounter | Encounter | Visit or diary period that provides temporal and contextual anchoring for data. |
| DM1 Questionnaire | Questionnaire | Canonical definition of each version-controlled electronic instrument. |
| DM1 QuestionnaireResponse | QuestionnaireResponse | Single completed submission of an instrument by a patient, caregiver, or clinician. |
| DM1 Observation | Observation | Individual clinical measurement or derived score not directly represented as a questionnaire item. |
| DM1 Condition | Condition | DM1 diagnosis and other clinical findings, comorbidities, and complications. |
| DM1 MedicationStatement | MedicationStatement | Patient- or caregiver-reported medication use and history. |
| DM1 MedicationRequest | MedicationRequest | Clinician-prescribed medications and treatment changes, including data imported from electronic health records (EHRs). |
| DM1 AdverseEvent | AdverseEvent | Adverse events from initial report through classification and resolution. |
| DM1 Consent | Consent | Informed consent decisions governing data collection and secondary use. |
| DM1 AuditEvent | AuditEvent | Interoperable representation of audit trail entries for governance and inspection. |

### DM1 Patient Profile

#### Base Resource

FHIR Patient (R4)

#### Purpose

Represents an enrolled study participant. This is the central resource to which all clinical data are linked. It carries the pseudonymous study identifier, demographic attributes needed for research stratification and OMOP mapping, and a reference to the participant's consent status.

#### Key Constraints

The identifier element is constrained to require exactly one identifier with a system URI corresponding to the project's pseudonymous identifier namespace. Identifiers from national systems, hospital medical record numbers, or any other system that could serve as a direct identifier are prohibited through an invariant that rejects unrecognised identifier system URIs.

The name element is constrained to zero cardinality. No name information is stored in the Patient resource. Display names for clinical workflows, where needed, are resolved from the Identity Store at presentation time and never persisted in the clinical data store.

The birthDate element is constrained to year and month only (YYYY-MM format) to reduce re-identification risk while preserving sufficient precision for age-based stratification and OMOP PERSON year_of_birth mapping. Exact date of birth is held in the Identity Store if needed for clinical purposes.

The gender element is required and bound to the FHIR AdministrativeGender value set (male, female, other, unknown), which maps directly to OMOP gender concepts.

The address and telecom elements are constrained to zero cardinality. No contact information is stored in the Patient resource.

The communication element is optional and carries the participant's preferred language using the IETF BCP 47 language tag value set. This supports multilingual instrument delivery.

A contained reference to a Consent resource or a reference extension linking to the participant's current consent record is included, enabling downstream services and the ETL pipeline to determine consent scope without querying a separate service at every access.

#### Extensions

An extension carrying the Orphanet rare disease identifier (ORPHA:273 for DM1) is included to support registry linkage and EHDS secondary use. The extension uses a coding element bound to the Orphanet code system.

An extension for study enrolment date is defined, recording the date the participant was formally enrolled. This supplements the Patient resource's period-of-care semantics and maps to OMOP OBSERVATION_PERIOD start date.

#### Terminology Bindings

Gender: FHIR AdministrativeGender (required). Language: IETF BCP 47 (preferred). Rare disease identifier: Orphanet (required within the extension).

### DM1 RelatedPerson Profile

#### Base Resource

FHIR RelatedPerson (R4)

#### Purpose

Represents a caregiver or legal representative authorised to act on behalf of a patient, including submitting data through the mobile application under proxy entry rules defined in the role-based access control (RBAC) model.

#### Key Constraints

The patient element references the DM1 Patient Profile and is required.

The relationship element is required and bound to a value set drawn from the FHIR PatientRelationshipType value set, constrained to the subset relevant to the study (for example, parent, spouse, child, guardian, other caregiver).

As with the Patient profile, the name, address, and telecom elements are constrained to zero cardinality. The RelatedPerson is identified through a pseudonymous identifier in the same namespace as the Patient, ensuring that the Identity Store remains the sole location for direct identifiers.

The communication element mirrors the Patient profile convention, supporting preferred language for instrument delivery.

### DM1 Encounter Profile

#### Base Resource

FHIR Encounter (R4)

#### Purpose

Represents a study visit, a diary completion period, or any other data collection event that groups related clinical observations and questionnaire responses. Encounter serves as the temporal and contextual anchor for all data captured during a visit or reporting window.

#### Key Constraints

The status element is required and bound to the FHIR EncounterStatus value set (planned, arrived, in-progress, on-leave, finished, cancelled, entered-in-error).

The class element is required and bound to a project-defined value set that distinguishes scheduled study visits, unscheduled visits, remote diary periods, and ad hoc event reports. This classification supports visit-window logic and maps to OMOP VISIT_OCCURRENCE visit_concept_id.

The type element is bound to a value set of study-defined visit types (for example, baseline, follow-up month three, follow-up month six, annual review, symptom diary window, adverse event report). Each type carries a SNOMED CT code where a suitable concept exists, or a project-defined code where it does not.

The subject element references the DM1 Patient Profile and is required.

The period element is required and records the start and end timestamps of the encounter in Coordinated Universal Time (UTC). For diary periods, the period spans the window during which the patient was expected to complete entries.

The serviceProvider element is optional and references the Organisation resource representing the participating site. This supports site-scoped access control and OMOP VISIT_OCCURRENCE care_site mapping.

#### Extensions

A protocol-visit-number extension records the visit number as defined in the study protocol schedule, independent of the encounter's chronological position. This supports protocol deviation detection and alignment with the study configuration service's schedule definitions.

A visit-window extension records the allowed visit window (earliest and latest permissible dates) for protocol-scheduled encounters, enabling automated flagging of out-of-window visits.

### DM1 Questionnaire Profile

#### Base Resource

FHIR Questionnaire (R4)

#### Purpose

Represents a version-controlled electronic instrument: an electronic patient-reported outcome (ePRO), a clinician-reported form, or a structured diary. The Questionnaire resource is the canonical definition of the instrument; individual completions are captured through the QuestionnaireResponse profile.

#### Key Constraints

The url element is required and carries the canonical URL of the instrument within the project's FHIR namespace.

The version element is required. Every change to an instrument produces a new version, and the version identifier is immutable once published. This supports the governance framework's change management requirements and ensures that each QuestionnaireResponse can be traced to the exact instrument version used.

The status element is required (draft, active, retired, unknown). Only active questionnaires are surfaced to patients and site staff through the mobile application and clinician portal.

The title and description elements are required and carry the human-readable instrument name and purpose in the study's primary language. The Questionnaire's translation extension is used for multilingual variants.

Each item element carries a linkId (unique within the questionnaire), a type (group, display, boolean, decimal, integer, date, dateTime, time, string, text, url, choice, open-choice, attachment, reference, quantity), and a code element binding the question to a terminology concept. For items that correspond to validated clinical scales, the code is a LOINC identifier. For study-specific questions, the code uses the project code system.

Enable-when conditions implement skip logic and conditional display. These mirror the conditional question rules defined in the instrument specification and are enforced by both the mobile application (for user experience) and the backend (for data validation).

Required items are marked with the required flag. Items with defined answer ranges or permissible values carry answerValueSet or answerOption constraints, which serve as the FHIR-level representation of edit checks.

#### Extensions

A scoring-algorithm extension documents the method for computing summary scores from individual items, referencing the scoring logic version and parameters. This supports reproducibility and OMOP mapping of derived scores.

An instrument-category extension classifies the questionnaire (ePRO, clinician-reported, caregiver-reported, mixed) for reporting and analysis purposes.

### DM1 QuestionnaireResponse Profile

#### Base Resource

FHIR QuestionnaireResponse (R4)

#### Purpose

Represents a single completed submission of a questionnaire by a patient, caregiver, or clinical researcher. This is the primary vehicle for capturing structured data from the mobile application and clinician portal.

#### Key Constraints

The questionnaire element is required and carries the canonical URL and version of the originating DM1 Questionnaire Profile, establishing a traceable link between the response and the instrument definition.

The status element is required (in-progress, completed, amended, entered-in-error, stopped). Responses with status in-progress represent saved but not yet submitted forms, supporting the save-and-return workflow important for DM1 patients who may experience fatigue during data entry.

The subject element references the DM1 Patient Profile and is required.

The encounter element references the DM1 Encounter Profile and is required for responses associated with a defined visit or diary period.

The authored element records the timestamp of the response completion in UTC and is required.

The author element references the individual who completed the form. For patient-submitted entries, this references the Patient resource. For caregiver-submitted entries, this references the RelatedPerson resource. For clinician-completed forms, this references a Practitioner resource. The distinction supports attribution in the audit trail and RBAC enforcement.

Each item element carries a linkId matching the corresponding item in the originating Questionnaire, and an answer element whose type aligns with the item type defined in the questionnaire. Items left unanswered are omitted from the response, and their absence is interpreted according to the missing-data handling rules in the data management plan.

#### Extensions

A submission-device extension records the device type (mobile, tablet, desktop) and operating system from which the response was submitted. This supports data quality analysis and usability evaluation.

A correction-history extension, used when the response status is amended, references the prior version of the response and carries the reason for amendment, the identity and role of the person who made the correction, and the timestamp of the correction. This extension is the FHIR-level representation of the audit trail for data corrections.

### DM1 Observation Profile

#### Base Resource

FHIR Observation (R4)

#### Purpose

Represents an individual clinical measurement, derived score, or structured data point that does not originate from a questionnaire. Typical uses include grip strength, forced vital capacity, electrocardiogram intervals (PR interval, QRS duration, QTc), body weight, and computed clinical scores.

#### Key Constraints

The status element is required and bound to the FHIR ObservationStatus value set (registered, preliminary, final, amended, corrected, cancelled, entered-in-error, unknown).

The category element is required and bound to the FHIR Observation Category value set (vital-signs, laboratory, survey, exam, social-history, activity), extended with a project-defined category for DM1-specific neuromuscular assessments.

The code element is required and bound to a value set combining LOINC (preferred) and project-defined codes (as a fallback for DM1-specific measures not yet in LOINC). This is the primary semantic anchor for the observation and the key input for OMOP MEASUREMENT and OBSERVATION mapping.

The subject element references the DM1 Patient Profile and is required.

The encounter element references the DM1 Encounter Profile and is required where the observation is associated with a study visit.

The effective element (effectiveDateTime or effectivePeriod) records when the observation was made, in UTC, and is required.

The value element carries the result. For quantitative measurements, valueQuantity is used with the Unified Code for Units of Measure (UCUM) system for units. For coded findings, valueCodeableConcept is used with SNOMED CT bindings. For ordinal scales, valueInteger or valueQuantity with a defined scale is used.

The referenceRange element is populated where clinically meaningful reference ranges exist, supporting automated flagging of out-of-range values in the data quality layer.

The derivedFrom element references the source data (for example, a QuestionnaireResponse from which a summary score was computed), supporting traceability from derived values back to raw entries.

#### Extensions

A measurement-method extension records the instrument or technique used for the measurement (for example, hand-held dynamometer for grip strength, spirometer model for respiratory function), supporting quality assessment and cross-site comparability.

### DM1 Condition Profile

#### Base Resource

FHIR Condition (R4)

#### Purpose

Represents a diagnosis or clinical finding, including the primary DM1 diagnosis, comorbidities, complications, and intercurrent illnesses reported during the study.

#### Key Constraints

The clinicalStatus element is required and bound to the FHIR ConditionClinicalStatusCodes value set (active, recurrence, relapse, inactive, remission, resolved).

The verificationStatus element is required and bound to the FHIR ConditionVerificationStatus value set (unconfirmed, provisional, differential, confirmed, refuted, entered-in-error).

The category element is required, distinguishing encounter-diagnosis from problem-list-item, which supports both point-in-time reporting and longitudinal tracking.

The code element is required and bound to a value set combining SNOMED CT (preferred) and ICD-10 (as a secondary axis). For the primary DM1 diagnosis, the value set includes SNOMED CT 77956009 (Myotonic dystrophy) and its children, ICD-10 G71.1, and the Orphanet identifier ORPHA:273 as an additional coding. The ability to carry multiple codings on a single Condition resource ensures that the diagnosis is represented in whichever system a receiving registry or the OMOP ETL pipeline requires.

The subject element references the DM1 Patient Profile and is required.

The encounter element references the DM1 Encounter Profile where the condition was recorded or updated during a specific visit.

The onset element (onsetDateTime, onsetAge, or onsetPeriod) records when the condition first appeared or was first diagnosed, supporting longitudinal disease characterisation and OMOP CONDITION_OCCURRENCE condition_start_date mapping.

The abatement element records resolution or remission where applicable.

The recorder element references the individual who recorded the condition (patient, caregiver, or clinician), supporting attribution.

#### Extensions

A disease-severity extension carries an ordinal or coded severity assessment specific to DM1, such as a Muscular Impairment Rating Scale (MIRS) grade, using a project-defined value set. This extension provides a structured place for disease staging that the base Condition resource does not natively support at the required granularity.

### DM1 MedicationStatement Profile

#### Base Resource

FHIR MedicationStatement (R4)

#### Purpose

Represents a medication that a patient is currently taking, has recently taken, or has stopped taking, as reported by the patient, caregiver, or clinician. This is the primary resource for concomitant medication recording in the study.

#### Key Constraints

The status element is required and bound to the FHIR MedicationStatementStatus value set (active, completed, entered-in-error, intended, stopped, on-hold, unknown, not-taken).

The medication element is required and uses a CodeableConcept bound to a value set drawing from ATC at the chemical substance level (fifth level) as the primary classification, supplemented by RxNorm or RxNorm Extension where more granular identification is needed for OMOP DRUG_EXPOSURE mapping. Where the patient reports a medication by brand name and the exact substance cannot be resolved at the point of capture, the free-text name is recorded alongside the best available ATC code, and the reconciliation is flagged for review by site staff.

The subject element references the DM1 Patient Profile and is required.

The context element references the DM1 Encounter Profile where the medication was reported or reviewed.

The effectivePeriod element records the start and, where known, end dates of the medication use, supporting longitudinal drug exposure analysis and OMOP drug_exposure_start_date and drug_exposure_end_date mapping.

The dosage element is optional but encouraged. Where reported, it carries the dose quantity (using UCUM units), route (coded using SNOMED CT or EDQM Standard Terms), and frequency (using the FHIR Timing data type).

The informationSource element distinguishes whether the medication was reported by the patient, a caregiver, or a clinician, which is relevant for data quality assessment.

### DM1 MedicationRequest Profile

#### Base Resource

FHIR MedicationRequest (R4)

#### Purpose

Represents a prescribed medication or a treatment change initiated by a clinician, as distinct from the patient-reported medication history captured in MedicationStatement. This profile is used when the study protocol requires recording prescriber-initiated actions alongside patient self-reports, or when data are imported from external electronic health records (EHRs).

#### Key Constraints

The status element is required and bound to the FHIR MedicationRequestStatus value set (active, on-hold, cancelled, completed, entered-in-error, stopped, draft, unknown).

The intent element is required (proposal, plan, order, original-order, reflex-order, filler-order, instance-order, option).

The medication element follows the same coding conventions and value set as the MedicationStatement profile, ensuring consistency in drug coding across self-report and prescriber channels.

The subject element references the DM1 Patient Profile and is required.

The encounter element references the DM1 Encounter Profile.

The authoredOn element records when the prescription was written, in UTC.

The requester element references the prescribing clinician.

The dosageInstruction element mirrors the MedicationStatement dosage conventions.

### DM1 AdverseEvent Profile

#### Base Resource

FHIR AdverseEvent (R4)

#### Purpose

Represents an adverse event reported by a patient through the mobile application or flagged by a clinical researcher during data review. The profile supports the full adverse event lifecycle from initial report through investigation, classification, and resolution.

#### Key Constraints

The actuality element is required (actual or potential).

The event element is required and bound to a value set combining Medical Dictionary for Regulatory Activities (MedDRA) preferred terms (where the study requires MedDRA coding for regulatory reporting) and SNOMED CT clinical finding concepts. Where both systems are used, both codings are carried on the same CodeableConcept, and the ETL pipeline maps the SNOMED CT coding to the OMOP CONDITION_OCCURRENCE table while the MedDRA coding supports regulatory report generation.

The subject element references the DM1 Patient Profile and is required.

The encounter element references the DM1 Encounter Profile where the event was reported or assessed.

The date element records when the event occurred or was first observed, and is required.

The detected element records when the event was identified or reported to the study team.

The recordedDate element records when the event was entered into the system.

The seriousness element is bound to the FHIR AdverseEventSeriousness value set (serious, non-serious), extended with a project-defined value set for sub-classifications relevant to regulatory reporting (results in death, life-threatening, requires hospitalisation, results in persistent or significant disability, congenital anomaly, other medically important condition).

The severity element is bound to the FHIR AdverseEventSeverity value set (mild, moderate, severe).

The outcome element is bound to the FHIR AdverseEventOutcome value set (resolved, resolving, not-resolved, resolved-with-sequelae, fatal, unknown).

The recorder element references the individual who entered the event.

The contributor element references clinicians involved in assessing or classifying the event.

#### Extensions

A causality-assessment extension carries the investigator's assessment of the relationship between the adverse event and the study or the participant's underlying DM1 condition, using a project-defined value set (unrelated, unlikely, possible, probable, definite, not assessable).

A regulatory-report-reference extension links the adverse event to any external regulatory report submitted (for example, a safety report identifier), supporting traceability between the platform and the regulatory reporting pipeline.

### DM1 Consent Profile

#### Base Resource

FHIR Consent (R4)

#### Purpose

Represents the participant's informed consent record, including which aspects of data collection and secondary use the participant has agreed to. The Consent resource is the FHIR-level representation of the decisions captured through the eConsent workflow and is referenced by the Identity and Access Management (IAM) layer to enforce consent-based access restrictions.

#### Key Constraints

The status element is required (draft, proposed, active, rejected, inactive, entered-in-error).

The scope element is required and bound to the FHIR ConsentScope value set (research, patient-privacy, treatment), with research and patient-privacy as the relevant scopes for this platform.

The category element is required, identifying the consent as informed consent for research participation using the FHIR ConsentCategoryCodes.

The patient element references the DM1 Patient Profile and is required.

The dateTime element records when the consent was given or last updated, in UTC.

The organization element references the institution responsible for the study at the participant's site.

The provision element carries the granular consent decisions. Each provision specifies the type (permit or deny), the period during which the provision is effective, the purpose (coded using a project-defined value set distinguishing core study data collection, optional data elements, secondary research use, data sharing through EHDS mechanisms, and sharing with external registries), and the data scope to which the provision applies. This granularity matches the consent framework described in the governance documentation and ensures that the platform can enforce consent at the data-flow level.

The sourceAttachment or sourceReference element links to the signed consent document, supporting audit and regulatory inspection.

#### Extensions

A consent-version extension records the version identifier of the consent form presented to the participant, enabling traceability between the participant's agreement and the exact information they received.

A withdrawal-details extension, used when the consent status changes to inactive or rejected, records the date of withdrawal, the method (through the mobile application, through the study site, in writing), and the scope of withdrawal (full or partial), supporting the withdrawal-handling process defined in the governance framework.

### DM1 AuditEvent Profile

#### Base Resource

FHIR AuditEvent (R4)

#### Purpose

Provides a FHIR-native representation of audit trail entries generated by the platform. While the primary audit trail is stored in append-only PostgreSQL tables as described in the governance documentation, the AuditEvent profile enables export of audit records in a standard, interoperable format for regulatory inspections, cross-system correlation, and EHDS transparency requirements.

#### Key Constraints

The type element is required and bound to the FHIR AuditEventType value set, extended with project-defined types for study-specific events (data lock, data unlock, consent withdrawal, configuration change, ETL execution).

The subtype element refines the event type with more specific classifications (create, read, update, delete, export, query, login, logout, permission-change).

The action element is required (C for create, R for read, U for update, D for delete, E for execute).

The recorded element captures the timestamp in UTC and is required.

The outcome element records success or failure.

The agent element identifies the actor (user identifier, role at the time of the action, device or IP address) and is required. The agent.who reference resolves to the Patient, RelatedPerson, Practitioner, or system identity that performed the action.

The source element identifies the system component that generated the audit event (mobile application, clinician portal, API service, ETL pipeline, IAM service).

The entity element identifies the data object affected by the action, referencing the specific FHIR resource instance (Patient, QuestionnaireResponse, Observation, Consent, and so forth) and carrying the resource version before and after the change where applicable.

The purposeOfEvent element records the stated purpose of the action where required by policy (for example, routine data entry, data correction with mandatory reason, research export under approved access request).

### Profile Dependencies and References

The profiles form a connected graph. The following summary captures the primary reference relationships.

- DM1 Patient Profile is referenced by all clinical profiles (Encounter, QuestionnaireResponse, Observation, Condition, MedicationStatement, MedicationRequest, AdverseEvent, Consent) as the subject of the data.
- DM1 RelatedPerson Profile references the DM1 Patient Profile and is referenced by QuestionnaireResponse (as author for caregiver-submitted entries).
- DM1 Encounter Profile is referenced by QuestionnaireResponse, Observation, Condition, MedicationStatement, MedicationRequest, and AdverseEvent as the contextual anchor for visit-based data.
- DM1 Questionnaire Profile is referenced by the DM1 QuestionnaireResponse Profile to establish the instrument-response link.
- DM1 Consent Profile references the DM1 Patient Profile and is referenced by the Identity and Access Management (IAM) layer and the de-identification pipeline to enforce consent-based data access and provisioning rules.
- DM1 AuditEvent Profile references any resource in the set through its entity element and any actor through its agent element.

### FHIR Bundles and Transaction Patterns

#### Submission Bundles

When a patient or clinician submits data through the mobile application or portal, the payload is structured as a FHIR transaction Bundle. A typical patient diary submission bundle contains a QuestionnaireResponse (the completed diary), one or more Observation resources (for any discrete measurements reported alongside the diary), and an Encounter resource (if the submission initiates or updates a visit record). The bundle is processed atomically by the Patient Data Capture Service: either all resources are validated, accepted, and persisted, or the entire submission is rejected with structured error information.

#### Export Bundles

For interoperability with external systems, the Integration Service (FHIR facade) assembles searchset or document Bundles containing the requested resources for a given participant or visit. Export bundles are generated on demand and are subject to consent and RBAC checks before release.

#### Validation

All resources, whether submitted individually or within bundles, are validated against the active profile versions at the point of ingestion. Validation covers structural conformance (required elements present, cardinalities respected, data types correct), terminology conformance (coded values belong to the bound value sets), and referential integrity (references resolve to existing resources of the correct profile type). Validation errors are returned to the submitting client with sufficient detail to support correction, and are logged in the audit trail.

### Mapping to OMOP CDM

The relationship between each FHIR profile and the OMOP CDM target tables is documented in the standards and terminologies document and the ETL mapping specifications. The following summary provides the primary mapping paths for reference.

- DM1 Patient Profile maps to OMOP PERSON (demographic attributes) and OBSERVATION_PERIOD (enrolment date through the study enrolment extension).
- DM1 Encounter Profile maps to OMOP VISIT_OCCURRENCE.
- DM1 QuestionnaireResponse Profile items are decomposed into OMOP OBSERVATION or MEASUREMENT rows, depending on the nature of each question and the OMOP domain assignment of its coded concept.
- DM1 Observation Profile maps to OMOP MEASUREMENT (for quantitative observations with LOINC codes in the Measurement domain) or OMOP OBSERVATION (for coded findings and scores assigned to the Observation domain).
- DM1 Condition Profile maps to OMOP CONDITION_OCCURRENCE.
- DM1 MedicationStatement and MedicationRequest Profiles map to OMOP DRUG_EXPOSURE.
- DM1 AdverseEvent Profile maps to OMOP CONDITION_OCCURRENCE (for the clinical event itself, using the SNOMED CT coding) and may additionally feed a study-specific adverse event tracking table outside the core OMOP CDM if required by the study protocol.
- DM1 Consent Profile does not map to an OMOP clinical table but governs which data are eligible for inclusion in the OMOP warehouse through the de-identification and provisioning layer.
- DM1 AuditEvent Profile does not map to OMOP CDM tables but supports the governance, audit, and compliance layer described in the architecture.

### Lifecycle and Governance

Profiles are managed as versioned artefacts within the project's configuration management system. The lifecycle of a profile follows these stages.

- Draft profiles are created during Month 1, based on the study data specification and the instrument designs, and are reviewed by Clinical Data Management (CDM), data engineering, and the technical team.
- Active profiles are published when the study configuration is deployed to the test environment; from this point, the FHIR facade enforces validation against the active profile version.
- Revised profiles are created when a protocol amendment, terminology update, or data quality finding necessitates a change, and are assigned a new version identifier while previous versions remain available for historical validation and audit.
- Retired profiles are profiles that are no longer in active use, typically because a successor version has been published, but are preserved in the version history for validating historical data.
- All profile changes are recorded in the audit trail and the change log, and their impact on downstream systems (FHIR facade validation rules, ETL mapping specifications, OMOP loading logic) is assessed and addressed before the new version is activated.

### Document Control

This document is version-controlled alongside the study data specification, the instrument designs, and the coding strategy. It is expected to evolve significantly during Month 1 as the data specification is finalised and the first profile drafts are tested against synthetic data, and to stabilise during Month 2 as the FHIR facade is implemented and validation is enforced in the test environment.

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 0.1 | 2026-03-01 | Clinical Data Management and Technical Team | Initial draft defining twelve profiles covering the minimal resource set for the DM1 study |
