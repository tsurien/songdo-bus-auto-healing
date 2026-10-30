import unittest

from fastapi.testclient import TestClient

from src.api import app, get_arrivals
from src.bus_data import Arrival


class ArrivalEndpointTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def tearDown(self):
        app.dependency_overrides.clear()

    def test_selected_stop_with_arrival(self):
        app.dependency_overrides[get_arrivals] = lambda: lambda: [
            Arrival(route_id="mock-route", eta_seconds=180)
        ]
        response = self.client.get("/arrivals", params={"stop": "38563", "direction": "경제자유구역청·국제업무지구역5번출구"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["arrivals"][0]["eta_seconds"], 180)

    def test_empty_is_normal(self):
        app.dependency_overrides[get_arrivals] = lambda: lambda: []
        response = self.client.get("/arrivals", params={"stop": "38563", "direction": "경제자유구역청·국제업무지구역5번출구"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["arrivals"], [])

    def test_other_direction_rejected(self):
        app.dependency_overrides[get_arrivals] = lambda: lambda: []
        response = self.client.get("/arrivals", params={"stop": "38563", "direction": "다른 방향"})
        self.assertEqual(response.status_code, 400)

    def test_unconfigured_source_is_not_fake_success(self):
        response = self.client.get("/arrivals", params={"stop": "38563", "direction": "경제자유구역청·국제업무지구역5번출구"})
        self.assertEqual(response.status_code, 503)


if __name__ == "__main__":
    unittest.main()
