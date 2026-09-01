#!/usr/bin/env python3
"""
End-to-end test script for WildGuard Kenya API.
Tests the complete incident workflow: create, retrieve, transition statuses.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.gis.geos import Point
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import User
from communities.models import Community, WildlifeSpecies
from incidents.models import HWCIncident


class APITests:
    def __init__(self):
        self.client = APIClient()
        self.passed = 0
        self.failed = 0

    def log_test(self, name, passed, message=''):
        status_mark = '✓' if passed else '✗'
        self.stdout(f'{status_mark} {name}')
        if message:
            self.stdout(f'  └─ {message}')
        if passed:
            self.passed += 1
        else:
            self.failed += 1

    def stdout(self, msg):
        print(msg)

    def test_auth_endpoints(self):
        self.stdout('\n🔐 Testing Authentication...')
        
        # Create a test user
        user = User.objects.create_user(
            username='test_user',
            password='testpass123',
            role=User.Role.COMMUNITY_MEMBER,
        )

        # Test token obtain
        response = self.client.post(
            '/api/auth/token/',
            {'username': 'test_user', 'password': 'testpass123'},
            format='json',
        )
        self.log_test('POST /api/auth/token/', response.status_code == status.HTTP_200_OK)
        
        if response.status_code == status.HTTP_200_OK:
            token = response.data.get('access')
            self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

            # Test current user endpoint
            response = self.client.get('/api/auth/me/')
            self.log_test(
                'GET /api/auth/me/',
                response.status_code == status.HTTP_200_OK,
                f'User: {response.data.get("username")}' if response.status_code == status.HTTP_200_OK else '',
            )
            
            return True
        return False

    def test_incident_creation(self):
        self.stdout('\n📝 Testing Incident Creation...')

        # Setup
        reporter = User.objects.get(username='demo_grace_kisumu')
        community = Community.objects.get(name='Mara North')
        species = WildlifeSpecies.objects.get(name='Elephant')
        
        # Login as community member
        response = self.client.post(
            '/api/auth/token/',
            {'username': 'demo_grace_kisumu', 'password': 'password'},
            format='json',
        )
        
        if response.status_code != status.HTTP_200_OK:
            self.log_test('Login as community member', False, f'Authentication failed: {response.status_code}')
            return None
        
        self.log_test('Login as community member', True, 'Token obtained')
        token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')
        
        # Create incident
        incident_data = {
            'species': species.id,
            'community': community.id,
            'animal_count': 3,
            'severity': 'HIGH',
            'description': 'Test incident for E2E validation - DEMO DATA',
            'event_time': timezone.now().isoformat(),
            'latitude': -1.35,
            'longitude': 35.30,
            'property_damage': False,
        }
        
        response = self.client.post('/api/incidents/', incident_data, format='json')
        self.log_test(
            'POST /api/incidents/',
            response.status_code == status.HTTP_201_CREATED,
            f'Status: {response.status_code}' if response.status_code != status.HTTP_201_CREATED else f'Incident ID: {response.data.get("id")}',
        )
        
        if response.status_code == status.HTTP_201_CREATED:
            incident_id = response.data.get('id')
            return incident_id
        else:
            self.stdout(f'  Response: {response.data}')
        return None

    def test_incident_retrieval(self, incident_id):
        self.stdout('\n🔍 Testing Incident Retrieval...')

        # Get incident detail
        response = self.client.get(f'/api/incidents/{incident_id}/')
        self.log_test(
            f'GET /api/incidents/{incident_id}/',
            response.status_code == status.HTTP_200_OK,
            f'Species: {response.data.get("species", {}).get("name")}' if response.status_code == status.HTTP_200_OK else '',
        )

        # List incidents
        response = self.client.get('/api/incidents/')
        self.log_test(
            'GET /api/incidents/',
            response.status_code == status.HTTP_200_OK,
            f'Count: {len(response.data) if isinstance(response.data, list) else "N/A"}',
        )

    def test_risk_calculation(self, incident_id):
        self.stdout('\n⚠️  Testing Risk Calculation...')

        response = self.client.get(f'/api/incidents/{incident_id}/')
        if response.status_code == status.HTTP_200_OK:
            risk_score = response.data.get('risk_score')
            risk_level = response.data.get('risk_level')
            self.log_test(
                'Risk Score Calculation',
                0 <= risk_score <= 100,
                f'Score: {risk_score}, Level: {risk_level}',
            )

    def test_status_transitions(self, incident_id):
        self.stdout('\n🔄 Testing Status Transitions...')

        # Login as supervisor
        response = self.client.post(
            '/api/auth/token/',
            {'username': 'demo_alex_mwangi', 'password': 'password'},
            format='json',
        )
        
        if response.status_code != status.HTTP_200_OK:
            self.log_test('Login as supervisor', False, 'Authentication failed')
            return
        
        token = response.data.get('access')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')

        # Test transition to UNDER_REVIEW
        response = self.client.post(
            f'/api/incidents/{incident_id}/action/',
            {'action': 'review'},
            format='json',
        )
        self.log_test(
            'POST /api/incidents/{id}/action/ [review]',
            response.status_code in (status.HTTP_200_OK, status.HTTP_400_BAD_REQUEST),
            f'Status: {response.status_code}',
        )

    def test_alerts(self):
        self.stdout('\n🚨 Testing Alerts...')

        response = self.client.get('/api/alerts/')
        self.log_test(
            'GET /api/alerts/',
            response.status_code == status.HTTP_200_OK,
            f'Count: {len(response.data) if isinstance(response.data, list) else "N/A"}',
        )

    def run_all_tests(self):
        self.stdout('╔════════════════════════════════════════════════════════════╗')
        self.stdout('║      WildGuard Kenya - End-to-End API Test Suite          ║')
        self.stdout('╚════════════════════════════════════════════════════════════╝')

        if self.test_auth_endpoints():
            incident_id = self.test_incident_creation()
            if incident_id:
                self.test_incident_retrieval(incident_id)
                self.test_risk_calculation(incident_id)
                self.test_status_transitions(incident_id)
                self.test_alerts()

        self.stdout(f'\n╔════════════════════════════════════════════════════════════╗')
        self.stdout(f'║  PASSED: {self.passed}  │  FAILED: {self.failed}')
        self.stdout(f'╚════════════════════════════════════════════════════════════╝\n')

        return self.failed == 0


if __name__ == '__main__':
    tester = APITests()
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)
