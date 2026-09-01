import pytest
from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status

from accounts.models import User
from communities.models import Community, WildlifeSpecies
from incidents.models import HWCIncident, IncidentStatusHistory, RiskAssessment, Alert
from incidents.services import calculate_hwc_risk, transition_incident_status, validate_status_transition


class TestRiskCalculationEngine:
    """Test the HWC risk calculation engine."""

    def test_base_species_danger_factor(self):
        """Test that species danger factor is used as base score."""
        result = calculate_hwc_risk(species_danger_factor=50)
        assert result['score'] == 50
        assert result['risk_level'] == 'MODERATE'

    def test_settlement_proximity_bonus(self):
        """Test +25 bonus for settlement within 2km."""
        result = calculate_hwc_risk(species_danger_factor=30, settlement_within_2km=True)
        assert result['score'] == 55
        assert 'Settlement within 2 km' in result['reasons']

    def test_nighttime_bonus(self):
        """Test +10 bonus for night-time incidents."""
        result = calculate_hwc_risk(species_danger_factor=30, is_night=True)
        assert result['score'] == 40
        assert 'Night-time event' in result['reasons']

    def test_multiple_animals_bonus(self):
        """Test +10 bonus for multiple animals."""
        result = calculate_hwc_risk(species_danger_factor=30, animal_count=5)
        assert result['score'] == 40
        assert 'Multiple animals' in result['reasons']

    def test_previous_incidents_bonus(self):
        """Test +15 bonus for previous nearby incidents."""
        result = calculate_hwc_risk(species_danger_factor=30, previous_nearby_incidents=2)
        assert result['score'] == 45
        assert 'Previous nearby incidents' in result['reasons']

    def test_property_damage_bonus(self):
        """Test +15 bonus for property damage."""
        result = calculate_hwc_risk(species_danger_factor=30, property_damage=True)
        assert result['score'] == 45
        assert 'Crop or property damage' in result['reasons']

    def test_combined_factors(self):
        """Test combined risk factors."""
        result = calculate_hwc_risk(
            species_danger_factor=30,
            settlement_within_2km=True,
            is_night=True,
            animal_count=3,
            property_damage=True,
        )
        # 30 + 25 + 10 + 10 + 15 = 90
        assert result['score'] == 90
        assert result['risk_level'] == 'HIGH'

    def test_score_capped_at_100(self):
        """Test that score is capped at 100."""
        result = calculate_hwc_risk(
            species_danger_factor=80,
            settlement_within_2km=True,
            is_night=True,
            animal_count=10,
            previous_nearby_incidents=5,
            property_damage=True,
        )
        assert result['score'] == 100
        assert result['risk_level'] == 'CRITICAL'

    def test_risk_level_boundaries(self):
        """Test risk level classification."""
        assert calculate_hwc_risk(species_danger_factor=20)['risk_level'] == 'LOW'
        assert calculate_hwc_risk(species_danger_factor=35)['risk_level'] == 'MODERATE'
        assert calculate_hwc_risk(species_danger_factor=60)['risk_level'] == 'HIGH'
        assert calculate_hwc_risk(species_danger_factor=80)['risk_level'] == 'CRITICAL'

    def test_reasons_included(self):
        """Test that reasons list is populated."""
        result = calculate_hwc_risk(
            species_danger_factor=30,
            settlement_within_2km=True,
            animal_count=2,
        )
        assert len(result['reasons']) >= 3
        assert 'Species danger factor' in result['reasons'][0]


class TestStatusTransitions:
    """Test incident status transition logic."""

    @pytest.fixture
    def user(self, django_db):
        return User.objects.create_user(username='testuser', password='pass')

    def test_valid_transitions(self):
        """Test that valid transitions are accepted."""
        assert validate_status_transition('REPORTED', 'UNDER_REVIEW') is True
        assert validate_status_transition('UNDER_REVIEW', 'VERIFIED') is True
        assert validate_status_transition('VERIFIED', 'DISPATCHED') is True
        assert validate_status_transition('DISPATCHED', 'RESPONDING') is True
        assert validate_status_transition('RESPONDING', 'RESOLVED') is True
        assert validate_status_transition('RESOLVED', 'CLOSED') is True

    def test_invalid_transitions(self):
        """Test that invalid transitions are rejected."""
        assert validate_status_transition('REPORTED', 'VERIFIED') is False
        assert validate_status_transition('VERIFIED', 'UNDER_REVIEW') is False
        assert validate_status_transition('RESOLVED', 'RESPONDING') is False
        assert validate_status_transition('CLOSED', 'RESOLVED') is False

    def test_transition_from_under_review_to_rejected(self):
        """Test rejection path."""
        assert validate_status_transition('UNDER_REVIEW', 'REJECTED') is True

    @pytest.mark.django_db
    def test_transition_creates_history(self, user):
        """Test that status transitions create history records."""
        species = WildlifeSpecies.objects.create(name='Elephant', danger_factor=75)
        community = Community.objects.create(name='Test Community', county='Test County')
        
        incident = HWCIncident.objects.create(
            species=species,
            reporter=user,
            community=community,
            location=Point(0, 0, srid=4326),
            description='Test incident',
            severity='HIGH',
            status='REPORTED',
            event_time=timezone.now(),
        )

        transition_incident_status(incident, 'UNDER_REVIEW', user, notes='Test note')

        assert incident.status == 'UNDER_REVIEW'
        history = IncidentStatusHistory.objects.filter(incident=incident).last()
        assert history.old_status == 'REPORTED'
        assert history.new_status == 'UNDER_REVIEW'
        assert history.notes == 'Test note'


@pytest.mark.django_db
class TestIncidentModel:
    """Test incident model."""

    @pytest.fixture
    def setup_data(self):
        """Create base test data."""
        user = User.objects.create_user(username='reporter', password='pass', role=User.Role.COMMUNITY_MEMBER)
        species = WildlifeSpecies.objects.create(name='Elephant', danger_factor=75)
        community = Community.objects.create(name='Test Community', county='Test County')
        return user, species, community

    def test_incident_creation(self, setup_data):
        """Test basic incident creation."""
        user, species, community = setup_data
        
        incident = HWCIncident.objects.create(
            species=species,
            reporter=user,
            community=community,
            location=Point(35.3, -1.35, srid=4326),
            description='Test elephant incident',
            animal_count=3,
            severity='HIGH',
            status='REPORTED',
            event_time=timezone.now(),
        )

        assert incident.id is not None
        assert incident.species == species
        assert incident.reporter == user
        assert incident.status == 'REPORTED'

    def test_incident_risk_score(self, setup_data):
        """Test that risk score is stored correctly."""
        user, species, community = setup_data
        
        incident = HWCIncident.objects.create(
            species=species,
            reporter=user,
            community=community,
            location=Point(35.3, -1.35, srid=4326),
            description='Test incident',
            severity='CRITICAL',
            status='REPORTED',
            event_time=timezone.now(),
            risk_score=85,
            risk_level='CRITICAL',
        )

        assert incident.risk_score == 85
        assert incident.risk_level == 'CRITICAL'

    def test_incident_geographic_query(self, setup_data):
        """Test geographic queries on incident location."""
        user, species, community = setup_data
        
        incident = HWCIncident.objects.create(
            species=species,
            reporter=user,
            community=community,
            location=Point(35.3, -1.35, srid=4326),
            description='Test incident',
            severity='HIGH',
            status='REPORTED',
            event_time=timezone.now(),
        )

        # Query by location
        from django.contrib.gis.db.models.functions import Distance
        from django.db.models import F
        
        search_point = Point(35.3, -1.35, srid=4326)
        incidents = HWCIncident.objects.annotate(
            distance=Distance('location', search_point)
        ).filter(distance__lte=1000)  # Within 1km
        
        assert incident in incidents


@pytest.mark.django_db
class TestAlertGeneration:
    """Test alert generation for critical incidents."""

    @pytest.fixture
    def setup_data(self):
        """Create base test data."""
        user = User.objects.create_user(username='reporter', password='pass')
        species = WildlifeSpecies.objects.create(name='Lion', danger_factor=80)
        community = Community.objects.create(name='Test Community', county='Test County')
        return user, species, community

    def test_critical_incident_creates_alert(self, setup_data):
        """Test that critical incidents generate alerts."""
        user, species, community = setup_data
        
        from incidents.services import create_critical_alert
        
        incident = HWCIncident.objects.create(
            species=species,
            reporter=user,
            community=community,
            location=Point(35.3, -1.35, srid=4326),
            description='Critical incident',
            severity='CRITICAL',
            status='REPORTED',
            event_time=timezone.now(),
            risk_score=95,
            risk_level='CRITICAL',
        )

        alert = create_critical_alert(incident)
        
        assert alert is not None
        assert alert.incident == incident
        assert alert.priority == 'CRITICAL'

    def test_non_critical_incident_no_alert(self, setup_data):
        """Test that non-critical incidents don't generate alerts."""
        user, species, community = setup_data
        
        from incidents.services import create_critical_alert
        
        incident = HWCIncident.objects.create(
            species=species,
            reporter=user,
            community=community,
            location=Point(35.3, -1.35, srid=4326),
            description='Moderate incident',
            severity='MODERATE',
            status='REPORTED',
            event_time=timezone.now(),
            risk_score=40,
            risk_level='MODERATE',
        )

        alert = create_critical_alert(incident)
        
        assert alert is None

    def test_alert_idempotency(self, setup_data):
        """Test that alert creation is idempotent."""
        user, species, community = setup_data
        
        from incidents.services import create_critical_alert
        
        incident = HWCIncident.objects.create(
            species=species,
            reporter=user,
            community=community,
            location=Point(35.3, -1.35, srid=4326),
            description='Critical incident',
            severity='CRITICAL',
            status='REPORTED',
            event_time=timezone.now(),
            risk_score=95,
            risk_level='CRITICAL',
        )

        alert1 = create_critical_alert(incident)
        alert2 = create_critical_alert(incident)
        
        assert alert1.id == alert2.id if alert1 and alert2 else True
        assert Alert.objects.filter(incident=incident).count() == 1
