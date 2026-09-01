from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
from django.utils import timezone
from datetime import timedelta

from communities.models import Community, WildlifeSpecies
from accounts.models import User
from incidents.models import HWCIncident, IncidentStatusHistory, RiskAssessment


class Command(BaseCommand):
    help = 'Seed the database with demo data for testing and demonstrations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete all existing demo data before seeding',
        )

    def handle(self, *args, **options):
        if options['reset']:
            self.reset_data()

        self.stdout.write('Seeding demo data...')
        self.seed_species()
        self.seed_communities()
        self.seed_users()
        self.seed_incidents()
        self.stdout.write(self.style.SUCCESS('✓ Demo data seeded successfully'))

    def reset_data(self):
        """Delete all demo data."""
        self.stdout.write('Resetting all data...')
        HWCIncident.objects.all().delete()
        WildlifeSpecies.objects.all().delete()
        Community.objects.all().delete()
        User.objects.filter(username__startswith='demo_').delete()
        self.stdout.write(self.style.SUCCESS('✓ Data reset'))

    def seed_species(self):
        """Create wildlife species."""
        species_data = [
            ('Elephant', 75),
            ('Lion', 80),
            ('Buffalo', 70),
            ('Hippo', 65),
            ('Leopard', 60),
            ('Hyena', 45),
            ('Wild Dog', 50),
            ('Rhino', 85),
        ]

        for name, danger_factor in species_data:
            WildlifeSpecies.objects.get_or_create(
                name=name,
                defaults={'danger_factor': danger_factor, 'is_active': True},
            )
        self.stdout.write(f'✓ Seeded {len(species_data)} wildlife species')

    def seed_communities(self):
        """Create communities across Kenyan counties."""
        communities_data = [
            ('Mara North', 'Narok'),
            ('Mara South', 'Narok'),
            ('Kajiado East', 'Kajiado'),
            ('Kajiado West', 'Kajiado'),
            ('Tsavo West', 'Taita Taveta'),
            ('Tsavo East', 'Taita Taveta'),
            ('Lake Naivasha', 'Nakuru'),
            ('Hell\'s Gate', 'Nakuru'),
            ('Amboseli', 'Kajiado'),
            ('Samburu', 'Samburu'),
            ('Mount Kenya', 'Nyeri'),
            ('Kora', 'Tana River'),
            ('Rahole', 'Tana River'),
            ('Mombasa', 'Mombasa'),
            ('Diani', 'Kwale'),
            ('Kilifi', 'Kilifi'),
            ('Lake Turkana', 'Turkana'),
            ('Laikipia', 'Laikipia'),
            ('Ngorongoro', 'Arusha'),
            ('Serengeti', 'Mara'),
        ]

        # Approximate coordinates (center points for Kenyan areas)
        coords = {
            'Mara North': (-1.35, 35.30),
            'Mara South': (-1.65, 35.25),
            'Kajiado East': (-2.05, 36.70),
            'Kajiado West': (-2.30, 36.20),
            'Tsavo West': (-3.05, 37.75),
            'Tsavo East': (-3.30, 38.90),
            'Lake Naivasha': (-0.75, 36.40),
            'Hell\'s Gate': (-0.50, 36.35),
            'Amboseli': (-2.65, 37.25),
            'Samburu': (0.50, 37.50),
            'Mount Kenya': (-0.15, 37.30),
            'Kora': (-1.15, 39.20),
            'Rahole': (-1.35, 39.85),
            'Mombasa': (-4.05, 39.65),
            'Diani': (-4.35, 39.55),
            'Kilifi': (-3.62, 39.85),
            'Lake Turkana': (2.30, 36.50),
            'Laikipia': (-0.15, 36.70),
            'Ngorongoro': (-3.15, 35.50),
            'Serengeti': (-2.20, 34.80),
        }

        for name, county in communities_data:
            lat, lon = coords.get(name, (-1.0, 36.0))
            Community.objects.get_or_create(
                name=name,
                county=county,
                defaults={
                    'center': Point(lon, lat, srid=4326),
                    'is_active': True,
                },
            )
        self.stdout.write(f'✓ Seeded {len(communities_data)} communities')

    def seed_users(self):
        """Create demo users with different roles."""
        users_data = [
            ('demo_alex_mwangi', 'Alex', 'Mwangi', User.Role.SUPERVISOR, '+254712345001'),
            ('demo_jane_kipchoge', 'Jane', 'Kipchoge', User.Role.RANGER, '+254712345002'),
            ('demo_david_muthui', 'David', 'Muthui', User.Role.RANGER, '+254712345003'),
            ('demo_sarah_omondi', 'Sarah', 'Omondi', User.Role.RANGER, '+254712345004'),
            ('demo_grace_kisumu', 'Grace', 'Kisumu', User.Role.COMMUNITY_MEMBER, '+254712345005'),
            ('demo_peter_wanjiru', 'Peter', 'Wanjiru', User.Role.COMMUNITY_MEMBER, '+254712345006'),
            ('demo_amina_yusuf', 'Amina', 'Yusuf', User.Role.ADMIN, '+254712345007'),
        ]

        for username, first_name, last_name, role, phone in users_data:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'role': role,
                    'phone_number': phone,
                    'is_staff': role in (User.Role.ADMIN, User.Role.SUPERVISOR),
                    'is_active': True,
                },
            )
            # Set a default password for all demo users
            if created:
                user.set_password('password')
                user.save()
        self.stdout.write(f'✓ Seeded {len(users_data)} users')

    def seed_incidents(self):
        """Create demo incidents with various risk levels and statuses."""
        elephant = WildlifeSpecies.objects.get(name='Elephant')
        lion = WildlifeSpecies.objects.get(name='Lion')
        buffalo = WildlifeSpecies.objects.get(name='Buffalo')
        hippo = WildlifeSpecies.objects.get(name='Hippo')

        mara_north = Community.objects.get(name='Mara North')
        kajiado_east = Community.objects.get(name='Kajiado East')
        tsavo_west = Community.objects.get(name='Tsavo West')
        lake_naivasha = Community.objects.get(name='Lake Naivasha')
        amboseli = Community.objects.get(name='Amboseli')

        reporter_community = User.objects.get(username='demo_grace_kisumu')
        reporter_ranger = User.objects.get(username='demo_jane_kipchoge')
        supervisor = User.objects.get(username='demo_alex_mwangi')
        ranger1 = User.objects.get(username='demo_david_muthui')

        now = timezone.now()
        incidents_data = [
            # Critical incident - REPORTED (fresh, high risk)
            {
                'species': elephant,
                'reporter': reporter_community,
                'community': mara_north,
                'location': Point(35.35, -1.35, srid=4326),
                'description': 'DEMO: Large herd of 8 elephants reported within 500m of cultivated land near Mara North boundary.',
                'animal_count': 8,
                'severity': HWCIncident.Severity.CRITICAL,
                'status': HWCIncident.Status.REPORTED,
                'event_time': now - timedelta(minutes=15),
                'property_damage': True,
                'risk_score': 95,
                'risk_level': HWCIncident.Severity.CRITICAL,
            },
            # Critical incident - VERIFIED (ready for response)
            {
                'species': lion,
                'reporter': reporter_ranger,
                'community': kajiado_east,
                'location': Point(36.70, -2.05, srid=4326),
                'description': 'DEMO: Lion pride of 5 observed near livestock enclosure. Fresh tracks indicate recent activity.',
                'animal_count': 5,
                'severity': HWCIncident.Severity.CRITICAL,
                'status': HWCIncident.Status.VERIFIED,
                'event_time': now - timedelta(hours=1, minutes=30),
                'property_damage': False,
                'risk_score': 88,
                'risk_level': HWCIncident.Severity.CRITICAL,
                'verified': True,
            },
            # High risk - DISPATCHED (response underway)
            {
                'species': buffalo,
                'reporter': reporter_community,
                'community': tsavo_west,
                'location': Point(37.75, -3.05, srid=4326),
                'description': 'DEMO: Herd of buffalo (20+) blocking main water access path. Livestock concern.',
                'animal_count': 20,
                'severity': HWCIncident.Severity.HIGH,
                'status': HWCIncident.Status.DISPATCHED,
                'event_time': now - timedelta(hours=2, minutes=45),
                'property_damage': True,
                'risk_score': 70,
                'risk_level': HWCIncident.Severity.HIGH,
                'verified': True,
            },
            # High risk - RESPONDING (ranger en route)
            {
                'species': hippo,
                'reporter': reporter_community,
                'community': lake_naivasha,
                'location': Point(36.40, -0.75, srid=4326),
                'description': 'DEMO: Hippo sighting near residential water collection point. Safety concern at dusk.',
                'animal_count': 2,
                'severity': HWCIncident.Severity.HIGH,
                'status': HWCIncident.Status.RESPONDING,
                'event_time': now - timedelta(hours=3, minutes=20),
                'property_damage': False,
                'risk_score': 65,
                'risk_level': HWCIncident.Severity.HIGH,
                'verified': True,
            },
            # Moderate risk - RESOLVED (action taken)
            {
                'species': elephant,
                'reporter': reporter_community,
                'community': amboseli,
                'location': Point(37.25, -2.65, srid=4326),
                'description': 'DEMO: Single elephant spotted near community edge at dawn. Moved away after alert.',
                'animal_count': 1,
                'severity': HWCIncident.Severity.MODERATE,
                'status': HWCIncident.Status.RESOLVED,
                'event_time': now - timedelta(hours=5, minutes=10),
                'property_damage': False,
                'risk_score': 40,
                'risk_level': HWCIncident.Severity.MODERATE,
                'verified': True,
            },
            # Moderate risk - UNDER_REVIEW
            {
                'species': buffalo,
                'reporter': reporter_community,
                'community': mara_south,
                'location': Point(35.25, -1.65, srid=4326),
                'description': 'DEMO: Buffalo tracks identified in crop field. No current sighting.',
                'animal_count': 1,
                'severity': HWCIncident.Severity.MODERATE,
                'status': HWCIncident.Status.UNDER_REVIEW,
                'event_time': now - timedelta(hours=6, minutes=30),
                'property_damage': True,
                'risk_score': 45,
                'risk_level': HWCIncident.Severity.MODERATE,
                'verified': False,
            },
            # Low risk - CLOSED
            {
                'species': hippo,
                'reporter': reporter_ranger,
                'community': kajiado_west,
                'location': Point(36.20, -2.30, srid=4326),
                'description': 'DEMO: Hippo observed at water hole during daylight. No threat to community.',
                'animal_count': 1,
                'severity': HWCIncident.Severity.LOW,
                'status': HWCIncident.Status.CLOSED,
                'event_time': now - timedelta(hours=12),
                'property_damage': False,
                'risk_score': 20,
                'risk_level': HWCIncident.Severity.LOW,
                'verified': True,
            },
        ]

        created_count = 0
        for incident_data in incidents_data:
            incident, created = HWCIncident.objects.get_or_create(
                reporter=incident_data['reporter'],
                event_time=incident_data['event_time'],
                species=incident_data['species'],
                defaults=incident_data,
            )
            if created:
                # Create status history
                IncidentStatusHistory.objects.create(
                    incident=incident,
                    actor=incident_data['reporter'],
                    old_status='',
                    new_status=HWCIncident.Status.REPORTED,
                )
                # Create risk assessment
                RiskAssessment.objects.create(
                    incident=incident,
                    score=incident_data['risk_score'],
                    level=incident_data['risk_level'],
                    reasons=[
                        f"Species danger factor +{incident_data['species'].danger_factor}",
                        "Settlement proximity factor" if incident_data['property_damage'] else "Remote location",
                    ],
                    rules_version='v1',
                )
                created_count += 1

        self.stdout.write(f'✓ Seeded {created_count} demo incidents')
