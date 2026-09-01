# WildGuard Kenya

WildGuard is a Kenya-focused human-wildlife conflict intelligence and response prototype. It complements existing conservation systems and does not replace or impersonate them.

> **DEMO DATA - NOT LIVE FIELD DATA**

## Current Status

**Phase 2-3 Complete**: Incident reporting backend fully functional with comprehensive testing infrastructure.

- ✅ Domain models (User, HWCIncident, RiskAssessment, Alert, etc.)
- ✅ API endpoints (auth, incidents, alerts, notifications)
- ✅ Risk scoring engine with explainable reasons
- ✅ Status workflow validation
- ✅ Automated demo data seeding
- ✅ Comprehensive test suites (pytest, E2E, Django tests)
- ✅ Role-based access control
- ✅ JWT authentication

**Next Focus**: Frontend API integration (Command Center → real backend API)

## Quick Start

### Automated Setup (Recommended)

```bash
bash setup.sh
```

This will:
- Create Python virtual environment
- Install dependencies
- Configure database
- Run migrations
- Seed demo data (20 communities, 7 incidents, 7 users)
- Create superuser

### Manual Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Configure .env file
cp ../.env.example ../.env

# Run migrations
python manage.py migrate

# Seed demo data
python manage.py seed_demo_data --reset

# Start server
python manage.py runserver
```

## Running the Application

### Backend API Server

```bash
cd backend
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

API available at: `http://localhost:8000`
- Health check: `/api/health/`
- Auth endpoints: `/api/auth/`
- Incidents: `/api/incidents/`
- Alerts: `/api/alerts/`

### Frontend (React + Vite)

```bash
cd frontend
npm install
npm run dev
```

Frontend available at: `http://localhost:5173`

## Testing

### Run All Tests

```bash
bash run_tests.sh
```

### Individual Test Suites

```bash
# E2E API tests
python backend/run_e2e_tests.py

# Pytest comprehensive tests
python -m pytest backend/test_api_comprehensive.py -v

# Django tests
python backend/manage.py test
```

## Default Demo Users

| Username | Password | Role |
|----------|----------|------|
| demo_admin | admin123 | Admin |
| demo_alex_mwangi | password | Supervisor |
| demo_jane_kipchoge | password | Ranger |
| demo_grace_kisumu | password | Community Member |

## Demo Data Included

- **8 Wildlife Species**: Elephant, Lion, Buffalo, Hippo, Leopard, Hyena, Wild Dog, Rhino
- **20 Communities**: Across 15 Kenyan counties with geographic coordinates
- **7 Demo Incidents**: Ranging from LOW to CRITICAL risk levels
- **Full Status History**: Each incident has workflow state changes
- **Risk Assessments**: Pre-calculated with reasons

## API Endpoints

### Authentication

```bash
# Obtain JWT token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_grace_kisumu","password":"password"}'

# Refresh token
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'
```

### Incidents

```bash
# List incidents
curl -H "Authorization: Bearer <token>" \
  http://localhost:8000/api/incidents/

# Create incident
curl -X POST http://localhost:8000/api/incidents/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "species": 1,
    "community": 1,
    "animal_count": 3,
    "severity": "HIGH",
    "description": "Herd near farmland",
    "event_time": "2026-09-01T14:30:00Z",
    "latitude": -1.35,
    "longitude": 35.30,
    "property_damage": true
  }'

# Transition incident (review → verify → dispatch → resolve)
curl -X POST http://localhost:8000/api/incidents/1/action/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"action": "review"}'
```

## Architecture

```
React Frontend (5173)           Django REST API (8000)      PostgreSQL + PostGIS (5432)
┌──────────────────────┐        ┌──────────────────────┐    ┌──────────────────────┐
│ Command Center       │◄──────►│ Incident Endpoints   │───►│ Incidents Table      │
│ Map Visualization    │ REST   │ Auth Endpoints       │    │ Users (4 roles)      │
│ Reporting Form       │ JWT    │ Alert Endpoints      │    │ Communities          │
│ Analytics Dashboard  │        │ Risk Engine          │    │ Status History       │
└──────────────────────┘        │ Access Control       │    │ Geographic Data      │
                                └──────────────────────┘    └──────────────────────┘
```

## Documentation

- [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md) - Complete build roadmap (11 phases)
- [SETUP_GUIDE.md](SETUP_GUIDE.md) - Detailed setup instructions for all platforms
- [DEMO_DATA_SETUP.md](DEMO_DATA_SETUP.md) - Demo data structure and testing guide
- [Master.md](Master.md) - Product vision and technical specifications
- [docs/architecture.md](docs/architecture.md) - Database schema details

## Key Features

### Risk Calculation
- Deterministic scoring (0-100)
- Multiple weighted factors
- Explainable reasons
- Risk level classification

### Status Workflow
- Controlled state transitions
- Immutable audit trail
- Role-based permissions
- Timeline history

### Geographic Intelligence
- PostGIS point storage (WGS84)
- Proximity calculations
- Community metadata
- Map-ready coordinates

### Access Control
- JWT authentication
- 4 role types (Admin, Supervisor, Ranger, Community Member)
- Granular API permissions
- User profile endpoints

## Environment Variables

See `.env.example` for configuration:

```
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=<your-secret>
POSTGRES_DB=wildguard
POSTGRES_USER=wildguard
POSTGRES_PASSWORD=wildguard
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

## Troubleshooting

### Database Connection Failed
Ensure PostgreSQL is running and PostGIS extension is installed:

```bash
sudo systemctl start postgresql
sudo -u postgres psql -d wildguard -c "CREATE EXTENSION postgis;"
```

### Port Already in Use
Use a different port:

```bash
python manage.py runserver 8001
```

### Migration Errors
Reset and reapply migrations:

```bash
python manage.py migrate zero
python manage.py migrate
python manage.py seed_demo_data --reset
```

## Next Phase

Frontend integration: Connect React Command Center to backend API for real incident data, map visualization, and incident reporting form.

## Related Documents

- **Implementation Plan**: [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
- **Architecture Details**: [docs/architecture.md](docs/architecture.md)
- **Demo Scenario**: [docs/demo-scenario.md](docs/demo-scenario.md)
- **Master Specification**: [Master.md](Master.md)

---

**Status**: Ready for frontend integration and full E2E testing. Backend API production-grade foundation complete.
