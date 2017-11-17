from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.views import LoginView
from django.core import mail
from django.test import TestCase
from django.urls import reverse
import re

from user.models import User, AssociatedEmail
from user.management.commands.resetdb import load_fixture_profiles

import pdb


class TestAuth(TestCase):
    """
    Test views that require authentication
    """
    fixtures = ['user']

    def setUp(self):
        load_fixture_profiles()
        self.client.login(username='rgmark@mit.edu', password='Tester1!')

    def test_profile_fixtures(self):
        """
        Test that the demo profiles in the fixtures are successfully loaded and
        attached to the user objects.
        """
        u = User.objects.get(email='rgmark@mit.edu')
        self.assertTrue(u.profile.last_name == 'Mark')

    def test_edit_password(self):
        response = self.client.post(reverse('edit_password'),
            data={'old_password':'Tester1!',
            'new_password1':'Very5trongt0t@11y',
            'new_password2':'Very5trongt0t@11y'})
        self.assertRedirects(response, reverse('edit_password_done'))
        # Try to log in using the new password
        self.client.logout()
        self.assertTrue(self.client.login(username='rgmark@mit.edu',
            password='Very5trongt0t@11y'))

    def test_user_settings(self):
        response = self.client.get(reverse('user_settings'))
        self.assertRedirects(response, reverse('edit_profile'))

    def test_logout(self):
        response = self.client.get(reverse('logout'))
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_edit_profile(self):
        response = self.client.post(reverse('edit_profile'),
            data={'first_name':'Roger', 'last_name':'Federer'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.get(email='rgmark@mit.edu').profile.last_name,
            'Federer')



class TestPublic(TestCase):
    """
    Test views that do not require authentication
    """

    fixtures = ['user']

    def setUp(self):
        load_fixture_profiles()

    def test_admin_home(self):
        """
        Test that the admin page redirects to a login page.
        """
        response = self.client.get('/admin/')
        self.assertRedirects(response, '/admin/login/?next=/admin/',
            status_code=302)

    def test_login(self):
        response = self.client.post(reverse('login'),
            data={'username':'rgmark@mit.edu','password':'Tester1!'})
        self.assertRedirects(response, reverse('user_home'))
        self.assertIn('_auth_user_id', self.client.session)

    def test_reset_password(self):
        """
        Test the full reset password functionality
        """
        # Request the password reset
        response = self.client.post(reverse('reset_password_request'),
            data={'email':'rgmark@mit.edu'})
        self.assertRedirects(response, reverse('reset_password_sent'))

        # Reset the password
        # Get the reset info from the email
        uidb64, token = re.findall('reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/',
            mail.outbox[0].body)[0]

        response = self.client.post(reverse('reset_password_confirm',
            kwargs={'uidb64':uidb64,'token':token}), follow=True,
            data={'new_password1':'Very5trongt0t@11y',
                'new_password2':'Very5trongt0t@11y'})

        pdb.set_trace()

        self.assertRedirects(response, reverse('reset_password_complete'))


        
