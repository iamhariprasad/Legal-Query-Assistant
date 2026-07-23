# AI-Powered Legal Query Assistant: Remaining Implementation Script

## Current Status

The backend API, Docker services, authentication, Indian Kanoon search, RAG query endpoint, PostgreSQL migration, Redis service, and Ollama integration have been brought up and tested through Swagger/API calls.

However, the product is not yet frontend-complete. The current browser UI still feels incomplete because several pages are mostly shells, the chat experience is not polished, and the user cannot clearly see whether backend data is being persisted or cached.

This file documents the remaining work required before the project should be considered production-quality from a user-facing and resume-ready perspective.

## Major Problems To Fix

### 0. API Reliability Must Be Fixed And Verified

Some APIs have worked through Swagger after patches, but the project still needs a proper API hardening pass. No frontend page should depend on an API that has not been tested with valid auth, invalid auth, validation errors, dependency failures, and happy-path data.

Required work:

- Test every endpoint from Swagger, frontend, and automated tests.
- Fix any API that returns incorrect `500` errors for expected user/dependency problems.
- Convert expected failures into clear `4xx` or structured `5xx` responses.
- Ensure `/api/v1/auth/register` handles duplicate emails cleanly.
- Ensure `/api/v1/auth/login` supports both frontend JSON login and Swagger form login.
- Ensure `/api/v1/auth/me` returns the active user reliably.
- Ensure `/api/v1/search/legal` works with Indian Kanoon and returns clear errors if the API token is invalid.
- Ensure `/api/v1/chat/query` works end to end and does not silently fail in the frontend.
- Ensure `/api/v1/chat/stream` actually streams useful status/tokens or is clearly implemented with guarded streaming semantics.
- Ensure `/api/v1/chat/history` returns persisted chat history for the logged-in user.
- Ensure `/api/v1/documents/{document_id}` and `/api/v1/documents/index` work with real Indian Kanoon document IDs.
- Ensure `/api/v1/feedback` works from the frontend and stores feedback.
- Ensure `/api/v1/evaluation/results` returns useful dashboard data.
- Ensure `/api/v1/evaluation/run` is admin-only and works.
- Ensure `/api/v1/admin/metrics` is admin-only and returns real operational metrics.
- Ensure `/api/v1/admin/guardrails` is admin-only and returns real guardrail logs.
- Add API integration tests for all routes.
- Add regression tests for previously seen failures: CORS parsing, Alembic async migration, bcrypt registration, Swagger login, Indian Kanoon `found` string parsing, and Ollama URL protocol.

### 1. Frontend Needs Major Improvement

The current frontend only has basic navigation and partial pages. Several sidebar pages exist by name, but they do not yet provide a complete product experience.

Required work:

- Build a polished ChatGPT-like chat interface.
- Add complete login/register/logout flows.
- Show authenticated user state clearly.
- Add proper loading states for long-running RAG requests.
- Add visible error states for failed backend calls.
- Show confidence score, refusal status, citations, and source snippets in the chat UI.
- Add a source drawer that actually opens from each answer.
- Add streaming-style answer rendering or token animation.
- Improve empty states for Chat, History, Search, Evaluation, Admin, and Settings.
- Make the UI responsive and professional on desktop and mobile.
- Add frontend tests for auth, chat, history, search, and dashboards.

### 1.1. New User Flow Must Make Sense

A new user should be able to open the application and understand exactly what to do without Swagger.

Required work:

- Add a dedicated Auth page or modal for login/register.
- Let a new user create an account from the frontend.
- Let an existing user login from the frontend.
- After login, route the user to Chat.
- Show the logged-in user name/email in the navbar or sidebar.
- Add logout.
- Persist the JWT token across refresh.
- Clear invalid/expired tokens automatically.
- Never require a user to manually copy tokens from Swagger.
- Add friendly messages for duplicate email, wrong password, expired session, and backend unavailable states.

### 1.2. Admin Must Not Be Mixed With Normal User UX

The Admin page currently appears in the same sidebar for every user. That does not make product sense. Admin functionality must be role-gated and visually separated from normal user workflows.

Required work:

- Hide Admin navigation for non-admin users.
- Make `/admin` route inaccessible for normal users.
- Add backend role checks to every admin endpoint.
- Add an admin-only layout or clearly separated Admin section.
- Provide a way to create the first admin user through a seed command or documented database command.
- Show a proper `403`/not-authorized UI when a non-admin attempts admin access.
- Do not place admin controls on the user login page.
- Do not show operational controls to normal legal query users.
- Add tests proving normal users cannot access admin APIs or admin UI.

### 2. Frontend Must Be Fully Connected To Backend

Swagger confirms the backend works, but the frontend must prove the same workflows without using Swagger manually.

Required work:

- Connect Chat page to `/api/v1/chat/query`.
- Connect Search page to `/api/v1/search/legal`.
- Connect History page to `/api/v1/chat/history`.
- Connect Evaluation dashboard to `/api/v1/evaluation/results`.
- Connect Admin dashboard to `/api/v1/admin/metrics` and `/api/v1/admin/guardrails`.
- Connect Settings page to real local settings/status where possible.
- Persist JWT auth token safely in frontend state/storage.
- Add automatic token handling in Axios.
- Add unauthorized handling and redirect/show login when token is missing or expired.
- Add user-visible backend/API error messages.
- Add a frontend integration checklist for every sidebar page.
- Remove or finish any page that only contains labels without working data.

Every visible page must either:

- Perform a real backend-backed workflow, or
- Be removed until it is implemented.

### 3. PostgreSQL Persistence Must Be Proven In UI

The database schema and migration exist, and chat history is inserted from the backend. But the frontend does not yet make persistence obvious to the user.

Required work:

- Confirm every successful chat response is stored in `chat_history`.
- Show persisted chat history in the History page.
- Show created timestamp, query, answer, confidence, refusal reason, and citations.
- Add feedback submission and store feedback in PostgreSQL.
- Add admin-visible guardrail logs from PostgreSQL.
- Add admin-visible evaluation results from PostgreSQL.
- Add a simple database status indicator in Admin or Settings.
- Add integration tests proving chat history survives backend restart.
- Add a manual verification flow: ask a question, refresh browser, reopen History, confirm the same answer is still present.
- Add API tests proving persisted chat records are scoped to the authenticated user.

### 4. Redis Usage Must Be Visible And Verified

Redis is running and the backend contains cache code, but the UI and diagnostics do not make Redis behavior obvious.

Required work:

- Verify Indian Kanoon search responses are cached in Redis.
- Show `cache_hit` in Search page results.
- Add backend metric for Redis cache hits/misses.
- Add Admin dashboard cards for Redis status, cache hits, cache misses, and average cached response latency.
- Add tests for cache set/get behavior.
- Add logs that clearly show when Redis is used.
- Add graceful fallback if Redis is unavailable.
- Add a manual verification flow: run the same search twice and show the second response has `cache_hit: true`.
- Add Admin dashboard display for cache hit/miss count.

### 5. Chat UX Is Not Production-Ready Yet

The chat page must feel like the primary product, not a thin API tester.

Required work:

- Keep the input fixed at the bottom.
- Render user and assistant messages clearly.
- Disable send button while request is running.
- Show long-running model state such as searching, retrieving, reranking, generating, verifying citations, and applying guardrails.
- Show citation cards below assistant answers.
- Allow opening each citation URL.
- Add copy answer button.
- Add retry button.
- Add clear chat button.
- Add feedback buttons for each answer.
- Add refusal explanation when guardrails block an answer.
- Display backend progress states instead of leaving users staring at one user message.
- Ensure no request can appear to hang without status.
- Add timeout messaging for slow local Ollama responses.

### 6. Citation Display Must Be Normalized

The backend can return citations, but generated answer text may refer to citation numbers that do not visually match the citation cards.

Required work:

- Normalize answer citation markers to match returned citation cards.
- Ensure citation numbers are sequential.
- Ensure every displayed citation marker maps to an actual citation card.
- Add tests for citation verification and citation rendering.
- Refuse responses when citation markers cannot be mapped.

### 7. Performance Needs Improvement

The current RAG request can take around one minute or longer on CPU.

Required work:

- Cache fetched Indian Kanoon documents.
- Cache document chunks and embeddings.
- Avoid re-indexing the same document chunks repeatedly.
- Limit document fetches for initial queries.
- Add configurable top-k retrieval settings.
- Add background indexing for large documents.
- Add progress updates during long requests.
- Add Locust run documentation and generated reports.

### 8. Evaluation Dashboard Needs Real Product Polish

The evaluation dataset exists, but dashboard and evaluation workflows need to be more useful.

Required work:

- Seed or run all 100 labeled legal queries.
- Store evaluation results in PostgreSQL.
- Display aggregate metrics in the frontend.
- Show per-query pass/fail status.
- Show citation accuracy, faithfulness, hallucination rate, precision, recall, latency, and context recall.
- Add filters for refused, failed, unsafe, and low-confidence cases.
- Add downloadable evaluation report.

### 9. Admin Dashboard Needs Real Operations Data

The Admin page must become useful for observing the system.

Required work:

- Show total chats.
- Show total refusals.
- Show average confidence.
- Show average latency.
- Show Redis cache hit rate.
- Show Indian Kanoon request count.
- Show guardrail trigger breakdown.
- Show recent failed requests.
- Show model name and Ollama connectivity.
- Show PostgreSQL and Redis health.

### 10. Documentation Must Reflect Actual Usage

The README and docs should be updated after frontend/backend behavior is finalized.

Required work:

- Add exact Windows + Docker + Ollama setup instructions.
- Document `host.docker.internal` Ollama configuration.
- Document Indian Kanoon token setup.
- Document first-run model downloads and expected latency.
- Document Swagger auth and frontend auth.
- Document database migration.
- Document troubleshooting for 401, 405, 500, 502, and slow model responses.
- Add screenshots after UI improvements.

### 11. Product Must Feel Coherent

The application must make sense to a first-time user. It should not look like a set of disconnected route names.

Required work:

- Define user roles: normal user and admin.
- Define normal user journey: register/login, ask, read answer, inspect citations, give feedback, view history.
- Define admin journey: login as admin, inspect metrics, inspect guardrails, run evaluation, view system health.
- Make the sidebar role-aware.
- Make every page have a clear purpose.
- Keep all data flows backend-backed.
- Remove dead UI.
- Add loading, empty, error, and success states to every page.
- Make the frontend visually polished enough for a resume/demo project.

## Immediate Next Implementation Order

1. Fix frontend authentication UX completely.
2. Separate admin UX from normal user UX.
3. Hide Admin for non-admin users and enforce backend admin-only access.
4. Make Chat page fully usable and visually complete.
5. Make History page show persisted PostgreSQL chat records.
6. Make Search page show real Indian Kanoon results and Redis cache hit status.
7. Make Admin page show PostgreSQL, Redis, guardrail, and system metrics.
8. Normalize citation numbering between answer text and citation cards.
9. Add visible progress states for long RAG requests.
10. Test and fix every API endpoint.
11. Add integration tests for frontend-to-backend workflows.
12. Add Redis cache verification tests.
13. Update README and screenshots.

## Acceptance Criteria

The project should not be called frontend-complete until:

- A user can register, login, ask a legal question, receive a cited answer, view sources, and revisit the answer in History entirely from the frontend.
- The frontend clearly shows when an answer is refused and why.
- The Search page returns real Indian Kanoon results from the frontend.
- The History page proves PostgreSQL persistence.
- The Admin dashboard proves Redis, PostgreSQL, guardrails, metrics, and evaluation are active.
- Admin is role-gated and not shown as a normal user feature.
- Every API is tested and returns correct structured responses.
- No sidebar page is a decorative placeholder.
- The app remains usable during long local Ollama responses.
- Tests cover the core frontend and backend workflows.
