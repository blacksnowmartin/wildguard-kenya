from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken


class AuthenticationTests(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='ranger-one',
            password='test-password',
            role='RANGER',
            first_name='Ranger',
            last_name='One',
        )

    def test_token_endpoint_returns_access_and_refresh_tokens(self):
        response = self.client.post(
            '/api/auth/token/',
            {'username': 'ranger-one', 'password': 'test-password'},
            format='json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_current_user_requires_authentication(self):
        response = self.client.get('/api/auth/me/')
        self.assertEqual(response.status_code, 401)

    def test_current_user_returns_role_profile(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.user).access_token}')
        response = self.client.get('/api/auth/me/')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['role'], 'RANGER')
        self.assertNotIn('password', response.data)
