import json

from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse


class AccountsTest(TestCase):
    def test_login(self):
        test_user = {
            'username': 'test',
            'password': 'test1234'
        }
        User.objects.create_user(**test_user).save()
        response = self.client.post(
            '/accounts/', test_user, content_type='application/json')
        self.assertEqual(response.status_code, 201)
