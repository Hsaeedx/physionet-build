from django.test import TestCase
from django.urls import reverse

from user.models import User
from user.management.commands.resetdb import load_fixture_profiles

import pdb

class TestAuth(TestCase):
    """
    Test authentication
    """
    fixtures = ['user']

    def setUp(self):
        load_fixture_profiles()
        
    def test_profile_fixtures(self):
        """
        Test that the demo profiles in the fixtures are successfully loaded and
        attached to the user objects. 
        """
        u = User.objects.get(email='rgmark@mit.edu')

        self.assertTrue(u.profile.last_name == 'Mark')

    def test_login(self):
        """
        Test that known users are able to login.
        """
        #pdb.set_trace()
        unknown_user_status = self.client.login(username='what', password='letmein')
        known_user_status = self.client.login(username='rgmark@mit.edu',
            password='Tester1!')
        known_admin_user_status = self.client.login(username='tester@mit.edu', 
            password='Tester1!')

        self.assertEqual(False, unknown_user_status)
        self.assertEqual(True, known_user_status)
        self.assertEqual(True, known_admin_user_status)

    def test_admin_home(self):
        """
        Test that the admin page redirects to a login page.
        """
        response = self.client.get('/admin/')
        redirect_url = response['Location'].split('?')[0]
        
        self.assertEqual('/admin/login/', redirect_url)
        self.assertEqual(302, response.status_code)
        self.assertRedirects(response,'/admin/login/?next=/admin/',
            status_code=302)


class TestPublic(TestCase):
    def test_public_pages(self):
        """
        Test that public pages are reached and return '200' codes.
        """
        response = self.client.get(reverse('home'))
        self.assertEqual(200, response.status_code)