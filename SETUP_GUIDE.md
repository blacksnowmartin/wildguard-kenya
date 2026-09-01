# WildGuard Kenya - Backend Setup and Testing Guide

## Prerequisites

Before setting up the backend, ensure you have:

1. **Python 3.10+** installed
2. **PostgreSQL 14+** with PostGIS extension installed
3. **pip** (Python package manager)

### Installing PostgreSQL + PostGIS (on Ubuntu/Debian)

```bash
# Install PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib postgresql-client

# Install PostGIS
sudo apt install postgresql-14-postgis-3

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and enable PostGIS
sudo -u postgres psql << EOF
CREATE DATABASE wildguard;
CREATE USER wildguard WITH PASSWORD 'wildguard';
ALTER ROLE wildguard SET client_encoding TO 'utf8';
ALTER ROLE wildguard SET default_transaction_isolation TO 'read committed';
ALTER ROLE wildguard SET default_transaction_deferrable TO on;
ALTER ROLE wildguard SET default_transaction_read_committed TO on;
ALTER ROLE wildguard SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE wildguard TO wildguard;

\c wildguard
CREATE EXTENSION postgis;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO wildguard;
EOF
```

### Installing via Docker Compose (Alternative)

```bash
# Start services
docker compose up -d db

# Wait for database to be ready
sleep 5

# Check database status
docker compose logs db
```

## Quick Setup

Run the automated setup script:

```bash
cd /path/to/wildguard-kenya
bash setup.sh
```

This script will:
- Create a Python virtual environment
- Install all dependencies
- Run database migrations
- Seed demo data
- Create a superuser account
- Prepare the application

## Manual Setup

If you prefer to set up manually:

### 1. Create Virtual Environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment

```bash
# Copy example .env to root directory
cp .env.example ../.env

# Edit .env with your database credentials if needed
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Seed Demo Data

```bash
# Full reset and reseed
python manage.py seed_demo_data --reset

# Or just seed (won't delete existing data)
python manage.py seed_demo_data
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

Or use a quick shell command:

```bash
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser(
    username='admin',
    email='admin@demo.wildguard',
    password='admin123',
    role=User.Role.ADMIN
)
print("Superuser created: admin / admin123")
EOF
```

## Running the Server

Start the development server:

```bash
cd backend
source .venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

The API will be available at:
- Health check: http://localhost:8000/api/health/
- Token endpoint: http://localhost:8000/api/auth/token/
- Current user: http://localhost:8000/api/auth/me/
- Incidents: http://localhost:8000/api/incidents/

## Running Tests

### End-to-End API Tests

```bash
cd backend
source .venv/bin/activate
python run_e2e_tests.py
```

This will test:
- ✓ JWT authentication (token obtain, refresh)
- ✓ Incident creation with location and risk calculation
- ✓ Incident retrieval (list and detail)
- ✓ Risk score calculation (0-100 scale)
- ✓ Status transitions (REPORTED → UNDER_REVIEW → VERIFIED, etc.)
- ✓ Critical alerts generation
- ✓ Alert retrieval

### Django Test Suite

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test incidents
python manage.py test accounts
python manage.py test communities

# Run with verbose output
python manage.py test --verbosity=2

# Run specific test case
python manage.py test incidents.tests.IncidentModelTests
```

### Test Coverage

```bash
# Install coverage
pip install coverage

# Run tests with coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

## Demo Users

After seeding, these demo users are available:

| Username | Password | Role | Use Case |
|----------|----------|------|----------|
| `demo_admin` | `admin123` | Admin | Full system access |
| `demo_alex_mwangi` | `password` | Supervisor | Verify & dispatch incidents |
| `demo_jane_kipchoge` | `password` | Ranger | Respond to incidents |
| `demo_grace_kisumu` | `password` | Community Member | Report incidents |

## API Endpoints

### Authentication

```bash
# Get token
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_grace_kisumu","password":"password"}'

# Refresh token
curl -X POST http://localhost:8000/api/auth/refresh/ \
  -H "Content-Type: application/json" \
  -d '{"refresh":"<refresh_token>"}'

# Get current user
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/auth/me/
```

### Incidents

```bash
# List all incidents
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/incidents/

# Create incident
curl -X POST http://localhost:8000/api/incidents/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "species": 1,
    "community": 1,
    "animal_count": 3,
    "severity": "HIGH",
    "description": "Herd of elephants near farmland",
    "event_time": "2026-09-01T14:30:00Z",
    "latitude": -1.35,
    "longitude": 35.30,
    "property_damage": true
  }'

# Get incident detail
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/incidents/1/

# Trigger incident action (review, verify, dispatch, resolve, etc.)
curl -X POST http://localhost:8000/api/incidents/1/action/ \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{"action": "review"}'
```

### Alerts

```bash
# List alerts
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/alerts/

# List notifications
curl -H "Authorization: Bearer <access_token>" \
  http://localhost:8000/api/notifications/

# Mark notification as read
curl -X POST http://localhost:8000/api/notifications/1/read/ \
  -H "Authorization: Bearer <access_token>"
```

## Troubleshooting

### Database Connection Errors

**Problem**: `psycopg.OperationalError: connection failed`

**Solution**: Ensure PostgreSQL is running:
```bash
# Check status
sudo systemctl status postgresql

# Start if needed
sudo systemctl start postgresql

# Or use Docker
docker compose up -d db
docker compose logs db
```

### PostGIS Extension Missing

**Problem**: `django.core.exceptions.ImproperlyConfigured: PostGIS extension not found`

**Solution**: Enable PostGIS in the database:
```bash
sudo -u postgres psql -d wildguard -c "CREATE EXTENSION postgis;"
```

### Python Package Issues

**Problem**: `ModuleNotFoundError: No module named 'django'`

**Solution**: Reinstall dependencies in virtual environment:
```bash
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Port Already in Use

**Problem**: `Address already in use: ('0.0.0.0', 8000)`

**Solution**: Use a different port:
```bash
python manage.py runserver 8001
```

Or kill the existing process:
```bash
lsof -ti:8000 | xargs kill -9
```

## Docker Deployment

For production-like local testing with Docker:

```bash
# Build and start all services
docker compose up -d

# Run migrations in container
docker compose exec backend python manage.py migrate

# Seed demo data
docker compose exec backend python manage.py seed_demo_data --reset

# View logs
docker compose logs -f backend

# Access services
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

## Next Steps

1. **Test the incident reporting flow** - Create an incident via the API
2. **Connect the frontend** - Update React app to fetch real incidents
3. **Build the map interface** - Integrate Mapbox for geographic visualization
4. **Implement risk engine** - Verify risk calculations in real-world scenarios
5. **Add response workflows** - Test ranger dispatch and resolution flows

## Documentation

- [Implementation Guide](../IMPLEMENTATION_GUIDE.md) - Detailed build roadmap
- [Master Spec](../Master.md) - Product vision and architecture
- [API Documentation](../docs/api.md) - Full API reference (coming soon)
- [Data Model](../docs/architecture.md) - Database schema and relationships
