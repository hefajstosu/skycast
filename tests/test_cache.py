from app.cache import TTLCache


class FakeClock:
    def __init__(self) -> None:
        self.now = 0.0

    def __call__(self) -> float:
        return self.now


def test_returns_value_before_expiry():
    clock = FakeClock()
    cache: TTLCache[str] = TTLCache(ttl_seconds=10, clock=clock)
    cache.set("a", "value")
    clock.now = 9.9
    assert cache.get("a") == "value"


def test_expires_after_ttl():
    clock = FakeClock()
    cache: TTLCache[str] = TTLCache(ttl_seconds=10, clock=clock)
    cache.set("a", "value")
    clock.now = 10
    assert cache.get("a") is None
    assert len(cache) == 0


def test_clear():
    cache: TTLCache[int] = TTLCache(ttl_seconds=10)
    cache.set("a", 1)
    cache.clear()
    assert cache.get("a") is None
