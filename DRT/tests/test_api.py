from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from datetime import date, timedelta


@override_settings(DATABASES={
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
})
class AuthAndReceiptAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.User = get_user_model()
        self.username = "apitester"
        self.email = "api@example.com"
        self.password = "VeryStrongPass123"

    def authenticate(self):
        # register
        url = reverse('api_register')
        res = self.client.post(url, {
            'username': self.username,
            'email': self.email,
            'password': self.password,
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        token = res.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    def test_register_and_get_profile(self):
        self.authenticate()
        # list users (current only)
        res = self.client.get('/api/users/')
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['username'], self.username)

    def test_create_receipt_and_analytics(self):
        self.authenticate()
        # create category
        from DRT.models import Category
        from django.contrib.auth import get_user_model
        user = self.User.objects.get(username=self.username)
        Category.objects.create(name='Groceries')

        # create receipt
        res = self.client.post('/api/receipts/', {
            'store_name': 'Market',
            'total_amount': '100.00',
            'currency': 'KES',
            'purchase_date': str(date.today()),
        }, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        receipt_id = res.data['id']

        # get list
        res_list = self.client.get('/api/receipts/')
        self.assertEqual(res_list.status_code, status.HTTP_200_OK)
        self.assertEqual(res_list.data['count'], 1)

        # analytics
        res_analytics = self.client.get('/api/receipts/analytics/')
        self.assertEqual(res_analytics.status_code, status.HTTP_200_OK)
        self.assertIn('summary', res_analytics.data)

    def test_logout_revokes_token(self):
        self.authenticate()
        res = self.client.post(reverse('api_logout'))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # subsequent request should be unauthorized
        res2 = self.client.get('/api/users/')
        # Depending on DRF authentication backends, unauthenticated may be 401 or 403 (CSRF enforced)
        self.assertIn(res2.status_code, (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN))


