# WildGuard Kenya Implementation Guide

This document explains how to turn `Master.md` into a working, credible prototype. Build the product as a modular monolith: one Django backend, one React frontend, and one PostgreSQL/PostGIS database. Keep boundaries clear inside the applications so integrations or services can be extracted later if needed.

## 1. Definition Of Done

The prototype is ready for demonstration when a user can:

1. Sign in with a role-appropriate account.
2. Submit an elephant incident with a location, severity, description, and optional evidence.
3. See the incident on the map with an explainable risk score.
4. Trigger and view a critical alert.
5. Have a ranger accept, dispatch, respond to, and resolve the incident.
6. Review the complete status timeline.
7. See the incident reflected in analytics and hotspot views.
8. Run the complete flow using clearly labeled fictional demo data.

Every completed phase must leave the application runnable and tested.

## 2. Recommended Build Order

### Phase 0: Confirm Product Boundaries

Before writing code, record these decisions in the project documentation:

- WildGuard complements existing conservation systems; it does not replace or impersonate them.
- The first release is Kenya-focused but should use configurable counties, communities, species, and scoring rules.
- Demo data is fictional and must be labeled `DEMO DATA - NOT LIVE FIELD DATA`.
- Reporter identity and contact information are private by default.
- The initial risk and hotspot calculations are explainable rules, not machine learning.

**Output:** product requirements, architecture notes, limitations, and a short boardroom demo script.

### Phase 1: Bootstrap Infrastructure

Create the repository layout, Docker Compose services, environment configuration, and local developer commands.

Recommended services:

- `db`: PostgreSQL with PostGIS.
- `backend`: Django and Django REST Framework.
- `frontend`: React, TypeScript, and Vite.

Set up:

- Django settings split by environment or a clearly documented environment-based configuration.
- PostgreSQL connection through environment variables.
- CORS and JWT configuration.
- Health endpoints for the backend and database connectivity.
- Formatting, linting, and test commands.

**Gate:** a clean-machine setup can start the services, apply migrations, and return a successful health response.

### Phase 2: Domain Model And Authentication

Implement the core Django apps around ownership boundaries rather than one oversized app:

- `accounts`: users, roles, authentication, permissions.
- `communities`: communities and geographic metadata.
- `incidents`: incidents, evidence, status history, and notifications.
- `response`: ranger responses, assignments, dispatch, and resolution.
- `risk`: risk assessments and scoring rules.
- `analytics`: aggregates and hotspots.
- `integrations`: provider interfaces and future adapters.

Use a custom user model before the first migration. Add role-based API permissions and serializers. Store incident coordinates in a PostGIS geographic field, such as `PointField`, rather than only in numeric or string columns.

**Gate:** users can obtain JWT tokens, role restrictions work, and migrations recreate the database from an empty volume.

### Phase 3: Incident Reporting

Build the smallest complete reporting flow first:

- Species, animal count, severity, description, event time, and location.
- Manual map location selection plus browser geolocation where permitted.
- Evidence upload with file type and size validation.
- Optional contact details stored separately from public incident fields.
- Server-side validation for every field.

Expose the incident create, list, detail, and update endpoints. Add status history creation whenever the status changes; do not let clients edit history directly.

**Gate:** a community member can submit a report from a mobile-sized screen, and a supervisor can inspect the resulting incident and its initial timeline entry.

### Phase 4: Map And Command Center

Create the operational dashboard around real API data rather than hard-coded cards.

Implement:

- Mapbox map with incident markers and hotspot layers.
- Risk-colored markers: low, moderate, high, and critical.
- Marker click details.
- Filters for species, risk, status, date, county, and community.
- Summary metrics for active, critical, verified, unresolved, and recent incidents.

Keep public map responses free of reporter contact information. Use pagination for lists and a map-specific endpoint for geographic results.

**Gate:** filters change both the map and supporting totals, and a user can reach an incident detail view from a marker.

### Phase 5: HWC Risk Engine

Implement the scoring engine as a small, isolated Python module with typed inputs and outputs. Keep rules configurable and return both the final score and a list of reasons.

Suggested calculation:

- Species danger factor: configurable points.
- Settlement proximity under 2 km: `+25`.
- Night-time event: `+10`.
- Multiple animals: `+10`.
- Previous nearby incidents: `+15`.
- Crop or property damage: `+15`.
- Clamp the result to `0..100`.

Map the score to the four documented risk levels. Save a risk assessment record so later rule changes do not erase what was calculated for an earlier incident.

**Gate:** unit tests cover each factor, the score cap, risk boundaries, and human-readable reasons. The UI shows why the score was produced.

### Phase 6: Verification And Ranger Response

Implement the workflow as controlled state transitions, not arbitrary status edits.

Recommended transition rules:

- `REPORTED -> UNDER_REVIEW` by a reviewer.
- `UNDER_REVIEW -> VERIFIED` or `REJECTED` by an authorized reviewer.
- `VERIFIED -> DISPATCHED` by a supervisor.
- `DISPATCHED -> RESPONDING` by the assigned ranger.
- `RESPONDING -> RESOLVED` by the ranger.
- `RESOLVED -> CLOSED` by an authorized reviewer.

For each transition, record actor, timestamp, old status, new status, and optional notes. Use database transactions for transitions, assignments, and alert creation.

**Gate:** unauthorized users cannot advance an incident, invalid transitions return a clear API error, and the ranger can complete the full demo workflow.

### Phase 7: Alerts And Notifications

Generate an internal alert when a new or re-scored incident is critical. Make alert creation idempotent so retries do not create duplicates.

Store notification delivery as an internal event or notification record. Define adapter interfaces for SMS, WhatsApp, email, push, and USSD, but leave providers unimplemented until credentials, consent, and delivery tests exist.

**Gate:** a critical demo incident creates one visible high-priority dashboard alert, while the product does not claim that an external message was sent.

### Phase 8: Analytics And Hotspots

Start with database-backed aggregates and predictable queries:

- Incidents over time.
- Incidents by species, county, and community.
- Risk distribution.
- Response time and resolution rate.
- Time-of-day patterns.
- Unresolved incidents.

For hotspots, choose a simple documented approach such as grid bucketing or a radius-based count. Store the algorithm version or parameters used to produce each hotspot. Show count, dominant species, average risk, recent trend, and priority.

**Gate:** changing the date filter changes charts and hotspot results, and empty data states are handled cleanly.

### Phase 9: Executive View

Add a separate executive route using the same backend aggregates. Focus on decisions rather than operational controls:

- Where incidents are concentrated.
- Which species and communities are most affected.
- Current critical incidents.
- Response performance.
- Emerging hotspots.
- Direction of the recent trend.

Use restrained, accessible visual hierarchy. Do not invent statistics when the database is empty; show an explicit empty state.

**Gate:** an executive can understand current risk and response performance without opening individual technical records.

### Phase 10: Demo Data And Script

Create a repeatable Django seed command that is safe to rerun. It should create:

- At least 5 fictional communities.
- At least 50 incidents across several species and risk levels.
- Ranger users, responses, alerts, and historical status changes.
- Hotspots derived from the seeded incidents.
- One clearly recognizable elephant incident near farmland.

Use deterministic dates and coordinates so screenshots and walkthroughs remain stable. Add a reset-and-seed command for local demonstrations only.

The live walkthrough should be:

1. Log in as a community member.
2. Submit the elephant report.
3. Open the Command Center.
4. Explain the score and reasons.
5. Open the critical alert.
6. Log in as a ranger and accept the assignment.
7. Dispatch, respond, and resolve it.
8. Show the timeline and updated analytics.

**Gate:** a fresh local environment can be prepared with documented commands and the walkthrough completes without manual database editing.

### Phase 11: Security, Testing, And Documentation

Add focused tests at each boundary:

- Risk engine unit tests.
- Model and transition tests.
- API permission and validation tests.
- Upload validation tests.
- Frontend tests for reporting, filtering, and response controls.
- One end-to-end test for the boardroom scenario where practical.

Review before release:

- No secrets committed; `.env.example` contains names, not values.
- JWT expiry and refresh behavior are documented.
- CORS is restricted outside local development.
- Rate limiting is documented and applied at the appropriate edge.
- Audit logs do not leak private reporter data.
- API schema and README match the implementation.
- Integrations are labeled as planned unless implemented and tested.

**Gate:** tests pass, the application starts from a clean setup, and the README explains installation, demo data, APIs, limitations, and future integrations.

## 3. Suggested API Shape

Keep endpoints resource-oriented and use explicit action endpoints for workflow transitions:

```text
POST   /api/auth/token/
POST   /api/auth/refresh/
GET    /api/incidents/
POST   /api/incidents/
GET    /api/incidents/{id}/
PATCH  /api/incidents/{id}/
POST   /api/incidents/{id}/verify/
POST   /api/incidents/{id}/dispatch/
POST   /api/incidents/{id}/resolve/
GET    /api/incidents/map/
GET    /api/analytics/
GET    /api/hotspots/
GET    /api/alerts/
```

Use serializers for validation, permission classes for role checks, and service functions for transitions and risk calculations. Keep views thin and make service behavior easy to unit test.

## 4. Working Agreement For Each Phase

For every phase:

1. Define the user-visible behavior and API contract.
2. Implement the backend model or service first when it owns the behavior.
3. Add focused tests before moving on.
4. Connect the frontend to the real endpoint.
5. Run migrations, tests, linting, and type checks.
6. Start the application and manually verify the main path.
7. Update the relevant documentation and demo notes.
8. Record known limitations instead of hiding them.

Do not start the next phase when the current phase cannot be demonstrated locally.

## 5. First Build Session

The first implementation session should produce a runnable skeleton, not the whole product:

1. Create the repository directories and baseline documentation.
2. Add Docker Compose with PostgreSQL/PostGIS.
3. Create the Django project and custom user model.
4. Create the React/Vite application with routing and a basic authenticated shell.
5. Add environment examples and health checks.
6. Run migrations and the first backend/frontend test commands.
7. Commit no secrets and document the exact startup commands.

Once that foundation is green, begin incident models and authentication before investing in map polish. The map is important, but it becomes valuable only when it is backed by real incidents, risk calculations, and response state.

## 6. Risks To Manage Early

- **Map dependency:** Mapbox tokens and network access can block demos. Provide a clear configuration error and keep list/detail workflows usable without a map token.
- **Geospatial complexity:** Use PostGIS queries and tested geographic utilities rather than hand-written coordinate math scattered through the code.
- **Workflow inconsistency:** Centralize status transitions so every API and UI path records the same history.
- **Sensitive data exposure:** Separate private reporter fields from public incident serializers from the start.
- **Demo fragility:** Seed deterministic data and test the exact walkthrough after migrations.
- **False claims:** Label fictional data and planned integrations throughout the UI and documentation.

## 7. Final Release Checklist

- [ ] Clean-machine setup documented and verified.
- [ ] PostGIS migrations apply successfully.
- [ ] JWT authentication and role permissions tested.
- [ ] Community report works on mobile-sized screens.
- [ ] Incident location is stored as a geographic field.
- [ ] Risk score and reasons are visible.
- [ ] Status history is complete and immutable from normal client APIs.
- [ ] Ranger response workflow works end to end.
- [ ] Critical alerts appear internally.
- [ ] Analytics and hotspots use real seeded data.
- [ ] Demo data is clearly fictional and labeled.
- [ ] No unimplemented integration is presented as active.
- [ ] API documentation, README, limitations, and roadmap are current.
- [ ] Backend tests, frontend tests, linting, and type checks pass.
