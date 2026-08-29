from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from communities.models import Community, WildlifeSpecies
from incidents.models import HWCIncident


class IncidentApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='member-one',
            password='test-password',
            role='COMMUNITY_MEMBER',
        )
        self.ranger = get_user_model().objects.create_user(
            username='ranger-one',
            password='test-password',
            role='RANGER',
        )
        self.community = Community.objects.create(name='Mara North', county='Narok')
        self.species = WildlifeSpecies.objects.create(name='Elephant', danger_factor=25)

    def test_client_can_create_incident(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(
            '/api/incidents/',
            {
                'species': self.species.id,
                'community': self.community.id,
                'animal_count': 3,
                'severity': 'HIGH',
                'description': 'Elephants near farmland.',
                'event_time': timezone.now().isoformat(),
                'latitude': -1.523,
                'longitude': 35.121,
                'property_damage': True,
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(HWCIncident.objects.count(), 1)

    def test_ranger_can_verify_incident(self):
        incident = HWCIncident.objects.create(
            species=self.species,
            community=self.community,
            reporter=self.user,
            location='POINT (35.121 -1.523)',
            description='Test incident',
            animal_count=2,
            severity='HIGH',
            event_time=timezone.now(),
            risk_score=0,
            risk_level='LOW',
        )
        self.client.force_authenticate(user=self.ranger)
        response = self.client.post(f'/api/incidents/{incident.pk}/action/', {'action': 'verify'}, format='json')
        self.assertEqual(response.status_code, 200)
        incident.refresh_from_db()
        self.assertEqual(incident.status, HWCIncident.Status.VERIFIED)
