# WildGuard Kenya - Manual Installation Guide

Follow these commands step-by-step to install and run the project.

## Prerequisites Already Installed ✓

- ✓ Python 3.12.3
- ✓ Node.js v24.16.0
- ✓ npm 11.17.0  
- ✓ PostgreSQL 16 with PostGIS 3
- ✓ WildGuard database and user created

## Installation Steps

### Step 1: Activate Python Virtual Environment

```bash
cd /home/blacksnowmartin/wildguard-kenya/backend
source .venv/bin/activate
```

You should see `(.venv)` in your terminal prompt after this.

### Step 2: Run Database Migrations

This creates all the necessary database tables:

```bash
python manage.py migrate --noinput
```

**Expected output:**
```
Operations to perform:
  Apply all migrations: accounts, admin, auth, communities, contenttypes, incidents, response, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying accounts.0001_initial... OK
  Applying communities.0001_initial... OK
  Applying incidents.0001_initial... OK
  ... (more migrations)
```

### Step 3: Seed Demo Data

This populates the database with demo communities, species, users, and incidents:

```bash
python manage.py seed_demo_data --reset
```

**Expected output:**
```
Seeding demo data...
✓ Seeded 8 wildlife species
✓ Seeded 20 communities
✓ Seeded 7 users
✓ Seeded 7 demo incidents
✓ Demo data seeded successfully
```

### Step 4: Create Admin Superuser

```bash
python manage.py shell
```

Then paste this code:

```python
from django.contrib.auth import get_user_model
User = get_user_model()
User.objects.create_superuser(
    username='admin',
    email='admin@wildguard.local',
    password='admin123',
    role='ADMIN'
)
print("✓ Admin user created: admin / admin123")
exit()
```

### Step 5: Verify Backend is Working

Start the development server:

```bash
python manage.py runserver 0.0.0.0:8000
```

**Expected output:**
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CONTROL-C.
```

### Step 6: Test API in Another Terminal

Open a NEW terminal (keep the server running):

```bash
# Test health check
curl http://localhost:8000/api/health/

# Expected output:
# {"status": "ok", "service": "wildguard-api"}
```

### Step 7: Start the React Frontend

In a THIRD terminal, go to the frontend directory:

```bash
cd /home/blacksnowmartin/wildguard-kenya/frontend
npm install
npm run dev
```

**Expected output:**
```
VITE v5.x.x  ready in 123 ms

➜  Local:   http://localhost:5173/
➜  press h to show help
```

## 🎉 You're Done!

Access the application:
- **Frontend**: http://localhost:5173
- **API**: http://localhost:8000/api/
- **Health Check**: http://localhost:8000/api/health/

## Demo Users to Test

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| demo_alex_mwangi | password | Supervisor |
| demo_jane_kipchoge | password | Ranger |
| demo_grace_kisumu | password | Community Member |

## Testing the API

Get a token and test incident creation:

```bash
# 1. Get token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"demo_grace_kisumu","password":"password"}' | jq -r '.access')

# 2. List incidents
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/api/incidents/ | jq '.[] | {id, species, risk_level, status}'

# Expected output: 7 demo incidents with varying risk levels
```

## Troubleshooting

### Issue: "Database connection failed"

**Solution:**
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql

# If not running:
sudo systemctl start postgresql

# Verify connection:
psql -U wildguard -d wildguard -h localhost -c "SELECT 1;"
```

### Issue: "Module not found" errors

**Solution:**
```bash
# Make sure virtual environment is activated
source .venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

### Issue: Port 8000 or 5173 already in use

**Solution:**
```bash
# For port 8000
python manage.py runserver 8001

# For frontend, edit vite.config.ts to use different port
```

### Issue: PostGIS extension not found

**Solution:**
```bash
# Enable PostGIS in the database
sudo -u postgres psql -d wildguard -c "CREATE EXTENSION postgis;"
```

## What to Do Next

1. **Look at the frontend** - Open http://localhost:5173 and see the Command Center with demo incidents
2. **Test the API** - Use curl commands to create incidents, verify them, dispatch them
3. **Understand the workflow** - Each incident goes through states: REPORTED → UNDER_REVIEW → VERIFIED → DISPATCHED → RESPONDING → RESOLVED → CLOSED
4. **Read the documentation**:
   - [DEMO_DATA_SETUP.md](../DEMO_DATA_SETUP.md) - Understanding demo data
   - [docs/api.md](../docs/api.md) - Full API reference
   - [IMPLEMENTATION_GUIDE.md](../IMPLEMENTATION_GUIDE.md) - Project roadmap

## Current Project Status

✅ **Phase 2-3 Complete**: Backend API fully functional with:
- 11 API endpoints (auth, incidents, alerts)
- Risk scoring engine (0-100 scale)
- Status workflow validation
- JWT authentication
- Role-based access control
- Demo data seeding
- Comprehensive tests

⏳ **Phase 4 Next**: Frontend integration
- Connect React to real API data
- Build incident reporting form
- Implement map visualization

## File Structure

```
wildguard-kenya/
├── backend/                  # Django REST API
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/              # Django settings & URLs
│   ├── accounts/            # User model & auth
│   ├── communities/         # Communities & species
│   ├── incidents/           # Incident models & API
│   └── .venv/              # Python virtual environment
├── frontend/                # React + Vite
│   ├── package.json
│   ├── vite.config.ts
│   └── src/
├── docs/                    # Documentation
├── docker-compose.yml       # For future Docker deployment
└── README.md
```

---

**Need Help?** Check the documentation files or review the COMPLETION_SUMMARY.md for more details.
