## Standards, Terminologies, and Coding Strategy for the DM1 Prospective Data Platform

This document defines the standards and terminology strategy for the prospective data collection platform targeting Myotonic Dystrophy Type 1 (DM1). It explains why standardised coding matters in this context, identifies the specific vocabularies and classification systems adopted, describes how they are applied across the operational and research layers of the architecture, and establishes the governance processes for maintaining terminological consistency over time. The strategy is designed to support seamless data flow from the point of capture on a patient's mobile device, through the operational clinical store expressed in Fast Healthcare Interoperability Resources (FHIR), into the Observational Medical Outcomes Partnership Common Data Model (OMOP CDM) research warehouse, and onward to external registries and national health data infrastructures under the European Health Data Space (EHDS).

### Why Standardised Coding Matters

In a platform that collects patient-reported outcomes, clinician assessments, adverse events, and medication data from multiple sites and potentially across borders, the meaning of each recorded value must be unambiguous, stable, and machine-interpretable. Without standardised coding, the same clinical observation can be expressed in dozens of incompatible ways, making aggregation unreliable, research queries brittle, and interoperability with external systems impractical.

Standardised terminologies solve this problem by assigning each clinical concept a unique, persistent identifier drawn from a curated vocabulary. When a patient reports a symptom, when a clinician classifies an adverse event, or when an extract-transform-load (ETL) pipeline maps a source variable into OMOP, the coded concept provides a shared reference point that all downstream systems can interpret consistently. This is especially important for a rare disease like DM1, where multi-site collaboration and pooled analysis are essential for generating meaningful evidence.

Beyond analytical value, standardised coding is increasingly a regulatory expectation. The General Data Protection Regulation (GDPR) and the EHDS both emphasise transparency and interoperability in health data processing. Using recognised terminologies demonstrates that data are collected and processed in a way that is understandable, auditable, and aligned with the broader European health data ecosystem.

### Terminology Landscape for This Platform

The platform operates across two distinct but connected data environments: the operational clinical store, where data are structured around FHIR resources, and the OMOP CDM research warehouse, where data are organised into standardised clinical domain tables with concept-based coding. Each environment draws on overlapping but not identical sets of terminologies. The strategy described here ensures that the two environments remain aligned, with explicit, documented, and testable mappings between them.

### FHIR Resource and Profile Strategy

#### Core FHIR Resources

The operational data model is oriented around a minimal set of FHIR resources chosen to represent the study data without semantic loss. The following resources form the core of the FHIR profile set for this platform.

Patient and RelatedPerson represent the enrolled participant and, where applicable, a caregiver or legal representative acting on their behalf. These resources carry demographic attributes and pseudonymous identifiers, with direct identifiers stored separately in the Identity Store.

Encounter represents a study visit or contact, carrying the visit type, timing, and status. Visit windows and scheduled diary periods are modelled as planned encounters, while completed data collection events generate corresponding encounter records.

Questionnaire and QuestionnaireResponse are the primary vehicles for electronic patient-reported outcomes (ePROs) and clinician-reported forms. Each instrument version is expressed as a Questionnaire resource with coded items, and each completed submission generates a QuestionnaireResponse linked to the originating questionnaire version, the responding patient, and the relevant encounter.

Observation is used for individual clinical measurements, scores, and structured data points that do not fit naturally within a questionnaire structure, such as laboratory results, vital signs, or derived clinical scores. Each observation carries a code identifying what was measured, a value, and references to the patient and encounter.

Condition captures active or historical diagnoses and clinical findings, including the DM1 diagnosis itself and any comorbidities or complications reported during the study.

MedicationStatement and MedicationRequest record concomitant medications, treatment changes, and, where relevant, study-related interventions. These resources carry coded medication identifiers and are linked to the patient and the reporting encounter.

AdverseEvent is used to capture adverse events reported by patients or flagged by clinical researchers, with severity, seriousness, causality, and outcome coded according to study conventions.

#### Profiling Approach

Each FHIR resource is constrained through a profile that specifies which elements are mandatory, which are optional, the value sets (coded answer lists) permitted for coded elements, and any extensions required for DM1-specific data. Profiles are version-controlled alongside the study configuration and are published in a form that the FHIR facade can use for validation at the point of data ingestion.

The profiling approach follows a principle of minimal constraint: profiles enforce what is necessary for data quality and interoperability without over-constraining elements that may vary across sites or evolve during the study. Where international profiles exist, such as those from HL7 Europe or the International Patient Summary, they are adopted or extended rather than reinvented.

### Clinical Terminologies

#### Systematized Nomenclature of Medicine Clinical Terms

Systematized Nomenclature of Medicine Clinical Terms (SNOMED CT) serves as the primary reference terminology for clinical concepts in this platform. SNOMED CT provides a comprehensive, hierarchical system of concepts covering clinical findings, disorders, procedures, body structures, substances, and organisms, with formal definitions and relationships between concepts.

Within the DM1 platform, SNOMED CT is used to code diagnoses and clinical findings recorded in Condition resources, including the DM1 diagnosis itself (SNOMED CT concept 77956009, Myotonic dystrophy) and comorbidities such as cardiac conduction disorders, cataracts, respiratory impairment, and endocrine abnormalities commonly associated with the disease. SNOMED CT is also used for observable entities referenced in Observation and AdverseEvent resources, and for body site qualifiers where anatomical precision is relevant.

The platform adopts the International Edition of SNOMED CT as the baseline, supplemented by the relevant national extension where the deploying institution operates within a country that maintains one. Where a clinical concept relevant to DM1 does not have a suitable SNOMED CT representation, the gap is documented and addressed through the custom concept process described later in this document.

#### Logical Observation Identifiers Names and Codes

Logical Observation Identifiers Names and Codes (LOINC) is the primary terminology for identifying observation types, particularly laboratory tests, clinical measurements, survey instruments, and patient-reported outcome scales. LOINC provides stable, universally recognised identifiers for what was measured or asked, while SNOMED CT typically codes the answer or finding.

In this platform, LOINC codes are used as the primary code for Observation resources representing clinical measurements (such as grip strength, forced vital capacity, or electrocardiogram intervals commonly monitored in DM1), for identifying validated patient-reported outcome instruments (where LOINC panels exist for the instrument), and for laboratory results if the study protocol includes any biochemical markers. LOINC codes are assigned at the instrument and data specification level and are carried through from the operational FHIR store into the OMOP research warehouse.

#### Anatomical Therapeutic Chemical Classification

The Anatomical Therapeutic Chemical (ATC) classification system, maintained by the World Health Organization (WHO) Collaborating Centre for Drug Statistics Methodology, is used for coding concomitant medications recorded in MedicationStatement and MedicationRequest resources. ATC provides a hierarchical classification that groups medications by the organ system they act on, their therapeutic intent, and their chemical substance, which supports both clinical review and aggregate analysis of medication patterns.

Where more granular substance-level coding is needed for the OMOP research warehouse, ATC codes are supplemented by or mapped to RxNorm or RxNorm Extension concepts, which are the standard drug vocabularies within the OMOP CDM.

#### International Classification of Diseases

The International Classification of Diseases (ICD), in its tenth revision (ICD-10) or the eleventh revision (ICD-11) where adopted, is used selectively within the platform. ICD codes may appear in data imported from external electronic health record (EHR) systems, in adverse event reports that reference hospital discharge diagnoses, or in country-specific regulatory submissions. The platform supports ICD coding as an additional classification axis alongside SNOMED CT, with mappings maintained in the OMOP vocabulary infrastructure.

#### Orphanet Rare Disease Ontology

Because Myotonic Dystrophy Type 1 is a rare disease, the Orphanet classification is relevant for identifying the condition in contexts where rare disease registries, European Reference Networks, or EHDS secondary use processes require Orphanet numbering. The Orphanet identifier for DM1 (ORPHA:273) is included in the platform's concept set and is available as an additional coding on the primary Condition resource. This supports linkage with rare disease registries and alignment with European rare disease data standards.

### OMOP CDM Vocabulary Strategy

#### Standard Vocabularies

The OMOP CDM research warehouse uses its own vocabulary infrastructure, managed through the Observational Health Data Sciences and Informatics (OHDSI) Athena vocabulary repository. The standard vocabularies adopted for this platform include SNOMED CT as the primary vocabulary for conditions, observations, and clinical findings; LOINC for measurements and survey instruments; RxNorm and RxNorm Extension for drug exposures; ICD-10 and ICD-10-CM as source vocabularies mapped to SNOMED CT standard concepts; and ATC as a classification vocabulary for drug grouping and analysis.

Each vocabulary is downloaded from Athena at a defined version, loaded into the OMOP warehouse's vocabulary tables (CONCEPT, CONCEPT_RELATIONSHIP, CONCEPT_ANCESTOR, CONCEPT_SYNONYM, VOCABULARY, DOMAIN, CONCEPT_CLASS), and maintained under version control. Vocabulary updates follow the governance process described in this document.

#### Concept Mapping Approach

The mapping from operational data to OMOP concepts follows a layered approach. At the first layer, data elements captured through FHIR resources carry their source codes (SNOMED CT, LOINC, ATC, ICD, or local codes as assigned during instrument design). At the second layer, the ETL pipeline resolves each source code to an OMOP standard concept identifier using the vocabulary tables. Where a direct standard mapping exists (for example, a SNOMED CT code that maps to a standard OMOP concept in the Condition domain), the mapping is straightforward. Where the source code maps to a non-standard OMOP concept, the pipeline follows the concept relationships to identify the appropriate standard concept. Where no mapping exists, the value is loaded with a concept identifier of zero and flagged for review.

This approach ensures that all data reach the OMOP warehouse, even when mappings are incomplete, while clearly distinguishing mapped from unmapped values and enabling systematic improvement over time.

#### OMOP Domains and Target Tables

The following OMOP CDM tables are populated in the initial release, corresponding to the primary data domains captured by the platform.

PERSON receives demographic and enrolment information, derived from the pseudonymised Patient resource. Gender, year of birth, and race or ethnicity (where collected and consented) are coded using OMOP standard concepts.

VISIT_OCCURRENCE records study visits and data collection events, mapped from FHIR Encounter resources.

CONDITION_OCCURRENCE stores diagnoses and clinical findings, mapped from FHIR Condition resources using SNOMED CT as the primary source vocabulary.

DRUG_EXPOSURE records concomitant medications and treatment changes, mapped from MedicationStatement and MedicationRequest resources using ATC and RxNorm.

MEASUREMENT holds clinical measurements such as grip strength, respiratory function parameters, and electrocardiogram intervals, mapped from FHIR Observation resources coded with LOINC.

OBSERVATION (the OMOP table, distinct from the FHIR resource of the same name) captures patient-reported outcome scores, symptom diary entries, and other structured data points that do not fit into Measurement or Condition domains. QuestionnaireResponse data are decomposed into individual observation records, each linked to the originating instrument and visit.

NOTE stores free-text annotations and clinician comments where they carry clinical significance, with natural language processing applied as a future enhancement if warranted.

FACT_RELATIONSHIP links related records across tables where the study design requires explicit relationships, for example linking an adverse event to its resolution or linking a questionnaire response to the visit during which it was completed.

### DM1-Specific Concepts and Custom Vocabularies

#### The Challenge of Rare Disease Coding

Standard terminologies provide broad coverage of common clinical concepts, but rare diseases often present coding gaps. Myotonic Dystrophy Type 1 involves a constellation of symptoms and assessments that may not be fully represented in SNOMED CT or LOINC, particularly for disease-specific functional scales, specialised neuromuscular assessments, and patient-reported outcomes developed specifically for myotonic dystrophy populations.

#### Approach to Custom Concepts

Where a standard concept does not exist for a DM1-relevant data element, the platform follows a defined process. First, the team searches the existing vocabularies thoroughly, including SNOMED CT pre-coordinated and post-coordinated expressions, LOINC panels, and OMOP custom concepts already available in the community. Second, if no suitable concept is found, a local custom concept is created with a unique identifier drawn from a reserved range, a human-readable name and definition, a mapping to the closest standard concept (even if imprecise) as an interim measure, and a documented rationale for why the standard vocabulary is insufficient.

Custom concepts are stored in the OMOP vocabulary tables as source concepts, clearly distinguished from standard concepts by their vocabulary identifier. They are registered in a project-maintained concept registry that tracks their lifecycle: creation, review, potential submission to the relevant standards body, and eventual replacement by a standard concept if one becomes available.

#### DM1-Specific Instruments

Several instruments commonly used in DM1 research may require custom LOINC panel requests or local concept definitions. Examples include the Myotonic Dystrophy Health Index (MDHI), the DM1-Active questionnaire, disease-specific quality of life instruments, and functional rating scales adapted for myotonic dystrophy. For each instrument, the coding strategy documents the panel structure, the individual question codes, and the scoring algorithm, and submits LOINC panel proposals to the Regenstrief Institute where the instrument has sufficient validation and community adoption to warrant formal inclusion.

### Mapping Workflow: From Source to FHIR to OMOP

#### Source-to-FHIR Mapping

Each data element defined in the study data specification is mapped to a FHIR resource and element. The mapping specifies the target resource type, the target element path, the value type, and the terminology binding (which code system and value set the element draws from). For example, a symptom diary entry recording myotonia severity maps to an Observation resource with a LOINC code identifying the observation type and a SNOMED CT code or ordinal value representing the severity. These mappings are documented in a mapping specification table, reviewed by Clinical Data Management (CDM) and data engineering jointly, and tested by generating sample FHIR bundles from synthetic data.

#### FHIR-to-OMOP Mapping

The ETL pipeline from the operational FHIR-aligned store to the OMOP warehouse implements a second mapping layer. Each FHIR resource type maps to one or more OMOP CDM tables, and each coded element within the resource maps to an OMOP concept through the vocabulary lookup process described earlier. The mapping is designed and documented using OHDSI tools: WhiteRabbit profiles the source data to produce a scan report summarising field values and distributions, and Rabbit in a Hat provides a visual interface for defining source-to-target field mappings. The resulting mapping document is version-controlled and serves as the specification for ETL development.

#### Usagi for Concept Mapping

Where source codes need to be matched to OMOP standard concepts and no direct vocabulary mapping exists, the OHDSI Usagi tool provides a semi-automated approach. Usagi uses text similarity matching to suggest candidate OMOP concepts for each source term, which a domain expert (typically a member of the CDM team or a clinical terminologist) then reviews, accepts, modifies, or rejects. The approved mappings are exported and loaded into the OMOP vocabulary tables as source-to-concept relationships, ensuring they are applied consistently by the ETL pipeline.

### Vocabulary Governance

#### Version Control

All vocabulary artefacts used by the platform are version-controlled. This includes the OMOP vocabulary download (identified by its Athena release date), FHIR value sets and code system definitions, mapping specification documents, custom concept registries, and Usagi mapping files. Version control ensures that any OMOP dataset can be traced back to the exact vocabulary version used at the time of loading, and that changes to coding are deliberate, documented, and reversible.

#### Vocabulary Update Process

Vocabularies are updated on a defined schedule, typically aligned with OMOP vocabulary releases from Athena (approximately quarterly). Each update follows a controlled process: the new vocabulary version is downloaded and loaded into a staging environment, the impact on existing mappings is assessed (new concepts added, deprecated concepts identified, relationship changes), affected ETL pipelines are re-validated, and the update is promoted to production only after CDM and data engineering have confirmed that no unintended data quality regressions occur. The update, its assessment, and its deployment are recorded in the audit trail and the change log.

#### Handling Deprecated and Retired Concepts

When a standard concept is deprecated or retired in a vocabulary update, existing data in the OMOP warehouse that reference the affected concept are not silently changed. Instead, the deprecation is logged, the affected records are flagged for review, and the CDM team decides whether to remap historical data to a replacement concept or to retain the original coding with a clear annotation that the concept is no longer current. This approach preserves data provenance and supports reproducibility of prior analyses.

#### Custom Concept Lifecycle

Custom concepts created for DM1-specific data elements are reviewed at each vocabulary update to determine whether a newly published standard concept now covers the same meaning. If a standard replacement is identified, the custom concept is mapped to it, historical data are considered for remapping, and the custom concept is marked as retired in the project concept registry. The goal is to minimise the number of custom concepts in active use over time, converging toward standard vocabularies as coverage improves.

### Interoperability Considerations

#### EHDS and Cross-Border Exchange

The EHDS envisions a framework in which health data can be shared across European Union member states for both primary care and secondary research purposes. The terminology strategy described here supports this vision by adopting internationally recognised code systems (SNOMED CT, LOINC, ICD, ATC) and by expressing data through FHIR, which is the preferred interoperability format in many EHDS implementation discussions. When the platform shares data through FHIR interfaces with external registries, national health data infrastructures, or EHDS health data access bodies, the coding carried in each resource provides the semantic foundation for meaningful interpretation by the receiving system.

#### Alignment with Rare Disease Registries

Several European rare disease registries and the European Reference Network for Rare Neuromuscular Diseases (EURO-NMD) maintain data sets relevant to DM1. The coding strategy ensures that the platform's data can be mapped to registry-required fields and vocabularies, including Orphanet identifiers, Human Phenotype Ontology (HPO) terms for phenotypic description where relevant, and registry-specific minimum data sets. Where registry alignment requires additional coding that is not part of the primary study data specification, the mapping is documented as a secondary output of the ETL and provisioning layer.

#### CDISC Standards

Where the data collected through this platform are intended to support regulatory submissions, alignment with Clinical Data Interchange Standards Consortium (CDISC) standards may be required. The terminology strategy supports this by ensuring that source variables can be mapped to CDISC Controlled Terminology, that the data specification documents the correspondence between study variables and Study Data Tabulation Model (SDTM) domains, and that the ETL infrastructure can produce CDISC-formatted extracts alongside OMOP datasets. CDISC alignment is treated as a secondary mapping target, not as the primary data model, since the platform's operational and research environments are built around FHIR and OMOP respectively.

### Tooling Summary

The following tools support the terminology and coding strategy throughout the project lifecycle.

Athena, the OHDSI vocabulary repository, provides downloadable vocabulary bundles for loading into the OMOP warehouse. It is the authoritative source for standard concept identifiers, relationships, and mappings used by the ETL pipeline.

WhiteRabbit, an OHDSI data profiling tool, scans the operational data source and produces a report summarising field-level value distributions. This report is the input for mapping design.

Rabbit in a Hat, an OHDSI mapping design tool, provides a visual interface for defining source-to-target field mappings between the operational schema and the OMOP CDM tables. The output is a documented mapping specification.

Usagi, an OHDSI concept mapping tool, assists in matching source terms and local codes to OMOP standard concepts using text similarity and vocabulary lookups. Its output feeds into the source-to-concept mapping tables.

Atlas, the OHDSI cohort definition and analysis platform, allows researchers to define cohorts using standard OMOP concepts. It serves as a key validation tool for confirming that coded data in the OMOP warehouse support the intended research queries.

FHIR validation tooling, such as the HL7 FHIR Validator or equivalent libraries integrated into the backend, ensures that FHIR resources conform to the defined profiles and terminology bindings at the point of data ingestion.

### Document Control

This document is version-controlled alongside the project's other governance and technical artefacts. It is expected to be refined during Months 1 and 2 as the study data specification is finalised, FHIR profiles are defined, and OMOP mapping work progresses through WhiteRabbit profiling and Rabbit in a Hat design sessions.

| Version | Date | Author | Summary of Changes |
|---------|------|--------|--------------------|
| 0.1 | 2026-03-01 | Clinical Data Management | Initial draft covering terminology selection, FHIR profiles, OMOP mapping strategy, and vocabulary governance |
