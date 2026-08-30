import os
import unittest

# Keep smoke tests isolated from production database configuration.
os.environ.pop('DATABASE_URL', None)
os.environ.pop('POSTGRES_URL', None)
os.environ.pop('NEON_DATABASE_URL', None)
os.environ.pop('SUPABASE_DB_URL', None)
os.environ['TESTING'] = '1'
os.environ.pop('VERCEL', None)

from app import create_app


class PortalSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
        cls.client = cls.app.test_client()

    def test_public_pages_do_not_server_error(self):
        for path in (
            '/',
            '/healthz',
            '/auth/login',
            '/auth/register/citizen',
            '/auth/register/farmer',
            '/auth/register/ngo',
            '/auth/register/volunteer',
        ):
            with self.subTest(path=path):
                response = self.client.get(path, follow_redirects=False)
                self.assertNotEqual(response.status_code, 500)
                self.assertLess(response.status_code, 600)

    def test_unknown_route_is_handled(self):
        response = self.client.get('/route-that-does-not-exist')
        self.assertEqual(response.status_code, 404)

    def test_protected_portals_redirect_or_deny_without_server_error(self):
        for path in ('/citizen/dashboard', '/farmer/dashboard', '/admin/dashboard'):
            with self.subTest(path=path):
                response = self.client.get(path, follow_redirects=False)
                self.assertIn(response.status_code, (302, 401, 403))


if __name__ == '__main__':
    unittest.main(verbosity=2)
