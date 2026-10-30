import json
from datetime import datetime


class CacheUnavailable(Exception):
    """The cache could not be trusted or read."""


class ArrivalCache:
    def __init__(self, client):
        self.client = client

    def store(self, stop_id: str, data: dict, collected_at: datetime) -> None:
        if collected_at.tzinfo is None or collected_at.utcoffset() is None:
            raise ValueError("collected_at must be timezone-aware")
        value = json.dumps({"data": data, "collected_at": collected_at.isoformat()})
        try:
            self.client.set(f"arrival:{stop_id}", value)
        except Exception as exc:
            raise CacheUnavailable("Cache write failed") from exc

    def read(self, stop_id: str, now: datetime):
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("now must be timezone-aware")
        try:
            raw = self.client.get(f"arrival:{stop_id}")
        except Exception as exc:
            raise CacheUnavailable("Cache read failed") from exc
        if raw is None:
            return None
        try:
            entry = json.loads(raw)
            collected = datetime.fromisoformat(entry["collected_at"])
            if collected.tzinfo is None or collected.utcoffset() is None:
                raise ValueError("missing timezone")
            if not isinstance(entry["data"], dict):
                raise ValueError("invalid data")
            age = (now - collected).total_seconds()
        except (ValueError, TypeError, KeyError, UnicodeDecodeError) as exc:
            raise CacheUnavailable("Invalid cache data") from exc
        return entry if 0 <= age <= 120 else None

class RecoveryLimitReached(Exception):
    """No more attempts are allowed for this incident."""


class RecoveryStateStore:
    """Reserve retries atomically; missing state always fails closed."""

    _RESERVE = """
    local attempts = redis.call('HGET', KEYS[1], 'attempts')
    local maximum = redis.call('HGET', KEYS[1], 'max_attempts')
    if not attempts or not maximum then return -1 end
    attempts = tonumber(attempts)
    maximum = tonumber(maximum)
    if not attempts or not maximum or attempts < 0 or maximum < 1
       or attempts ~= math.floor(attempts) or maximum ~= math.floor(maximum)
       or attempts > maximum then return -1 end
    if attempts == maximum then return 0 end
    redis.call('HINCRBY', KEYS[1], 'attempts', 1)
    return attempts + 1
    """

    def __init__(self, client):
        self.client = client

    def reserve_attempt(self, incident_id: str) -> int:
        if not incident_id:
            raise ValueError("incident_id is required")
        try:
            result = self.client.eval(self._RESERVE, 1, f"recovery:{incident_id}")
        except Exception as exc:
            raise CacheUnavailable("Recovery state unavailable") from exc
        if result == -1:
            raise CacheUnavailable("Recovery state missing or invalid")
        if result == 0:
            raise RecoveryLimitReached("Recovery attempt limit reached")
        if not isinstance(result, int) or result < 1:
            raise CacheUnavailable("Unexpected recovery state response")
        return result
