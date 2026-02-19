## Risk Assessment for the DM1 Prospective Data Collection Platform

This document accompanies the risk matrix and describes the rationale behind each identified risk, its placement on the likelihood-impact grid, and the mitigation strategy selected to bring the residual exposure to an acceptable level within the three-month project timeline.

### Assessment Framework

Risks are evaluated on two axes, each scored from 0 (lowest) to 4 (highest).

| Score | Likelihood | Impact |
|-------|-----------|--------|
| 0 | Very Low: no credible scenario leads to this event within the project window. | Negligible: no measurable effect on timeline, data quality, or compliance. |
| 1 | Low: event is conceivable but unlikely given the planned controls. | Minor: small delay or localised rework with no downstream consequence. |
| 2 | Medium: event has occurred in comparable projects and could occur here. | Moderate: noticeable delay, partial rework, or degraded functionality in one workstream. |
| 3 | High: event is probable without active mitigation. | Major: significant delay, regulatory concern, or loss of confidence from stakeholders. |
| 4 | Very High: event is near-certain without structural change. | Critical: project viability, patient safety, or regulatory compliance is directly threatened. |

The product of the two scores determines the severity band displayed on the heat-map grid, ranging from green (low) through amber (medium) to red (critical).

### Identified Risks

#### R1: Fast Healthcare Interoperability Resources (FHIR) and Observational Medical Outcomes Partnership Common Data Model (OMOP CDM) Mapping Complexity

Likelihood: 3 (High). Impact: 4 (Major). Severity: High.

The mapping chain runs from study-specific variables through FHIR profiles into the operational data store, and then through an extract-transform-load (ETL) pipeline into OMOP CDM tables. Each step involves terminology alignment (Systematized Nomenclature of Medicine Clinical Terms (SNOMED CT), Logical Observation Identifiers Names and Codes (LOINC), Anatomical Therapeutic Chemical (ATC), project-defined concepts), structural transformation, and validation. In comparable projects, underestimating this complexity has been the single most common cause of delayed research-ready datasets.

The risk is rated High on likelihood because the DM1 data specification includes patient-reported outcomes, clinician assessments, and disease-specific scales that do not all have direct OMOP standard concept equivalents. Impact is Major because delays in producing usable OMOP datasets directly undermine the platform's core research value proposition.

Mitigation. Prioritise a minimal, high-value subset of variables for complete end-to-end mapping during the three-month window. Document the scope boundary explicitly so that stakeholders understand what will and will not be available in the initial OMOP warehouse. Plan subsequent phases to broaden coverage incrementally, guided by research priorities.

#### R2: Suboptimal Usability for Myotonic Dystrophy Type 1 (DM1) Patients and Caregivers

Likelihood: 2 (Medium). Impact: 4 (Major). Severity: High.

DM1 presents specific challenges for digital data collection. Patients may experience myotonia affecting fine motor control, fatigue limiting sustained interaction, cognitive involvement reducing tolerance for complex navigation, and variable day-to-day capacity. A mobile application that does not account for these factors risks low adherence, incomplete data, or systematic quality issues that compromise downstream analysis.

The risk is rated Medium on likelihood because accessible design principles and fatigue-aware interaction patterns are well understood and can be applied from the outset. Impact remains Major because poor adherence from a small patient population produces gaps that are difficult to compensate for analytically.

Mitigation. Conduct early and repeated usability sessions with DM1 patients or caregivers, starting with paper prototypes or low-fidelity mockups in Month 1 and moving to functional application walkthroughs in Months 2 and 3. Implement save-and-return functionality, adjustable font sizes, high-contrast options, and short form sections. Treat usability findings as high-priority defects with the same resolution urgency as functional bugs.

#### R3: Slow Governance and Legal Reviews

Likelihood: 3 (High). Impact: 3 (Moderate). Severity: Medium-High.

The platform processes personal health data under the General Data Protection Regulation (GDPR) and is designed to align with emerging European Health Data Space (EHDS) requirements. Governance deliverables include a data protection impact assessment (DPIA), consent language, data access procedures, retention policies, and ethics committee submissions. These artefacts depend on input from legal counsel, data protection officers, and institutional review processes, all of which operate on timelines that the project team cannot fully control.

The risk is rated High on likelihood because multi-stakeholder review cycles routinely exceed initial estimates, particularly when cross-border data sharing or secondary use provisions are involved. Impact is Moderate rather than Major because the pilot can proceed with provisional governance arrangements if full approvals are delayed, provided the provisional arrangements are documented and accepted by the study sponsor.

Mitigation. Start governance work in Month 1, in parallel with technical design. Maintain a clear review calendar with named reviewers and agreed turnaround windows. Engage the data protection officer and ethics committee contacts from the first week, even if initial documents are incomplete, to establish expectations and identify potential blockers early.

#### R4: Technical Integration of Free and Open Source Software (FOSS) Components

Likelihood: 2 (Medium). Impact: 3 (Moderate). Severity: Medium.

The platform assembles several independent open source components: Keycloak for identity and access management, PostgreSQL for operational and research data stores, a FHIR facade built on FastAPI or NestJS, OHDSI tools (Atlas, WebAPI) for the OMOP environment, Apache Airflow or Prefect for pipeline orchestration, and Prometheus, Grafana, and Loki or OpenSearch for observability. Each component is mature individually, but their integration introduces configuration surface area, version compatibility considerations, and operational complexity.

The risk is rated Medium on likelihood because the selected components are widely deployed together in health data platforms and have well-documented integration patterns. Impact is Moderate because integration issues typically manifest as delays in specific workstreams rather than as fundamental blockers, and can be resolved through configuration changes or version pinning.

Mitigation. Establish an integration environment that closely resembles the production target from the first weeks of the project. Conduct incremental end-to-end testing throughout the timeline rather than deferring integration validation to Month 3. Maintain version-pinned dependency manifests for all components and document the integration decisions and configuration choices as they are made.

### Summary

| Risk | Likelihood | Impact | Severity | Primary mitigation |
|------|-----------|--------|----------|-------------------|
| R1: FHIR/OMOP mapping complexity | High (3) | Major (4) | High | Prioritise minimal variable subset for end-to-end mapping; phase broader coverage. |
| R2: Suboptimal DM1 usability | Medium (2) | Major (4) | High | Early and repeated usability testing; fatigue-aware and accessible design. |
| R3: Slow governance/legal reviews | High (3) | Moderate (3) | Medium-High | Start governance in Month 1; named reviewers with agreed turnaround windows. |
| R4: FOSS integration complexity | Medium (2) | Moderate (3) | Medium | Integration environment from week one; incremental end-to-end testing. |

The overall risk profile is manageable within the three-month timeline, provided that mitigations are enacted from the start and that the project team maintains the cross-workstream coordination described in the planning document. The risk matrix should be revisited at each monthly milestone to reassess likelihood and impact in light of progress and emerging information.

### Document Control

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 0.1 | 2026-03-01 | Clinical Data Management and Technical Team | Initial risk assessment covering four risks aligned with the three-month project plan. |
