#!/bin/bash
# WildGuard Kenya - Database and Demo Data Setup Script
# Run this script to initialize the database with migrations and demo data

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     WildGuard Kenya - Complete Setup Script               ║"
echo "╚════════════════════════════════════════════════════════════╝"

cd "$(dirname "$0")"

# Check if backend directory exists
if [ ! -d "backend" ]; then
    echo "❌ Error: backend directory not found"
    exit 1
fi

cd backend

# Step 1: Setup Python environment
echo ""
echo "📦 Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source .venv/bin/activate

# Step 2: Install dependencies
echo ""
echo "📚 Installing dependencies..."
pip install -q -r requirements.txt --upgrade
echo "✓ Dependencies installed"

# Step 3: Check database connection
echo ""
echo "🗄️  Verifying database connection..."

# Load .env file if it exists
if [ -f "../.env" ]; then
    export $(cat ../.env | xargs)
fi

# Default values if .env doesn't exist
POSTGRES_HOST=${POSTGRES_HOST:-localhost}
POSTGRES_PORT=${POSTGRES_PORT:-5432}
POSTGRES_DB=${POSTGRES_DB:-wildguard}
POSTGRES_USER=${POSTGRES_USER:-wildguard}

# Try to connect to database
if ! python3 -c "
import psycopg
try:
    conn = psycopg.connect(f'host=$POSTGRES_HOST port=$POSTGRES_PORT dbname=postgres user=$POSTGRES_USER')
    conn.close()
    print('✓ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
" 2>/dev/null; then
    echo "❌ Cannot connect to PostgreSQL at $POSTGRES_HOST:$POSTGRES_PORT"
    echo "   Please ensure PostgreSQL is running and accessible."
    exit 1
fi

# Step 4: Run migrations
echo ""
echo "🔄 Running migrations..."
python manage.py migrate --noinput
echo "✓ Migrations completed"

# Step 5: Seed demo data
echo ""
echo "🌱 Seeding demo data..."
python manage.py seed_demo_data --reset
echo "✓ Demo data seeded"

# Step 6: Create superuser
echo ""
echo "👤 Creating superuser (demo_admin)..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='demo_admin').exists():
    User.objects.create_superuser(
        username='demo_admin',
        email='admin@demo.wildguard',
        password='admin123',
        role=User.Role.ADMIN
    )
    print("✓ Superuser 'demo_admin' created (password: admin123)")
else:
    print("✓ Superuser 'demo_admin' already exists")
EOF

# Step 7: Run collectstatic (for development)
echo ""
echo "📄 Collecting static files..."
python manage.py collectstatic --noinput -c 2>/dev/null || true
echo "✓ Static files collected"

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║             ✓ Setup Complete!                             ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║ To start the development server:                           ║"
echo "║   cd backend                                               ║"
echo "║   source .venv/bin/activate                                ║"
echo "║   python manage.py runserver                               ║"
echo "║                                                            ║"
echo "║ To run E2E tests:                                          ║"
echo "║   python run_e2e_tests.py                                  ║"
echo "║                                                            ║"
echo "║ Default users:                                             ║"
echo "║   demo_admin (ADMIN) - password: admin123                  ║"
echo "║   demo_alex_mwangi (SUPERVISOR) - password: password       ║"
echo "║   demo_jane_kipchoge (RANGER) - password: password         ║"
echo "║   demo_grace_kisumu (COMMUNITY_MEMBER) - password: password║"
echo "╚════════════════════════════════════════════════════════════╝"
