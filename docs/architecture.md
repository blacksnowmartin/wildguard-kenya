# Initial Architecture

WildGuard Kenya is a modular monolith: one Django REST API, one React/Vite client, and PostgreSQL/PostGIS.

The initial boundaries are Django apps: `accounts`, `communities`, `incidents`, `response`, `risk`, `analytics`, and `integrations`. The first slice provides the frontend Command Center shell and a backend health endpoint. The current backend slice adds migration-ready custom users, configurable communities and species, geographic incidents, private reporter details, immutable status history, response records, risk snapshots, alerts, and notifications. JWT authentication and API serializers are next.

All demonstration records must be visibly labeled `DEMO DATA - NOT LIVE FIELD DATA`. Reporter contact details will remain private by default, and risk scoring will remain transparent, rule-based, and versioned.
