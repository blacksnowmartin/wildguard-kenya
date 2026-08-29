from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APITestCase

from communities.models import Community, WildlifeSpecies
from incidents.models import HWCIncident
from incidents.services import validate_status_transition


class StatusTransitionTests(APITestCase):
    def test_valid_transitions_match_workflow(self):
        self.assertTrue(validate_status_transition(HWCIncident.Status.REPORTED, HWCIncident.Status.UNDER_REVIEW))
        self.assertTrue(validate_status_transition(HWCIncident.Status.UNDER_REVIEW, HWCIncident.Status.VERIFIED))
        self.assertTrue(validate_status_transition(HWCIncident.Status.VERIFIED, HWCIncident.Status.DISPATCHED))
        self.assertTrue(validate_status_transition(HWCIncident.Status.DISPATCHED, HWCIncident.Status.RESPONDING))
        self.assertTrue(validate_status_transition(HWCIncident.Status.RESPONDING, HWCIncident.Status.RESOLVED))
        self.assertTrue(validate_status_transition(HWCIncident.Status.RESOLVED, HWCIncident.Status.CLOSED))

    def test_invalid_transition_is_rejected(self):
        self.assertFalse(validate_status_transition(HWCIncident.Status.REPORTED, HWCIncident.Status.RESOLVED))

    def test_critical_alert_is_created_once(self):
        user = get_user_model().objects.create_user(username='m', password='x', role='COMMUNITY_MEMBER')
        community = Community.objects.create(name='Mara North', county='Narok')
        species = WildlifeSpecies.objects.create(name='Elephant', danger_factor=25)
        incident = HWCIncident.objects.create(
            species=species,
            community=community,
            reporter=user,
            location='POINT (35.12 -1.52)',
            description='Critical incident',
            animal_count=6,
            severity='CRITICAL',
            event_time=timezone.now(),
            risk_score=87,
            risk_level='CRITICAL',
            status=HWCIncident.Status.REPORTED,
        )
        incident.risk_level = HWCIncident.Severity.CRITICAL
        incident.save(update_fields=['risk_level'])

        from incidents.services import create_critical_alert

        alert = create_critical_alert(incident)
        duplicate = create_critical_alert(incident)

        self.assertIsNotNone(alert)
        self.assertIsNone(duplicate)
