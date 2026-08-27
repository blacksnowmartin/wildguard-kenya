# Initial Architecture

WildGuard Kenya is a modular monolith: one Django REST API, one React/Vite client, and PostgreSQL/PostGIS.

The initial boundaries are planned as Django apps: `accounts`, `communities`, `incidents`, `response`, `risk`, `analytics`, and `integrations`. The first slice provides the frontend Command Center shell and a backend health endpoint. Incident persistence and JWT authentication are the next implementation slice.

All demonstration records must be visibly labeled `DEMO DATA - NOT LIVE FIELD DATA`. Reporter contact details will remain private by default, and risk scoring will remain transparent, rule-based, and versioned.
