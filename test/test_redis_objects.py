import pytest
import redis

from redis_objects import RedisHash, RedisSet


@pytest.fixture
def redis_client():
    return redis.Redis(decode_responses=True)


@pytest.fixture
def redis_set(redis_client):
    redis_client.delete("myset")
    yield RedisSet(redis_client, "myset")


@pytest.fixture
def redis_hash(redis_client):
    redis_client.delete("myhash")
    yield RedisHash(redis_client, "myhash")


class TestRedisSet:
    def test_init(self, redis_client):
        members = {"foo", "bar"}
        s = RedisSet(redis_client, "myset", members)
        assert redis_client.smembers(s.name) == members

    def test_contains(self, redis_client):
        s = RedisSet(redis_client, "myset", {"foo"})
        assert "foo" in s
        assert "bar" not in s

    def test_add(self, redis_set):
        redis_set.add("foo")
        assert "foo" in redis_set

    def test_remove(self, redis_set):
        redis_set.remove("foo")
        assert "foo" not in redis_set


class TestRedisHash:
    def test_init(self, redis_client):
        mapping = {"foo": "bar"}
        h = RedisHash(redis_client, "myhash", mapping)
        assert redis_client.hgetall("myhash") == mapping

    def test_contains(self, redis_client):
        h = RedisHash(redis_client, "myhash", {"foo": "bar"})
        assert "foo" in h
        assert "bar" not in h

    def test_getitem(self, redis_client):
        h = RedisHash(redis_client, "myhash", {"foo": "bar"})
        assert h["foo"] == "bar"

    def test_setitem(self, redis_hash):
        redis_hash["foo"] = "bar"
        assert redis_hash["foo"] == "bar"
