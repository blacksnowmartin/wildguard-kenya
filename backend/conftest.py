"""
pytest configuration and shared fixtures for WildGuard Kenya backend tests.
"""
import pytest
from django.contrib.gis.geos import Point
from django.utils import timezone

from accounts.models import User
from communities.models import Community, WildlifeSpecies
from incidents.models import HWCIncident


@pytest.fixture
def test_user():
    """Create a test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        role=User.Role.COMMUNITY_MEMBER,
    )


@pytest.fixture
def supervisor_user():
    """Create a supervisor test user."""
    return User.objects.create_user(
        username='supervisor',
        email='supervisor@example.com',
        password='testpass123',
        role=User.Role.SUPERVISOR,
    )


@pytest.fixture
def ranger_user():
    """Create a ranger test user."""
    return User.objects.create_user(
        username='ranger',
        email='ranger@example.com',
        password='testpass123',
        role=User.Role.RANGER,
    )


@pytest.fixture
def species():
    """Create test wildlife species."""
    return WildlifeSpecies.objects.create(
        name='Elephant',
        danger_factor=75,
        is_active=True,
    )


@pytest.fixture
def community():
    """Create a test community."""
    return Community.objects.create(
        name='Test Community',
        county='Test County',
        center=Point(35.3, -1.35, srid=4326),
        is_active=True,
    )


@pytest.fixture
def incident(test_user, species, community):
    """Create a test incident."""
    return HWCIncident.objects.create(
        species=species,
        reporter=test_user,
        community=community,
        location=Point(35.3, -1.35, srid=4326),
        description='Test incident for validation',
        animal_count=3,
        severity='HIGH',
        status='REPORTED',
        event_time=timezone.now(),
        risk_score=65,
        risk_level='HIGH',
    )


@pytest.fixture
def critical_incident(test_user, species, community):
    """Create a critical test incident."""
    return HWCIncident.objects.create(
        species=species,
        reporter=test_user,
        community=community,
        location=Point(35.3, -1.35, srid=4326),
        description='Critical incident requiring immediate response',
        animal_count=8,
        severity='CRITICAL',
        status='REPORTED',
        event_time=timezone.now(),
        property_damage=True,
        risk_score=92,
        risk_level='CRITICAL',
    )


@pytest.fixture
def api_client():
    """Create a test API client."""
    from rest_framework.test import APIClient
    return APIClient()
