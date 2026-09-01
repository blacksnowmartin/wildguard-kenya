# WildGuard Kenya - Pre-Frontend Integration Verification Checklist

Complete this checklist to verify the backend is ready for frontend integration.

## Prerequisites ✓

- [ ] Python 3.10+ installed
- [ ] PostgreSQL 14+ with PostGIS extension installed or Docker available
- [ ] Git repository cloned
- [ ] 2GB free disk space

## Setup Completion ✓

- [ ] Ran `bash setup.sh` successfully OR manually completed setup steps
- [ ] No errors in setup script output
- [ ] Virtual environment created and activated
- [ ] All dependencies installed (pip list shows Django, DRF, etc.)
- [ ] `.env` file configured with correct database credentials
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Demo data seeded (`python manage.py seed_demo_data --reset`)

## Database Verification ✓

- [ ] PostgreSQL service running
- [ ] PostGIS extension enabled in wildguard database
- [ ] 20 communities created in database
- [ ] 8 wildlife species created
- [ ] 7 demo users created with correct roles
- [ ] 7 demo incidents created with varying risk levels

Verify with:
```bash
cd backend
python manage.py shell
>>> from communities.models import Community, WildlifeSpecies
>>> Community.objects.count()  # Should be 20
>>> WildlifeSpecies.objects.count()  # Should be 8
>>> from incidents.models import HWCIncident
>>> HWCIncident.objects.count()  # Should be 7
>>> exit()
```

## API Endpoint Testing ✓

### Health Check
- [ ] `curl http://localhost:8000/api/health/` returns `{"status": "ok"}`
- [ ] HTTP 200 status code

### Authentication
- [ ] `POST /api/auth/token/` returns access and refresh tokens
- [ ] Token can be used for authenticated requests
- [ ] `POST /api/auth/refresh/` extends session
- [ ] `GET /api/auth/me/` returns current user profile
- [ ] Unauthenticated requests return 401

Verify with:
```bash
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_grace_kisumu","password":"password"}' | jq -r '.access')

curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/auth/me/
```

### Incident Endpoints
- [ ] `GET /api/incidents/` returns list of 7 demo incidents
- [ ] Each incident has: id, species, community, reporter, status, risk_score, location, created_at
- [ ] Location is in GeoJSON Point format with WGS84 coordinates
- [ ] `GET /api/incidents/{id}/` returns single incident detail
- [ ] Can filter by status, risk_level, community_id
- [ ] Risk scores range from 20 to 95 (LOW to CRITICAL)

Verify with:
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/incidents/ | jq '.[] | {id, risk_score, risk_level, status}'
```

### Incident Creation
- [ ] Can create new incident with all required fields
- [ ] Returns 201 CREATED
- [ ] Incident appears in list
- [ ] Risk score automatically calculated
- [ ] Location stored as PostGIS PointField
- [ ] Status history created automatically

Verify with:
```bash
curl -X POST http://localhost:8000/api/incidents/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "species": 1,
    "community": 1,
    "animal_count": 3,
    "severity": "HIGH",
    "description": "Test incident",
    "event_time": "2026-09-01T14:30:00Z",
    "latitude": -1.35,
    "longitude": 35.30,
    "property_damage": false
  }'
```

### Incident Actions
- [ ] Valid status transitions work (REPORTED → UNDER_REVIEW → VERIFIED)
- [ ] Invalid transitions return 400 error
- [ ] Status history created on each transition
- [ ] Only authorized roles can transition (Ranger/Supervisor)
- [ ] Community members cannot execute actions

Verify with:
```bash
SUPERVISOR_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_alex_mwangi","password":"password"}' | jq -r '.access')

curl -X POST http://localhost:8000/api/incidents/1/action/ \
  -H "Authorization: Bearer $SUPERVISOR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "review"}'
```

### Alerts
- [ ] Critical incidents (risk_level=CRITICAL) generate alerts
- [ ] `GET /api/alerts/` returns list of critical alerts
- [ ] Alert includes incident details and reason
- [ ] Alert creation is idempotent (no duplicates)

Verify with:
```bash
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/alerts/ | jq '.[] | {priority, incident}'
```

### Notifications
- [ ] `GET /api/notifications/` returns user's notifications
- [ ] Can mark notification as read: `POST /api/notifications/{id}/read/`
- [ ] Unread notifications show `read_at: null`
- [ ] Read notifications show `read_at` timestamp

## Test Suite Results ✓

- [ ] All pytest tests pass: `python -m pytest test_api_comprehensive.py -v`
  - Risk calculation tests (at least 10 tests)
  - Status transition tests
  - Alert generation tests
  - Geographic query tests

- [ ] All Django tests pass: `python manage.py test`
  - Model tests
  - Serializer validation tests
  - Permission tests

- [ ] E2E tests pass: `python run_e2e_tests.py`
  - Authentication flow (✓)
  - Incident creation (✓)
  - Risk calculation (✓)
  - Status transitions (✓)
  - Alert generation (✓)

Run comprehensive test suite:
```bash
bash run_tests.sh
```

## Risk Engine Validation ✓

- [ ] Base score equals species danger factor (e.g., Elephant 75)
- [ ] Settlement proximity adds +25 to score
- [ ] Night-time incidents add +10
- [ ] Multiple animals add +10
- [ ] Previous nearby incidents add +15
- [ ] Property damage adds +15
- [ ] Score is clamped at 100 maximum
- [ ] Risk levels correct:
  - LOW: 0-25
  - MODERATE: 26-50
  - HIGH: 51-75
  - CRITICAL: 76-100

Verify with:
```bash
# Check demo incident risk scores
curl -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/incidents/ \
  | jq '.[] | {id, risk_score, risk_level, animal_count, severity}'
```

## Permissions & Access Control ✓

- [ ] Community members can only create incidents (their own reports)
- [ ] Community members cannot execute actions
- [ ] Rangers can respond to incidents but not verify
- [ ] Supervisors can verify and dispatch
- [ ] Admins have full access
- [ ] Unauthenticated requests blocked (401)
- [ ] Unauthorized requests blocked (403)

Test as different users:
```bash
# Try as community member (should create incident)
COMMUNITY_TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -d '{"username":"demo_grace_kisumu","password":"password"}' | jq -r '.access')

curl -X POST http://localhost:8000/api/incidents/1/action/ \
  -H "Authorization: Bearer $COMMUNITY_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"action": "review"}'
# Should return 403 FORBIDDEN
```

## Documentation ✓

- [ ] README.md updated with current status
- [ ] SETUP_GUIDE.md contains complete setup instructions
- [ ] DEMO_DATA_SETUP.md explains demo data structure
- [ ] docs/api.md contains full API reference
- [ ] docs/architecture.md explains data model
- [ ] IMPLEMENTATION_GUIDE.md reflects completed phases

## Performance & Stability ✓

- [ ] Backend starts without errors: `python manage.py runserver`
- [ ] No console errors during normal operation
- [ ] Database queries complete in <100ms
- [ ] Can handle 100 concurrent requests (load testing not required yet)
- [ ] Memory usage stable (no memory leaks)

## Frontend Integration Readiness ✓

- [ ] API documentation complete (docs/api.md)
- [ ] Example curl commands provided for all endpoints
- [ ] CORS configured for localhost:5173
- [ ] JWT token handling documented
- [ ] Error response format documented
- [ ] All response objects have consistent structure
- [ ] GeoJSON coordinates in correct format [longitude, latitude]

## Security Baseline ✓

- [ ] No secrets committed to repository
- [ ] .env.example contains placeholder values only
- [ ] JWT tokens expire appropriately
- [ ] Password hashing used (Django default)
- [ ] SQL injection protection (Django ORM)
- [ ] CSRF protection configured
- [ ] CORS restricted to development origins
- [ ] Debug mode disabled in production-like deployments

Check with:
```bash
cat .env  # Should not contain real credentials
grep -r "password" backend/ --include="*.py" | grep -v "password_" | wc -l  # Should be minimal
```

## Database Cleanup & Reset ✓

- [ ] Can reset database: `python manage.py migrate zero`
- [ ] Can re-apply migrations: `python manage.py migrate`
- [ ] Can reseed demo data: `python manage.py seed_demo_data --reset`
- [ ] No data persists after reset
- [ ] Clean state takes <30 seconds

## Ready for Frontend Integration? 

Once all items are checked, the backend is ready for:

1. **React Frontend Connection**
   - Implement API service layer
   - Add authentication state management
   - Connect incident list to real API
   - Build incident reporting form

2. **Map Integration**
   - Add Mapbox integration
   - Display incidents as markers
   - Show risk level colors
   - Implement filtering

3. **Analytics Dashboard**
   - Fetch incident aggregates
   - Display trends and hotspots

## Troubleshooting Failed Checks

### API returns 503 SERVICE UNAVAILABLE
- PostgreSQL not running: `sudo systemctl start postgresql`
- Check database: `psql -d wildguard -c "SELECT 1"`

### Migrations failed
```bash
python manage.py migrate --verbosity 2
python manage.py migrate zero  # Reset if needed
python manage.py migrate
```

### PostGIS extension missing
```bash
sudo -u postgres psql -d wildguard -c "CREATE EXTENSION postgis;"
```

### Demo data not seeding
```bash
python manage.py seed_demo_data --reset
python manage.py shell << EOF
from incidents.models import HWCIncident
print(f"Total incidents: {HWCIncident.objects.count()}")
EOF
```

### Tests failing
```bash
python -m pytest test_api_comprehensive.py -v --tb=short
python manage.py test --verbosity=2
```

---

**Date Completed**: ___________
**Verified By**: ___________
**Notes**: ___________

Once this checklist is complete, commit with message: "Phase 2-3 Complete: Backend ready for frontend integration"
