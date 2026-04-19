# Decision 026: Repository Structure

**Status:** Decided

**Category:** Stack Foundations

**Question:** Do frontend and backend live in one repository or separate repositories, and what workspace tooling manages them?

**Decision:** Monorepo with multiple packages, managed by pnpm workspaces and Turborepo. Structure: `apps/web` (frontend), `apps/api` (backend), and `packages/*` for shared code (validation schemas, TypeScript types, i18n keys as needed).

**Rationale:** TaskFlow has a real API boundary that may eventually be published (Decision 013), but it also has code that legitimately belongs to both sides — validation schemas (Decision 042) and shared types. A multi-package monorepo captures those shared-code benefits without the publish-a-package friction of separate repositories. Turborepo handles build orchestration and caching; pnpm workspaces handle dependency graph. Atomic cross-stack PRs stay possible while layer separation is clear in the directory structure. This assumes a predominantly TypeScript stack (Decisions 027/028).
