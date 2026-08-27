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

Docker is planned for the PostgreSQL/PostGIS development environment. The current machine does not have Docker installed, so the browser shell is intentionally runnable independently while the backend foundation is added.
