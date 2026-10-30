import unittest
from datetime import datetime, timedelta, timezone

from src.cache import ArrivalCache, CacheUnavailable


class MemoryRedis:
    def __init__(self):
        self.data = {}

    def set(self, key, value):
        self.data[key] = value

    def get(self, key):
        return self.data.get(key)


class BrokenRedis:
    def get(self, key):
        raise OSError("unavailable")


class CacheTests(unittest.TestCase):
    def setUp(self):
        self.redis = MemoryRedis()
        self.cache = ArrivalCache(self.redis)
        self.collected = datetime(2026, 1, 1, tzinfo=timezone.utc)
        self.cache.store("38563", {"route_id": "example"}, self.collected)

    def test_boundary_and_original_collection_time(self):
        at_limit = self.cache.read("38563", self.collected + timedelta(seconds=120))
        self.assertEqual(at_limit["collected_at"], self.collected.isoformat())
        self.assertEqual(at_limit["data"]["route_id"], "example")
        self.assertIsNone(self.cache.read("38563", self.collected + timedelta(seconds=121)))

    def test_missing_and_unavailable_are_distinct(self):
        self.assertIsNone(self.cache.read("missing", self.collected))
        with self.assertRaises(CacheUnavailable):
            ArrivalCache(BrokenRedis()).read("38563", self.collected)

    def test_future_collection_is_not_accepted(self):
        self.assertIsNone(self.cache.read("38563", self.collected - timedelta(seconds=1)))


if __name__ == "__main__":
    unittest.main()
