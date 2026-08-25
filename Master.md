# MASTER BUILD PROMPT — WILDGUARD KENYA

You are the lead software architect, senior full-stack engineer, GIS engineer, conservation-technology product designer, and technical product manager for a serious prototype called:

**WILDGUARD KENYA**

## 1. PRODUCT VISION

Build a production-quality prototype for a Human–Wildlife Conflict (HWC) Intelligence and Response Platform designed initially for Kenya.

The system must help communities report wildlife incidents, help conservation/ranger teams verify and respond to incidents, visualize incidents geographically, calculate explainable HWC risk scores, identify hotspots, maintain incident history, and provide analytics for decision-makers.

This is NOT intended to replace EarthRanger, KWS systems, county systems, or existing conservation platforms.

Instead, design WildGuard as a localized HWC intelligence and community-response layer that can eventually integrate with existing conservation infrastructure through APIs.

The prototype must be credible enough to demonstrate in a government, NGO, conservation, university, accelerator, or investor boardroom.

Do not build a toy CRUD application.

Build the foundation of a real product.

---

# 2. CORE PRODUCT WORKFLOW

Implement this complete workflow:

COMMUNITY REPORT
↓
INCIDENT CREATED
↓
GIS LOCATION
↓
RISK ANALYSIS
↓
VERIFICATION
↓
RANGER ALERT
↓
DISPATCH
↓
RESPONSE
↓
RESOLUTION
↓
ANALYTICS
↓
HOTSPOT INTELLIGENCE

Every stage must be represented in the system.

---

# 3. TECHNOLOGY STACK

Use:

Frontend:

* React
* TypeScript
* Vite
* Tailwind CSS
* Mapbox GL JS
* Recharts

Backend:

* Python
* Django
* Django REST Framework

Database:

* PostgreSQL
* PostGIS

Authentication:

* JWT

API:

* REST
* OpenAPI documentation

Testing:

* Pytest
* React/Vitest tests where appropriate

Infrastructure:

* Docker
* Docker Compose

Code quality:

* Type hints
* ESLint
* Prettier
* sensible Django project structure
* environment variables
* secure configuration

Do not introduce unnecessary microservices.

Use a modular monolith architecture that can later be split into services.

---

# 4. REPOSITORY STRUCTURE

Create:

wildguard-kenya/

README.md
LICENSE
.gitignore
.env.example
docker-compose.yml

docs/
problem-statement.md
product-requirements.md
system-architecture.md
database-design.md
api-specification.md
demo-scenario.md
future-integrations.md

frontend/

backend/

ai/

database/

integrations/

tests/

demo/

The README must explain how to run the entire project locally from a clean machine.

---

# 5. USER ROLES

Implement:

COMMUNITY_MEMBER
RANGER
SUPERVISOR
ADMIN

Each role must have appropriate permissions.

Community members:

* report incidents
* view their submitted reports
* receive status updates

Rangers:

* view assigned incidents
* verify incidents
* accept incidents
* update response status
* record resolution

Supervisors:

* view all incidents
* monitor response performance
* assign incidents
* view analytics
* view hotspots

Admins:

* manage users
* manage communities
* manage wildlife species
* manage system configuration

---

# 6. CORE DATA MODELS

Create robust Django models for:

User
Community
WildlifeSpecies
HWCIncident
IncidentEvidence
IncidentStatusHistory
RangerResponse
Alert
WildlifeSighting
RiskAssessment
Hotspot
Notification

HWCIncident should contain at least:

id
species
description
latitude
longitude
reported_at
severity
status
reporter
community
risk_score
risk_level
verified
created_at
updated_at

Use PostGIS-compatible geographic fields.

Do not store latitude/longitude only as plain strings.

---

# 7. INCIDENT STATUS

Implement:

REPORTED
UNDER_REVIEW
VERIFIED
REJECTED
DISPATCHED
RESPONDING
RESOLVED
CLOSED

Every status change must be recorded in IncidentStatusHistory.

The dashboard must be able to show the timeline of an incident.

---

# 8. HWC REPORTING INTERFACE

Create a mobile-friendly community reporting interface.

It must allow:

* species selection
* number of animals
* location capture
* manual map location selection
* severity
* description
* evidence/photo upload
* time
* optional contact information

Make reporting extremely simple.

The UI should be usable by someone with limited technical experience.

Provide sample/demo data so the system can be demonstrated without needing a real field deployment.

---

# 9. COMMAND CENTER

Create a professional dashboard called:

**WildGuard Command Center**

The dashboard should include:

* total incidents
* active incidents
* critical incidents
* incidents today
* average response time
* response rate
* verified incidents
* unresolved incidents

Main section:

LIVE HWC MAP

Use Mapbox.

Display incidents as geographic markers.

Marker colors must correspond to risk levels.

Clicking a marker must open an incident summary.

Add filters:

* species
* risk level
* status
* date
* county/community

---

# 10. RISK ENGINE

Create an explainable HWC risk engine.

Do NOT claim that this is machine learning.

Call it:

**HWC Risk Engine**

Initially use transparent rule-based scoring.

Example factors:

Elephant: +25
Buffalo: +30
Lion: +35
Hippo: +30
Other dangerous species: configurable

Settlement proximity < 2 km: +25

Night-time incident: +10

Multiple animals: +10

Previous incidents nearby: +15

Crop/property damage reported: +15

Cap the score at 100.

Risk levels:

0–25 = LOW
26–50 = MODERATE
51–75 = HIGH
76–100 = CRITICAL

The system must show WHY a score was generated.

Example:

Risk Score: 87

Reasons:

* Elephant activity +25
* Settlement within 2 km +25
* Night-time +10
* Multiple animals +10
* Previous nearby incidents +15
* Crop damage +15

Do not hide the calculation.

Design the architecture so this rule engine can later be replaced or supplemented by ML.

---

# 11. HOTSPOT DETECTION

Implement a basic spatial hotspot engine.

Use historical incidents to identify areas with unusually high concentrations of HWC incidents.

Display hotspots on the map.

Each hotspot should include:

* location
* incident count
* dominant species
* average risk
* recent trend
* recommended priority

Use a simple explainable algorithm initially.

Do not pretend it is advanced AI.

---

# 12. RANGER RESPONSE SYSTEM

Create a ranger interface.

A ranger should be able to see:

* assigned incidents
* priority
* location
* species
* risk score
* evidence
* reporter description

Buttons:

ACCEPT
DISPATCH
RESPONDING
RESOLVED

When resolving an incident, capture:

* resolution notes
* response time
* outcome
* optional evidence

---

# 13. ALERT SYSTEM

Create an internal alert system.

Critical incidents must generate high-priority alerts.

Example:

CRITICAL HWC INCIDENT

Species:
Elephant

Risk:
87/100

Location:
Community X

Reason:
Animal activity detected near populated area.

Design the architecture so SMS, WhatsApp, email and push notifications can be integrated later.

For the prototype, internal dashboard notifications are sufficient.

Do not claim that SMS/WhatsApp actually works unless a real provider integration exists.

---

# 14. ANALYTICS

Create an analytics page.

Show:

* incidents over time
* incidents by species
* incidents by community
* incidents by county
* risk distribution
* average response time
* response success rate
* unresolved incidents
* recurring hotspots
* time-of-day trends

Create charts that look suitable for an executive presentation.

Include date filters.

---

# 15. EXECUTIVE DASHBOARD

Create a separate executive view.

The executive dashboard should answer:

1. Where are incidents happening?
2. Which wildlife species cause the most incidents?
3. Which communities are most affected?
4. Which incidents are currently critical?
5. How quickly are teams responding?
6. Where are the emerging hotspots?
7. Is HWC increasing or decreasing?

Use clean visual hierarchy.

Avoid excessive technical terminology.

---

# 16. DEMO DATA

Create realistic fictional demonstration data.

IMPORTANT:

Clearly label all demonstration data as:

**DEMO DATA — NOT LIVE FIELD DATA**

Do not use fabricated data in a way that could be mistaken for official KWS, government, EarthRanger, or community data.

Create at least:

* 5 communities
* 50 incidents
* several wildlife species
* multiple risk levels
* several hotspots
* ranger responses
* historical status changes

The demo should immediately look alive after running the seed command.

---

# 17. DEMO SCENARIO

Create a one-command demo data seed.

The boardroom demonstration should follow this scenario:

A community member reports elephant activity near farmland.

The report contains:

Species:
Elephant

Number:
6

Severity:
High

Description:
Elephants approaching farmland and destroying crops.

Location:
Demo community

The system should:

1. Create incident.
2. Calculate risk.
3. Classify as CRITICAL.
4. Display it on the map.
5. Generate a critical alert.
6. Make the incident available to a ranger.
7. Allow ranger acceptance.
8. Allow dispatch.
9. Allow response.
10. Allow resolution.
11. Record the complete timeline.
12. Update analytics.

This must work reliably during a live demonstration.

---

# 18. FUTURE INTEGRATIONS

Create an integrations architecture but do not implement fake integrations.

Prepare interfaces/adapters for:

* EarthRanger
* Gundi
* SMS gateway
* WhatsApp
* USSD
* IoT sensors
* GPS collars
* camera traps
* weather data

Create clear TODO documentation describing how each integration would eventually work.

Never claim an integration exists unless it is actually implemented and tested.

---

# 19. EARTHRANGER POSITIONING

WildGuard must be architected as complementary to existing conservation systems.

Do NOT clone EarthRanger.

Do NOT copy proprietary code.

Do NOT present WildGuard as an official KWS or EarthRanger product.

Instead describe it as:

"A localized Human–Wildlife Conflict intelligence and community-response platform designed to complement existing conservation data and response infrastructure."

Create a future integration interface where appropriate.

---

# 20. SECURITY

Implement reasonable security from the beginning.

Include:

* authentication
* role-based authorization
* password hashing
* JWT security
* input validation
* file upload validation
* API permissions
* environment variables for secrets
* CORS configuration
* rate limiting strategy/documentation
* audit logging
* basic privacy controls

Do not expose secrets in source code.

Create .env.example rather than committing credentials.

---

# 21. PRIVACY

Treat community reports as potentially sensitive.

Do not expose reporter personal information on public maps.

Separate:

PUBLIC INCIDENT INFORMATION

from:

PRIVATE REPORTER INFORMATION

Design permissions accordingly.

---

# 22. API

Create clean REST endpoints.

At minimum:

POST /api/incidents/
GET /api/incidents/
GET /api/incidents/{id}/
PATCH /api/incidents/{id}/

POST /api/incidents/{id}/verify/
POST /api/incidents/{id}/dispatch/
POST /api/incidents/{id}/resolve/

GET /api/incidents/map/
GET /api/analytics/
GET /api/hotspots/
GET /api/alerts/

Use serializers and proper validation.

Generate API documentation.

---

# 23. UX REQUIREMENTS

The product should feel like a serious conservation technology platform.

Avoid:

* generic Bootstrap-looking screens
* excessive gradients
* unnecessary animations
* meaningless AI terminology
* fake statistics
* fake integrations
* clutter

Prioritize:

* maps
* clear alerts
* data
* status
* response workflows
* professional typography
* accessibility
* mobile responsiveness

---

# 24. README

Write a strong README explaining:

1. What WildGuard is.
2. The HWC problem.
3. Who uses it.
4. How it works.
5. Architecture.
6. Technology stack.
7. Installation.
8. Docker setup.
9. Database setup.
10. Demo data.
11. API documentation.
12. Testing.
13. Future integrations.
14. Limitations.
15. Roadmap.

Include a clear disclaimer:

"This prototype is not an official government, KWS, EarthRanger, or conservation-agency system. Demonstration data is fictional."

---

# 25. DEVELOPMENT PROCESS

Do NOT attempt to generate the entire system in one giant operation.

Work in phases.

PHASE 1:
Repository + Docker + database + backend foundation.

PHASE 2:
Authentication + users + communities.

PHASE 3:
Incident reporting.

PHASE 4:
GIS map.

PHASE 5:
Risk engine.

PHASE 6:
Ranger response workflow.

PHASE 7:
Alerts.

PHASE 8:
Analytics.

PHASE 9:
Hotspot detection.

PHASE 10:
Executive dashboard.

PHASE 11:
Demo data.

PHASE 12:
Testing + security + documentation.

After every phase:

1. Run tests.
2. Check for errors.
3. Start the application.
4. Verify the feature manually.
5. Update documentation.
6. Do not proceed if the previous phase is broken.

---

# 26. IMPORTANT CODING RULE

Do not merely create files to satisfy the specification.

Actually implement working functionality.

If a dependency is required, add it properly.

If a database migration is required, create it.

If an API endpoint is specified, implement it.

If a frontend component depends on an API, connect it.

Avoid TODO placeholders for core MVP functionality.

---

# 27. BOARDROOM QUALITY TEST

Before declaring the MVP complete, verify that a person can perform this sequence without developer intervention:

Community user:
→ login
→ report elephant incident
→ submit location/evidence

System:
→ calculates risk
→ generates alert
→ displays incident on map

Ranger:
→ sees incident
→ accepts
→ dispatches
→ marks responding
→ resolves

Supervisor:
→ sees updated dashboard
→ sees incident history
→ sees hotspot/analytics
→ sees response metrics

If this workflow works end-to-end, the prototype is considered successful.

---

# 28. INVESTOR DEMONSTRATION PRINCIPLE

The application must communicate one simple idea:

**"We turn scattered community HWC reports into actionable spatial intelligence and coordinated response."**

Do not overload the interface with blockchain, AI, IoT, Web3 or buzzwords.

The first product must solve the problem clearly.

Future technologies can be added after product-market validation.

---

# 29. START NOW

First inspect the repository.

If the repository is empty, initialize the complete project structure.

Then implement PHASE 1 only.

Do not jump ahead.

At the end of PHASE 1:

* show the created structure
* explain what was implemented
* provide exact commands to run it
* run available tests
* identify any remaining issues

Then wait for approval before moving to PHASE 2.
