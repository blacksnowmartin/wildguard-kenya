#!/bin/bash
set -e

export PAGER=''
export PYTHONUNBUFFERED=1

cd /home/blacksnowmartin/wildguard-kenya

echo "╔════════════════════════════════════════════════════════════╗"
echo "║     WildGuard Kenya - Installation Starting                ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
source backend/.venv/bin/activate

echo "Step 1: Running migrations..."
cd backend
python manage.py migrate --noinput 2>&1 | grep -E "(Applying|OK|No changes|Operations)" || true
echo "✓ Migrations completed"
echo ""

echo "Step 2: Seeding demo data..."
python manage.py seed_demo_data --reset 2>&1 | tail -20
echo "✓ Demo data seeded"
echo ""

echo "Step 3: Creating superuser (admin/admin123)..."
python manage.py shell << 'PYEOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@wildguard.local',
        password='admin123',
        role='ADMIN'
    )
    print("✓ Superuser 'admin' created")
else:
    print("✓ Superuser 'admin' already exists")
PYEOF

echo ""
echo "✓ Installation Complete!"
echo ""
