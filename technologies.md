## Technology Choices for the DM1 Prospective Data Platform

### Why free and open source software is ideal here

For a platform handling sensitive health and research data, free and open source software offers several advantages. It allows institutions to inspect and understand what the software is doing, which supports trust, independent security review, and alignment with internal policies and regulatory expectations. It avoids lock-in to any single vendor or cloud, so hospitals and research organizations can host the system in their own infrastructure, move between providers, or collaborate across sites without renegotiating proprietary licensing for every deployment. Open source ecosystems around FHIR, OMOP, and data science are already strong, which means the platform can adopt widely used standards, tools, and vocabularies rather than inventing its own formats. Finally, a FOSS base makes it easier to share components with the broader community, improve them collaboratively, and keep costs predictable over the life of a long-running study or registry.

Designing this platform then becomes a matter of selecting specific open source technologies that can be deployed and controlled locally by institutions if desired, and that integrate well with standards such as FHIR and OMOP CDM while meeting GDPR and future EHDS expectations. The goal is to choose components that are mature and interoperable, while giving you precise control over where data live and how they move through operational and research workflows.

### Mobile application

#### Cross-platform framework choice

For the patient-facing mobile application targeting individuals with Myotonic Dystrophy Type 1, a cross-platform approach makes sense in order to support both Android and iOS without duplicating effort. Two realistic candidates are Flutter and React Native. Flutter, based on the Dart language, offers excellent performance, a coherent UI toolkit, and good support for accessibility and custom component design, which can be important for DM1 users who may need larger controls and simplified navigation. React Native, based on JavaScript and TypeScript, fits very well when the team already has strong web development experience and wants to share domain models and validation logic with web frontends.

#### Offline-first storage and local security

In both frameworks, the app should be designed as offline-first: data are stored locally on the device in an embedded database such as SQLite, using libraries like Drift or sqflite in Flutter, or a mature SQLite binding in React Native. Sensitive values and encryption keys should be protected using the platform keychains or secure storage libraries, so that if a device is lost, the risk of data exposure is minimized while still allowing background synchronization when connectivity is available.

### Backend API and data store

#### Language and framework options

The backend API and application logic can be implemented using either TypeScript or Python, both of which have rich ecosystems and strong support for modern, testable APIs. A TypeScript stack based on a framework such as NestJS or a lighter alternative like Fastify provides strong typing, decorators to define routes and validation, and the ability to enforce strict data contracts across services. A Python stack using FastAPI offers similar advantages in terms of explicit type hints, asynchronous request handling, and clear dependency injection patterns.

#### Primary operational database

In both approaches, the use of a relational database such as PostgreSQL as the primary data store is recommended. PostgreSQL is mature, open source, widely supported in healthcare environments, and flexible enough to store both structured clinical data and semi-structured JSON payloads while still enabling robust transactional guarantees for audit trails and data locks.

### FHIR interoperability layer

#### Facade-based FHIR interface

Interoperability with clinical systems and adherence to FHIR can be handled via a dedicated FHIR layer rather than a monolithic FHIR server. One approach is to implement a FHIR facade in the chosen backend framework, using FHIR libraries for validation and resource modeling, such as Python packages that provide FHIR resource classes or TypeScript libraries that ship with FHIR schemas.

#### Internal model and mappings

Internally, the system stores data in a schema tailored to research and ePRO use cases, but exposes and consumes FHIR resources at the boundaries. This keeps the operational data model focused on the study and patient workflows while still allowing standards-based exchange with external EHRs, registries, or national health data infrastructures. Mapping between internal structures and FHIR resources should be explicit, version-controlled, and tested, since it later forms the basis for ETL to OMOP as well.

### Identity, access management, and consent

#### Centralized IAM

Identity and access management should be externalized into a dedicated, open source IAM solution rather than being handwritten inside the application. A practical choice here is Keycloak, which implements OpenID Connect and OAuth 2.0, supports roles, groups, and attributes, and integrates well with both web and mobile clients. Keycloak can act as the single source of truth for user authentication and coarse-grained role assignments such as patient, caregiver, clinical researcher, data manager, data engineer, auditor, and administrator. The application services then interpret these roles and additional claims, enforcing more fine-grained permissions in line with the RBAC model defined for the project.

#### Consent linkage and auditability

Keycloak also supports features that are useful for GDPR and EHDS, such as account management interfaces for users, multi-factor authentication and policies for password strength, and the ability to log and export authentication events for audit. Consent records themselves can live in the application database but must be reflected in IAM policies and claims so that consent status directly influences which data a user or service may access.

### Research environment and OMOP CDM

#### Dedicated OMOP warehouse

For the research environment, the recommended approach is to maintain a separate PostgreSQL instance implementing the OMOP Common Data Model. This instance is populated via ETL pipelines that extract data from the operational clinical store, transform them into OMOP tables and vocabularies, and load them into the warehouse. The OHDSI ecosystem provides several free and open source tools for this purpose. WhiteRabbit and Rabbit in a Hat can help profile source data and design mappings, while ETL logic itself can be implemented using technologies that the team is comfortable with, such as dbt, Python scripts, or R-based pipelines relying on packages like DBI and dplyr.

#### OHDSI tooling for researchers

On top of the OMOP database, OHDSI WebAPI and Atlas can be deployed to provide cohort definition, characterization, and study design capabilities, giving clinical researchers a powerful environment without exposing them to raw database internals and while keeping data access under governance rules.

### De-identification and data provisioning

#### Orchestrated pipelines

The de-identification and data provisioning layer is best implemented as a set of reproducible pipelines that sit between the operational database and the OMOP warehouse. Technologies like Apache Airflow or Prefect are appropriate for orchestrating workflows, tracking runs, and managing dependencies between tasks such as pseudonymization, masking, generalization, and computation of risk metrics. Each pipeline should be version-controlled and parameterized, so that a particular research extract can be traced back to the exact logic, vocabulary versions, and source data ranges used.

#### Governance and access control

For GDPR and EHDS, this layer is where data access requests are translated into concrete extracts and where technical enforcement of approved scopes, purposes, and retention schedules takes place, in alignment with decisions made by data access committees or governance boards.

### Observability, auditing, and compliance monitoring

#### Metrics and technical logging

Observability, auditing, and compliance monitoring require their own set of tools. For metrics and health monitoring, Prometheus combined with Grafana is a widely adopted, fully open source choice that can capture system metrics, custom application metrics, and business indicators such as the rate of completed questionnaires or failed logins. For logs, it is important to distinguish between technical logs and audit logs. Technical logs, containing stack traces and performance information, can be collected and indexed using stacks like Loki or OpenSearch.

#### Audit trail and investigations

Audit logs that record user actions on data and configurations should be stored in append-only tables in PostgreSQL or another tamper-evident store, with strict access controls. Correlating identifiers such as request IDs and timestamps across these systems allows efficient root cause analysis and, more importantly for clinical research, reconstruction of data histories and user actions during audits and inspections.

### Deployment and local-first operation

#### Containerization and orchestration

To support a local-first deployment model for institutions, the entire backend stack should be packaged as containers and orchestrated in a way that does not depend on a single cloud vendor. Docker or Podman images for the API services, PostgreSQL, Keycloak, OMOP warehouse, OHDSI tools, and observability stack can be composed with Docker Compose for small-scale deployments or Kubernetes for larger or more complex environments.

#### Institutional control and interoperability

This container-based approach allows hospitals or research organizations to host the system within their own infrastructure, aligning with data residency and governance requirements, while still reusing the same free and open source components across installations. Combined with an offline-capable mobile app, this yields a platform where data are always under the control of the responsible institution, but still interoperable through FHIR, analyzable via OMOP, and aligned with European data protection expectations.

