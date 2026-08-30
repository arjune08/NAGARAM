import unittest

from app import create_app


class PortalSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config.update(TESTING=True)
        cls.client = cls.app.test_client()

    def test_public_portals_render_or_redirect_cleanly(self):
        for path in (
            "/",
            "/auth/login",
            "/auth/register/citizen",
            "/auth/register/farmer",
            "/auth/register/ngo",
            "/auth/register/volunteer",
            "/healthz",
        ):
            response = self.client.get(path, follow_redirects=False)
            self.assertIn(response.status_code, (200, 302), path)

    def test_protected_workspaces_require_authentication(self):
        for path in (
            "/citizen/dashboard",
            "/farmer/dashboard",
            "/admin/command-center",
            "/ngo/dashboard",
            "/volunteer/dashboard",
        ):
            response = self.client.get(path, follow_redirects=False)
            self.assertIn(response.status_code, (302, 401, 403), path)

    def test_unknown_route_uses_not_found_page(self):
        response = self.client.get("/__portal-smoke-missing__")
        self.assertEqual(response.status_code, 404)


if __name__ == "__main__":
    unittest.main()
