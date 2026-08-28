# WildGuard Kenya

WildGuard is a Kenya-focused human-wildlife conflict intelligence and response prototype. It complements existing conservation systems and does not replace or impersonate them.

> **DEMO DATA - NOT LIVE FIELD DATA**

## Current status

The first runnable slice is a responsive Command Center frontend with fictional incident data. Backend models, authentication, reporting, risk, response workflow, and analytics are staged next according to [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md).

## Run the frontend

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:5173>.

## Backend foundation

The Django domain foundation is now migration-ready. With Docker installed, start PostGIS from the repository root:

```bash
docker compose up -d db
cd backend
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py runserver
```

The API health check is available at <http://localhost:8000/api/health/>.

JWT authentication is now configured with these endpoints:

- `POST /api/auth/token/`
- `POST /api/auth/refresh/`
- `GET /api/auth/me/`

The next implementation slice is role-aware incident serializers and endpoints. The current machine does not have Docker installed, so applying migrations or running database-backed tests must wait for a local PostGIS service.
