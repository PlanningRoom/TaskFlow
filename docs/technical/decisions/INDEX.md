# TaskFlow Technical Decision Index

Architectural Decision Records (ADRs) for TaskFlow. Decisions are grouped in the order they should be made — earlier groups constrain later ones. Inherited decisions (001–025) are already fixed by the business, product, and design phases.

## Inherited Constraints (Decided)

### Platform & Topology

| # | Decision | Status |
|---|----------|--------|
| 001 | [Application Delivery Model](001-application-delivery-model.md) | Decided |
| 002 | [Deployment Model](002-deployment-model.md) | Decided |
| 003 | [Tenancy Architecture](003-tenancy-architecture.md) | Decided |
| 004 | [Data Residency Scope](004-data-residency-scope.md) | Decided |
| 005 | [Responsive Web Strategy](005-responsive-web-strategy.md) | Decided |
| 006 | [Offline Support](006-offline-support.md) | Decided |
| 007 | [Real-Time Update Requirement](007-real-time-update-requirement.md) | Decided |
| 008 | [Concurrent Edit Conflict Resolution](008-concurrent-edit-conflict-resolution.md) | Decided |
| 009 | [Deep-Linkable Resources](009-deep-linkable-resources.md) | Decided |

### Auth & Identity

| # | Decision | Status |
|---|----------|--------|
| 010 | [Authentication Method](010-authentication-method.md) | Decided |
| 011 | [Account Onboarding Model](011-account-onboarding-model.md) | Decided |

### External Surface

| # | Decision | Status |
|---|----------|--------|
| 012 | [External Integrations](012-external-integrations.md) | Decided |
| 013 | [Public API Exposure](013-public-api-exposure.md) | Decided |

### Content Model

| # | Decision | Status |
|---|----------|--------|
| 014 | [Rich Content Format](014-rich-content-format.md) | Decided |
| 015 | [File Attachment Support](015-file-attachment-support.md) | Decided |
| 016 | [Time & Time Zone Handling](016-time-and-time-zone-handling.md) | Decided |

### Cross-Cutting Concerns

| # | Decision | Status |
|---|----------|--------|
| 017 | [Accessibility Target](017-accessibility-target.md) | Decided |
| 018 | [Internationalization Readiness](018-internationalization-readiness.md) | Decided |
| 019 | [Right-to-Left Readiness](019-right-to-left-readiness.md) | Decided |
| 020 | [Locale-Specific Formatting](020-locale-specific-formatting.md) | Decided |
| 021 | [Privacy & Data Deletion Model](021-privacy-and-data-deletion-model.md) | Decided |

### Design System Foundations

| # | Decision | Status |
|---|----------|--------|
| 022 | [Design Token Layer](022-design-token-layer.md) | Decided |
| 023 | [Typography System](023-typography-system.md) | Decided |
| 024 | [Icon System](024-icon-system.md) | Decided |
| 025 | [Motion & Reduced-Motion Support](025-motion-and-reduced-motion-support.md) | Decided |

---

## Architectural Decisions (All Decided)

### Stack Foundations

| # | Decision | Status |
|---|----------|--------|
| 026 | [Repository Structure](026-repository-structure.md) | Decided |
| 027 | [Frontend Language & Type System](027-frontend-language-and-type-system.md) | Decided |
| 028 | [Backend Language](028-backend-language.md) | Decided |
| 029 | [Frontend Framework](029-frontend-framework.md) | Decided |
| 030 | [Frontend Rendering Strategy](030-frontend-rendering-strategy.md) | Decided |
| 031 | [Frontend Build Tooling](031-frontend-build-tooling.md) | Decided |
| 032 | [Backend Framework](032-backend-framework.md) | Decided |
| 033 | [Primary Database Engine](033-primary-database-engine.md) | Decided |
| 034 | [Database Access Layer](034-database-access-layer.md) | Decided |
| 035 | [Database Migration Tooling](035-database-migration-tooling.md) | Decided |
| 036 | [Hosting Platform](036-hosting-platform.md) | Decided |
| 037 | [Cloud Region Selection](037-cloud-region-selection.md) | Decided |
| 038 | [Containerization Strategy](038-containerization-strategy.md) | Decided |
| 039 | [Local Development Environment](039-local-development-environment.md) | Decided |

### API & Real-Time

| # | Decision | Status |
|---|----------|--------|
| 040 | [API Style](040-api-style.md) | Decided |
| 041 | [API Versioning Strategy](041-api-versioning-strategy.md) | Decided |
| 042 | [Request/Response Validation](042-request-response-validation.md) | Decided |
| 043 | [Error Response Contract](043-error-response-contract.md) | Decided |
| 044 | [Real-Time Transport Protocol](044-real-time-transport-protocol.md) | Decided |
| 045 | [Real-Time Infrastructure](045-real-time-infrastructure.md) | Decided |
| 046 | [Optimistic UI Policy](046-optimistic-ui-policy.md) | Decided |

### Auth Implementation

| # | Decision | Status |
|---|----------|--------|
| 047 | [Session Strategy](047-session-strategy.md) | Decided |
| 048 | [Password Hashing Algorithm](048-password-hashing-algorithm.md) | Decided |
| 049 | [Password Reset Flow](049-password-reset-flow.md) | Decided |
| 050 | [Auth Library Choice](050-auth-library-choice.md) | Decided |
| 051 | [CSRF Protection Strategy](051-csrf-protection-strategy.md) | Decided |
| 052 | [Rate Limiting Strategy](052-rate-limiting-strategy.md) | Decided |

### Client Architecture

| # | Decision | Status |
|---|----------|--------|
| 053 | [Server State Management](053-server-state-management.md) | Decided |
| 054 | [Client State Management](054-client-state-management.md) | Decided |
| 055 | [Routing Library](055-routing-library.md) | Decided |
| 056 | [Form Handling Library](056-form-handling-library.md) | Decided |
| 057 | [CSS Strategy](057-css-strategy.md) | Decided |
| 058 | [Component Primitives](058-component-primitives.md) | Decided |
| 059 | [Drag-and-Drop Library](059-drag-and-drop-library.md) | Decided |
| 060 | [Markdown Rendering & Sanitization](060-markdown-rendering-and-sanitization.md) | Decided |
| 061 | [Internationalization Library](061-internationalization-library.md) | Decided |

### Data Layer

| # | Decision | Status |
|---|----------|--------|
| 062 | [Full-Text Search Implementation](062-full-text-search-implementation.md) | Decided |
| 063 | [Activity Feed Storage Model](063-activity-feed-storage-model.md) | Decided |
| 064 | [Notification Storage Model](064-notification-storage-model.md) | Decided |
| 065 | [Account Deletion & Anonymization Approach](065-account-deletion-and-anonymization-approach.md) | Decided |
| 066 | [Seed Data & Fixtures](066-seed-data-and-fixtures.md) | Decided |

### Supporting Services

| # | Decision | Status |
|---|----------|--------|
| 067 | [Transactional Email Provider](067-transactional-email-provider.md) | Decided |
| 068 | [Cache / Session Store](068-cache-session-store.md) | Decided |
| 069 | [Background Job System](069-background-job-system.md) | Decided |
| 070 | [Notification Dispatch Architecture](070-notification-dispatch-architecture.md) | Decided |

### Ops & Observability

| # | Decision | Status |
|---|----------|--------|
| 071 | [CI/CD Platform](071-ci-cd-platform.md) | Decided |
| 072 | [Environments Topology](072-environments-topology.md) | Decided |
| 073 | [Secrets Management](073-secrets-management.md) | Decided |
| 074 | [Backup & Disaster Recovery](074-backup-and-disaster-recovery.md) | Decided |
| 075 | [Logging, Metrics & Tracing](075-logging-metrics-tracing.md) | Decided |
| 076 | [Error Tracking](076-error-tracking.md) | Decided |
| 077 | [Uptime Monitoring](077-uptime-monitoring.md) | Decided |
| 087 | [Infrastructure as Code](087-infrastructure-as-code.md) | Decided |

### Quality & Workflow

| # | Decision | Status |
|---|----------|--------|
| 078 | [Linting & Formatting](078-linting-and-formatting.md) | Decided |
| 079 | [Unit & Integration Testing](079-unit-and-integration-testing.md) | Decided |
| 080 | [End-to-End Testing](080-end-to-end-testing.md) | Decided |
| 081 | [Accessibility Testing](081-accessibility-testing.md) | Decided |
| 082 | [Pre-Commit Hooks & CI Gates](082-pre-commit-hooks-and-ci-gates.md) | Decided |

### Security Hardening

| # | Decision | Status |
|---|----------|--------|
| 083 | [Content Security Policy & Security Headers](083-content-security-policy-and-security-headers.md) | Decided |
| 084 | [Audit Logging Scope](084-audit-logging-scope.md) | Decided |
| 085 | [Data Encryption Policy](085-data-encryption-policy.md) | Decided |
| 086 | [Dependency Vulnerability Scanning](086-dependency-vulnerability-scanning.md) | Decided |
