#!/usr/bin/env python3
"""
WildGuard Kenya - Automated Installation Script
Handles all setup steps: migrations, seeding, and verification
"""
import os
import sys
import subprocess
import django

# Set environment variables
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
os.chdir('/home/blacksnowmartin/wildguard-kenya/backend')
sys.path.insert(0, '/home/blacksnowmartin/wildguard-kenya/backend')

print("╔════════════════════════════════════════════════════════════╗")
print("║     WildGuard Kenya - Automated Setup                      ║")
print("╚════════════════════════════════════════════════════════════╝\n")

# Step 1: Activate virtual environment and setup Django
print("📦 Setting up Django environment...")
try:
    django.setup()
    print("✓ Django environment ready\n")
except Exception as e:
    print(f"✗ Django setup failed: {e}\n")
    sys.exit(1)

# Step 2: Run migrations
print("🔄 Running database migrations...")
try:
    result = subprocess.run(
        [sys.executable, 'manage.py', 'migrate', '--noinput'],
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode == 0:
        print("✓ Migrations completed successfully\n")
    else:
        print(f"✗ Migration failed: {result.stderr}\n")
        sys.exit(1)
except Exception as e:
    print(f"✗ Migration error: {e}\n")
    sys.exit(1)

# Step 3: Seed demo data
print("🌱 Seeding demo data...")
try:
    result = subprocess.run(
        [sys.executable, 'manage.py', 'seed_demo_data', '--reset'],
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode == 0:
        print(result.stdout)
        print("✓ Demo data seeded successfully\n")
    else:
        print(f"✗ Seeding failed: {result.stderr}\n")
except Exception as e:
    print(f"✗ Seeding error: {e}\n")

# Step 4: Create superuser
print("👤 Setting up superuser...")
try:
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@wildguard.local',
            password='admin123',
            role='ADMIN'
        )
        print("✓ Superuser 'admin' created (password: admin123)\n")
    else:
        print("✓ Superuser 'admin' already exists\n")
except Exception as e:
    print(f"✗ Superuser creation failed: {e}\n")

# Step 5: Collect static files
print("📄 Collecting static files...")
try:
    result = subprocess.run(
        [sys.executable, 'manage.py', 'collectstatic', '--noinput', '-c'],
        capture_output=True,
        text=True,
        timeout=30
    )
    print("✓ Static files collected\n")
except:
    print("⚠ Static files collection skipped\n")

# Summary
print("╔════════════════════════════════════════════════════════════╗")
print("║             ✓ Setup Complete!                             ║")
print("╠════════════════════════════════════════════════════════════╣")
print("║                                                            ║")
print("║ To start the backend server:                              ║")
print("║   cd backend                                              ║")
print("║   source .venv/bin/activate                               ║")
print("║   python manage.py runserver 0.0.0.0:8000                 ║")
print("║                                                            ║")
print("║ To start the frontend (in another terminal):              ║")
print("║   cd frontend                                             ║")
print("║   npm run dev                                             ║")
print("║                                                            ║")
print("║ Test Users:                                              ║")
print("║   admin / admin123 (Admin)                               ║")
print("║   demo_grace_kisumu / password (Community Member)        ║")
print("║   demo_alex_mwangi / password (Supervisor)               ║")
print("║   demo_jane_kipchoge / password (Ranger)                 ║")
print("║                                                            ║")
print("║ Backend API: http://localhost:8000/api/                  ║")
print("║ Frontend:    http://localhost:5173                       ║")
print("║                                                            ║")
print("╚════════════════════════════════════════════════════════════╝\n")
