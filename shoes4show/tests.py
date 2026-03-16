from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

class AuthenticationViewsTests(TestCase):
	# Registration flow: valid input should create user/profile and hash password.
	def test_register_creates_user_and_profile_with_hashed_password(self):
		response = self.client.post(
			reverse('shoes4show:register'),
			{
				'username': 'newuser',
				'email': 'newuser@example.com',
				'password': 'SafePass123!',
				'website': '',
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertTrue(User.objects.filter(username='newuser').exists())

		user = User.objects.get(username='newuser')
		self.assertNotEqual(user.password, 'SafePass123!')
		self.assertTrue(user.check_password('SafePass123!'))
		self.assertTrue(hasattr(user, 'userprofile'))
		self.assertTrue(response.context['registered'])

	# Registration flow: duplicate username should be rejected.
	def test_register_with_existing_username_does_not_create_new_user(self):
		User.objects.create_user(
			username='existing',
			email='existing@example.com',
			password='ExistingPass123!',
		)

		response = self.client.post(
			reverse('shoes4show:register'),
			{
				'username': 'existing',
				'email': 'another@example.com',
				'password': 'AnotherPass123!',
				'website': '',
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertEqual(User.objects.filter(username='existing').count(), 1)
		self.assertFalse(response.context['registered'])

	# Login flow: valid credentials should log in and redirect to index.
	def test_login_with_valid_credentials_redirects_to_index(self):
		User.objects.create_user(
			username='loginuser',
			email='loginuser@example.com',
			password='LoginPass123!',
		)

		response = self.client.post(
			reverse('shoes4show:login'),
			{
				'username': 'loginuser',
				'password': 'LoginPass123!',
			},
		)

		self.assertRedirects(response, reverse('shoes4show:index'))
		self.assertIn('_auth_user_id', self.client.session)

	# Login flow: invalid credentials should keep user unauthenticated.
	def test_login_with_invalid_credentials_returns_error_message(self):
		response = self.client.post(
			reverse('shoes4show:login'),
			{
				'username': 'missing-user',
				'password': 'wrong-password',
			},
		)

		self.assertEqual(response.status_code, 200)
		self.assertContains(response, 'Invalid login details supplied.')

	# Access control: anonymous users should be redirected to login.
	def test_restricted_redirects_anonymous_user_to_login(self):
		response = self.client.get(reverse('shoes4show:restricted'))

		self.assertEqual(response.status_code, 302)
		self.assertIn(reverse('shoes4show:login'), response.url)

	# Logout flow: authenticated users should have their session cleared.
	def test_logout_clears_session_and_redirects_to_index(self):
		User.objects.create_user(
			username='logoutuser',
			email='logoutuser@example.com',
			password='LogoutPass123!',
		)
		self.client.login(username='logoutuser', password='LogoutPass123!')

		response = self.client.get(reverse('shoes4show:logout'))

		# Verify the user is redirected to the index page and session is cleared
		self.assertRedirects(response, reverse('shoes4show:index'))
		self.assertNotIn('_auth_user_id', self.client.session)
		self.assertFalse('_auth_user_backend' in self.client.session)

