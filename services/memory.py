import json

import redis

from core.config import settings


class RedisMemory:

    def __init__(self) -> None:

        self.client = redis.Redis.from_url(
            settings.redis_url,
            decode_responses=True,
        )

        self.ttl = 3600

    def _get_key(
        self,
        session_id: str,
    ) -> str:

        return f"chat:{session_id}"

    def get_history(
        self,
        session_id: str,
    ) -> list[dict[str, str]]:

        key = self._get_key(session_id)

        messages = self.client.lrange(
            key,
            0,
            -1,
        )

        return [
            json.loads(message)
            for message in messages
        ]

    def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
    ) -> None:

        key = self._get_key(session_id)

        message = json.dumps(
            {
                "role": role,
                "content": content,
            }
        )

        self.client.rpush(
            key,
            message,
        )

        self.client.expire(
            key,
            self.ttl,
        )

    def clear_history(
        self,
        session_id: str,
    ) -> None:

        key = self._get_key(session_id)

        self.client.delete(key)


    