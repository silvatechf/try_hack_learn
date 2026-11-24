import unittest

from fastapi import FastAPI, Request
from httpx import ASGITransport, AsyncClient

from request_limits import RequestBodyLimitMiddleware


MAX_BODY_BYTES = 128


def create_test_app():
    app = FastAPI()
    app.add_middleware(
        RequestBodyLimitMiddleware,
        path="/limited",
        max_bytes=MAX_BODY_BYTES,
    )

    @app.post("/limited")
    async def limited_endpoint(request: Request):
        body = await request.body()
        return {"received_bytes": len(body)}

    @app.post("/unlimited")
    async def unlimited_endpoint(request: Request):
        body = await request.body()
        return {"received_bytes": len(body)}

    return app


class RequestBodyLimitTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.client = AsyncClient(
            transport=ASGITransport(app=create_test_app()),
            base_url="http://test",
        )

    async def asyncTearDown(self):
        await self.client.aclose()

    async def test_accepts_body_at_configured_limit(self):
        response = await self.client.post(
            "/limited",
            content=b"x" * MAX_BODY_BYTES,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["received_bytes"], MAX_BODY_BYTES)

    async def test_rejects_body_over_configured_limit(self):
        response = await self.client.post(
            "/limited",
            content=b"x" * (MAX_BODY_BYTES + 1),
        )

        self.assertEqual(response.status_code, 413)
        self.assertEqual(
            response.json()["detail"],
            "Request body exceeds the configured limit",
        )

    async def test_does_not_change_other_routes(self):
        response = await self.client.post(
            "/unlimited",
            content=b"x" * (MAX_BODY_BYTES + 1),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["received_bytes"], MAX_BODY_BYTES + 1)

    async def test_enforces_limit_for_streamed_bodies(self):
        async def chunks():
            yield b"x" * MAX_BODY_BYTES
            yield b"y"

        response = await self.client.post("/limited", content=chunks())

        self.assertEqual(response.status_code, 413)


if __name__ == "__main__":
    unittest.main()
