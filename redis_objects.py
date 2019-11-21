import redis


class RedisObject:
    def __init__(self, client: redis.Redis, name: str):
        self.client = client
        self.name = name


class RedisSet(RedisObject):
    def __init__(self, client: redis.Redis, name: str, members=None):
        super().__init__(client, name)
        if members is not None:
            self.client.delete(self.name)
            self.client.sadd(self.name, *members)

    def __contains__(self, item):
        return self.client.sismember(self.name, item)

    def add(self, elem):
        self.client.sadd(self.name, elem)

    def remove(self, elem):
        self.client.srem(self.name, elem)


class RedisHash(RedisObject):
    def __init__(self, client: redis.Redis, name: str, items=None):
        super().__init__(client, name)
        if items is not None:
            self.client.hmset(self.name, items)

    def __contains__(self, item):
        return self.client.hexists(self.name, item)

    def __getitem__(self, item):
        return self.client.hget(self.name, item)

    def __setitem__(self, key, value):
        self.client.hset(self.name, key, value)


class RedisInt(RedisObject):
    def __init__(self, client: redis.Redis, name: str, value=None):
        super().__init__(client, name)
        if value is not None:
            self.client.set(self.name, value)
