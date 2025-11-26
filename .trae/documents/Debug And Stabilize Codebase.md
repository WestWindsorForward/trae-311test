## Scope & Goal
- Debug and stabilize the "Township Request Management System" on branch `cursor/deploy-township-request-management-system-158c`, fix runtime/test failures, and verify end-to-end.

## Assumptions
- The branch is available in this repo; I will switch to it locally.
- I will only propose changes until you request a commit.

## Branch-Specific Discovery
- Check out the branch and survey project structure (monorepo vs single app).
- Identify the app type (Next.js/React, Node API, Python, etc.) via key files like `package.json`, `next.config.js`, `pyproject.toml`.
- Locate domain modules for request creation/approval/status workflows and related API routes.
- Find logging/error-handling utilities and config/env management.

## Reproduce Failures
- Install dependencies using the detected package manager.
- Run unit tests and any e2e/integration tests tied to request management flows.
- Start the dev server and manually exercise core flows: create request, approve/deny, list/filter/search, attachment upload, notifications.
- Capture stack traces, network errors, and backend responses.

## Diagnose Root Causes
- Trace failing paths to specific modules/functions with breakpoints or targeted logging.
- Common focus areas: validation schemas, state management, API contracts, authentication/authorization, pagination/sorting, timezones, and file upload handling.
- Inspect error boundaries and propagation to ensure useful user feedback.

## Implement Fixes
- Apply minimal, idiomatic changes consistent with existing patterns.
- Correct data shapes and lifecycle, add defensive checks, fix race conditions or misconfigured env.
- Improve error messages where helpful without leaking sensitive details.

## Tests & Hardening
- Add/update unit and integration tests covering the fixed flows.
- Ensure deterministic tests; mock external services (email, storage, auth) where needed.
- Add lint/type checks to prevent regressions if the toolchain supports it.

## Verification
- Run the full test suite and verify green.
- Launch the dev server and validate the full create→approve→list flows.
- Provide a preview link for manual validation when applicable.

## Deliverables
- Root-cause analysis and fix summary.
- Proposed code changes with file references (e.g., `src/requests/service.ts:87`).
- New/updated tests demonstrating resolution.
- Follow-up recommendations for resilience and maintainability.

## Next Step
- After you confirm, I will check out `cursor/deploy-township-request-management-system-158c`, reproduce issues, and begin the fix immediately.