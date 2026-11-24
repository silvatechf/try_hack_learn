import unittest

from httpx import ASGITransport, AsyncClient

from main import app


class PythonLabCorsPolicyTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        )

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_allows_configured_local_frontend_origin(self):
        response = await self.client.get(
            "/api/v1/python-lab/exercises",
            headers={"Origin": "http://localhost:3001"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "http://localhost:3001",
        )

    async def test_does_not_grant_access_control_header_to_unapproved_origin(self):
        response = await self.client.get(
            "/api/v1/python-lab/exercises",
            headers={"Origin": "https://unapproved.example"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("access-control-allow-origin", response.headers)

    async def test_allows_preflight_for_execution_post(self):
        response = await self.client.options(
            "/api/v1/python-lab/execute",
            headers={
                "Origin": "http://localhost:3001",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "content-type",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.headers.get("access-control-allow-origin"),
            "http://localhost:3001",
        )
        self.assertIn("POST", response.headers.get("access-control-allow-methods", ""))


if __name__ == "__main__":
    unittest.main()
