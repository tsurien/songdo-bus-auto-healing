import os
import unittest
from uuid import uuid4

from redis import Redis
from src.cache import CacheUnavailable, RecoveryLimitReached, RecoveryStateStore


@unittest.skipUnless(os.getenv("REDIS_INTEGRATION") == "1", "local Redis not requested")
class RecoveryStateTests(unittest.TestCase):
    def setUp(self):
        self.redis = Redis(host="127.0.0.1", port=6379)
        self.incident = f"test-{uuid4()}"
        self.key = f"recovery:{self.incident}"
        self.store = RecoveryStateStore(self.redis)

    def tearDown(self):
        self.redis.delete(self.key)

    def test_missing_and_limit_fail_closed(self):
        with self.assertRaises(CacheUnavailable):
            self.store.reserve_attempt(self.incident)
        self.redis.hset(self.key, mapping={"attempts": 0, "max_attempts": 3})
        self.assertEqual([self.store.reserve_attempt(self.incident) for _ in range(3)], [1, 2, 3])
        with self.assertRaises(RecoveryLimitReached):
            self.store.reserve_attempt(self.incident)
        self.redis.delete(self.key)
        with self.assertRaises(CacheUnavailable):
            self.store.reserve_attempt(self.incident)

    def test_invalid_state_fails_closed(self):
        self.redis.hset(self.key, mapping={"attempts": -1, "max_attempts": 3})
        with self.assertRaises(CacheUnavailable):
            self.store.reserve_attempt(self.incident)


if __name__ == "__main__":
    unittest.main()
