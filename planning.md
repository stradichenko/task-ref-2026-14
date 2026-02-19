## Three-Month Project Plan from a Clinical Data Management Perspective

This plan describes how to move from concept to a validated minimum viable platform for prospective data collection in Myotonic Dystrophy Type 1 (DM1), based on the architecture and technologies defined elsewhere in this project. The platform is mobile-first, role-based, aligned with the General Data Protection Regulation (GDPR) and emerging European Health Data Space (EHDS) requirements, and uses Fast Healthcare Interoperability Resources (FHIR) for clinical interoperability with an Observational Medical Outcomes Partnership Common Data Model (OMOP CDM) layer for research. 

The work over three months is structured into four overlapping workstreams: study and data design, platform implementation and configuration, governance and compliance, and validation and pilot preparation.

### Month 1: Foundation and Detailed Design

#### Objectives

Month 1 focuses on translating the conceptual architecture into concrete study and data specifications, agreeing on standards and coding strategies, and initiating the key governance artefacts. The goal is to define what data will be collected, how it will be structured, and how it is expected to behave in the system.

#### Key activities and deliverables

Study data definition. Clinical Data Management (CDM) leads the development of a detailed data specification covering all elements to be captured via the mobile application and clinician portal. This includes identifiers and linkage fields, eligibility variables, disease-specific questionnaires and scales, symptom diaries, adverse event reporting, concomitant medications, and site-reported outcomes. Each item is documented with a clear definition, permissible values, units, derivation rules where applicable, and handling of missing data.

Instrument and schedule design. In collaboration with clinical investigators, CDM consolidates and designs the electronic instruments to be implemented (electronic patient-reported outcomes (ePROs), clinician-reported forms, visit schedules). This covers visit windows, diary frequencies, conditional questions, and language variants. The result is a set of version-controlled form specifications that can be configured in the study configuration service and surfaced consistently in the mobile and web front-ends.

Standards, terminologies, and coding. In parallel, CDM agrees with data engineering and biostatistics on use of standard terminologies, particularly where OMOP CDM is the downstream model. Target mappings to Systematized Nomenclature of Medicine Clinical Terms (SNOMED CT), Logical Observation Identifiers Names and Codes (LOINC), and OMOP concepts are identified where feasible, and areas requiring local or custom concepts are highlighted. This ensures early alignment between operational data fields and the OMOP vocabulary strategy.

Minimal FHIR profile set. Together with the technical team, CDM participates in defining the minimal set of FHIR resources and profiles needed to represent the study data and patient context (for example Patient, Questionnaire, QuestionnaireResponse, Observation, Encounter, Condition, MedicationStatement). At this stage the focus is on ensuring that each item in the data specification can be expressed in FHIR without semantic loss and on documenting the mapping between forms and FHIR structures.

Role and permission matrix. Building on the role model defined in the architecture, CDM drafts a detailed role and permission matrix specifying which actions each role may perform on which objects. Examples include: patients creating and viewing their own entries within defined time windows; site staff reviewing and annotating data only for participants at their site; CDM configuring forms and running data quality reports; data engineers managing extract-transform-load (ETL) configurations without direct access to edit clinical values; and auditors with read-only access to audit trails. This matrix will later be implemented in the Identity and Access Management (IAM) layer (for example, Keycloak) and in the application services.

Initial governance documentation. In collaboration with legal, the data protection officer, and quality assurance, CDM initiates core governance documents: the data management plan outline, a draft data protection impact assessment (DPIA) structure, requirements for consent content, and high-level data flow diagrams referencing FHIR interfaces and OMOP outputs. These artefacts are intentionally drafted early so they can be refined as the technical design and implementation mature.

By the end of Month 1, the main deliverables from a CDM perspective are: a complete study data specification, designed and versioned instruments and schedules, an initial coding and standards strategy, a draft role and permission matrix, and first versions of governance documents aligned with the chosen architecture and technologies.

### Month 2: Configuration, Implementation Support, and Governance Detailing

#### Objectives

Month 2 is dedicated to implementing the study design in the platform, supporting the technical teams during build, and elaborating the governance and compliance framework. CDM works closely with development, data engineering, and security to ensure that the implemented system reflects the intended study logic and regulatory expectations.

#### Key activities and deliverables

Configuration of forms and schedules. Using the study configuration capabilities in the backend, CDM (or a delegated configuration specialist) configures questionnaires, visit schedules, and edit checks according to the Month 1 specifications. This includes range checks, cross-field consistency rules, protocol-driven constraints, and soft or hard validation messages aligned with the data management plan and protocol.

Review of early application prototypes. As the mobile application and clinician portal become available in a test environment, CDM participates in structured walkthroughs. The focus is on data entry flows, clarity of question wording, skip logic, error handling, and the overall burden of use for DM1 patients and site staff. Feedback from these reviews informs iterative refinements before broader testing.

Specification and testing of FHIR mappings. CDM, together with developers, validates that each form and data element is mapped correctly to FHIR resources and fields, and that the mapping logic is documented. Trial exports of example subjects as FHIR bundles are used to confirm that semantics and coding are preserved. These mapping specifications form a key input for later ETL development into OMOP CDM.

OMOP ETL design support. In parallel, data engineers work on the ETL pipelines from the operational PostgreSQL database to the OMOP warehouse. CDM provides subject-matter input on the correspondence between study variables and OMOP tables and concepts, reviews draft mapping specifications produced with tools such as WhiteRabbit and Rabbit in a Hat, and helps prioritise which domains (for example, conditions, measurements, drugs, observations) must be fully supported in the initial research dataset.

Audit trail and data correction workflows. Building on the role and permission matrix and governance drafts, CDM collaborates with developers to define how data corrections, queries, and annotations are handled in the system. This includes specifying when reasons for change are mandatory, how historical values are retained, and how these events appear in the audit trail. The resulting workflows must support both routine data cleaning and regulatory inspection needs.

Governance artefacts and DPIA refinement. With a clearer view of the implemented stack (Keycloak, PostgreSQL, FHIR facade, OMOP, orchestration with Airflow or Prefect, and observability components), CDM and the data protection officer refine the DPIA, retention rules, consent language, and data access request procedures. Standard operating procedures for handling subject access requests and for granting researchers access to OMOP datasets are drafted and aligned with institutional policies.

By the end of Month 2, the expectation is to have the initial study configuration live in a test environment, preliminary FHIR mappings validated on sample data, first ETL designs for OMOP documented, and governance documents brought to a level that accurately reflects the implemented architecture.

### Month 3: Validation, User Testing, and Pilot Readiness

#### Objectives

Month 3 is focused on validating behaviour against specifications, confirming end-to-end data flow from mobile capture through to OMOP, and preparing for a controlled pilot deployment. CDM concentrates on testing, documentation, and ensuring that operational and governance processes are ready.

#### Key activities and deliverables

Data management testing. CDM defines and executes data management test cases that exercise typical and edge-case scenarios: complete and incomplete forms, corrections within and beyond permitted time windows, out-of-range entries, conflicting values, adverse event reporting, and query workflows. Testing is performed in the test environment, with issues logged and prioritised for resolution.

Verification of audit trails and role-based access control (RBAC). Using the audit and observability tooling, CDM and internal auditors verify that user actions are captured as required and that role-based access control is correctly enforced. Test cases cover role changes, data corrections, exports, consent withdrawals, and configuration changes. Particular attention is given to the immutability, completeness, and access control of the audit trail.

End-to-end FHIR to OMOP validation. Once ETL pipelines are in place, the team performs an end-to-end validation using synthetic or early pilot subject data. Entries captured through the mobile app and portal pass through the FHIR layer into the operational store and are then transformed into OMOP CDM tables. CDM checks that key variables, relationships, and terminologies appear as expected in OMOP and that basic cohort definitions in Atlas return the anticipated results.

Usability sessions with patients and site staff. In collaboration with the clinical team, CDM organises structured usability sessions with a small number of DM1 patients or caregivers and with site personnel. These sessions focus on data completeness, clarity of instructions, perceived burden, and points where errors are likely. Findings are documented and translated into specific changes to wording, workflows, or notifications where necessary.

Finalisation of CDM and governance documentation. As technical issues are resolved, CDM finalises the data management plan, the description of edit checks, data flows, and derived variables, and the sections of the protocol or supporting documentation that describe the electronic data capture and data processing environment. In parallel, the DPIA and related privacy documentation are completed to a level suitable for review by ethics committees and data protection authorities.

Pilot preparation. Together with technical operations and the study leadership, CDM defines the scope and criteria for a limited pilot phase: participating sites, initial enrolment targets, monitoring indicators, and an issue escalation process. Specific OMOP extracts and analysis templates are prepared to allow early review of data quality and completeness during the pilot.

By the end of Month 3, the platform should be ready for a tightly scoped pilot. The core study configuration is implemented, data flows have been validated from mobile capture through FHIR and into OMOP, RBAC and audit mechanisms have been tested, and the necessary documentation and governance arrangements are in place.

### Dependencies and Interactions

Across the three months, several dependencies and cross-team interactions are critical from a CDM perspective. Progress on study configuration and form implementation depends on early agreement with clinicians regarding instruments and schedules, and on timely feedback from the technical team about what is feasible in the initial mobile and backend releases. FHIR and OMOP mapping work requires sustained collaboration between CDM and data engineering, since choices about variable definitions and coding directly influence ETL design and analytical usability. Governance and compliance documents, including the DPIA and consent materials, cannot be fully finalised until the architecture and technology stack are sufficiently stable, which calls for iterative engagement with legal, the data protection officer, and system architects.

To manage these dependencies, regular touchpoints are recommended: weekly coordination meetings between CDM and development to track implementation status and resolve design questions; bi-weekly alignment sessions with data engineers focused on mappings, ETL progress, and OMOP outputs; and monthly or milestone-based reviews with governance and compliance stakeholders. These interactions help maintain coherence across workstreams, reduce the risk of late rework, and support realistic delivery against the three-month plan.

### Key Risks and Mitigation Strategies

Several risks are inherent in a project of this nature. One major risk is underestimating the complexity of mapping between study-specific variables, FHIR resources, and OMOP CDM, which can delay generation of research-ready datasets. A practical mitigation is to prioritise a minimal, high-value subset of variables for complete end-to-end mapping in the first three months, while explicitly planning subsequent phases to broaden coverage.

Another important risk is suboptimal usability for DM1 patients and caregivers, which could reduce adherence or introduce systematic data quality issues. Early and repeated usability testing, combined with accessibility-focused design principles, mitigates this risk and supports better adherence.

There is also a schedule risk that governance and legal reviews may proceed more slowly than technical implementation, particularly in relation to GDPR, EHDS alignment, and cross-border data sharing. Starting governance work in Month 1, maintaining a clear review calendar, and engaging ethics and data protection stakeholders early reduces the likelihood that regulatory concerns will block deployment late in the timeline.

Finally, there are technical integration risks in combining multiple open source components, including Keycloak, PostgreSQL, FHIR libraries, OMOP tooling, and orchestration frameworks. These can be managed through close collaboration between CDM, solution architects, and engineering leads, early establishment of an integration environment that resembles production, and incremental end-to-end testing rather than deferring integration to the end of the three-month period.

From a Clinical Data Management standpoint, success over these three months is measured not only by technical readiness, but by the clarity and completeness of data specifications, the robustness of configured edit checks and workflows, demonstrable traceability from raw entries to OMOP outputs, and acceptance of the system and processes by patients, sites, and governance bodies as the project moves into its first pilot phase.

