from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from communities.models import Community, WildlifeSpecies
from incidents.models import Alert, HWCIncident, Notification


class AlertApiTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(username='ops-user', password='secret', role='SUPERVISOR')
        self.community = Community.objects.create(name='Mara North', county='Narok')
        self.species = WildlifeSpecies.objects.create(name='Elephant', danger_factor=25)

    def test_critical_incident_creates_alert(self):
        self.client.force_authenticate(user=self.user)
        incident = HWCIncident.objects.create(
            species=self.species,
            community=self.community,
            reporter=self.user,
            location='POINT (35.12 -1.52)',
            description='Critical',
            animal_count=6,
            severity='CRITICAL',
            event_time=timezone.now(),
            risk_score=87,
            risk_level='CRITICAL',
        )
        alert = Alert.objects.create(
            incident=incident,
            title='CRITICAL HWC INCIDENT',
            message='Elephant incident near farmland.',
            priority='CRITICAL',
        )
        Notification.objects.create(recipient=self.user, alert=alert)
        response = self.client.get('/api/alerts/')
        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(response.data), 0)

        notifications = self.client.get('/api/notifications/')
        self.assertEqual(notifications.status_code, 200)
        self.assertGreater(len(notifications.data), 0)
