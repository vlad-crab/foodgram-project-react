from django.test import TestCase, Client
from django.contrib.auth import get_user_model


User = get_user_model()


class TestUsers(TestCase):

    def setUp(self):
        self.anonymous_client = Client()
        self.user = User.objects.create_user(
            username='user',
            email='email@email.com',
            password='password',
            first_name='name',
            last_name='lastname',
        )
        self.logged_client = Client()
        self.logged_client.force_login(self.user)

    def test_user_create(self):
        response = self.anonymous_client.post(
            '/api/users/',
            data={
                'username': 'user1',
                'email': 'email1@email.com',
                'password': 'password',
                'first_name': 'name1',
                'last_name': 'lastname1',
            }
        )
        self.assertEqual(response.status_code, 201)

    def test_users_me(self):
        response = self.logged_client.get('/api/users/me/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_subscribed'], False)

    def test_users_profile(self):
        response = self.anonymous_client.get('/api/users/1/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['is_subscribed'], False)

    def test_user_login_logout(self):
        self.logged_client.logout()
        response = self.anonymous_client.post(
            '/api/auth/token/login/',
            data={
                'username': 'user',
                'password': 'password',
            }
        )
        self.assertEqual(response.status_code, 201)
        response = self.logged_client.post('/api/auth/token/logout/')
        self.assertEqual(response.status_code, 204)

    def test_set_password(self):
        response = self.logged_client.post(
            '/api/users/set_password/',
            data={
                'new_password': 'new_password',
                'current_password': 'password',
            }
        )
        self.assertEqual(response.status_code, 204)
        self.logged_client.logout()
        response = self.anonymous_client.post(
            '/api/auth/token/login/',
            data={
                'username': 'user',
                'password': 'new_password',
            }
        )
        self.assertEqual(response.status_code, 201)