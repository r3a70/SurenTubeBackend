import os


from redis import Redis


class RedisSingleton:

    _instance: 'RedisSingleton' = None
    client: Redis

    def __new__(cls, *args, **kwargs) -> 'RedisSingleton':

        if cls._instance is None:

            cls._instance = super().__new__(cls)
            cls._instance.client = Redis(*args, **kwargs)

        return cls._instance


redis: RedisSingleton = RedisSingleton(
    host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')),
    password=os.getenv('REDIS_PASSWORD')
)
redis_db: Redis = redis.client
