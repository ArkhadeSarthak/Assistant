import json
import httpx
from typing import Dict, List, Optional, Any
from app.config.settings import settings
from app.utils.logger import app_logger

class MemoryService:
    def __init__(self):
        self.redis_url = settings.UPSTASH_REDIS_REST_URL
        self.redis_token = settings.UPSTASH_REDIS_REST_TOKEN
        self.headers = {"Authorization": f"Bearer {self.redis_token}"}
        # In-memory fallback
        self._memory_fallback: Dict[str, List[Dict[str, Any]]] = {}
        self._key_value_fallback: Dict[str, Dict[str, str]] = {}
        self._last_query_fallback: Dict[str, str] = {}

    async def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves conversation history for session from Upstash Redis."""
        key = f"session:{session_id}:history"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.redis_url}/get/{key}", headers=self.headers)
                if res.status_code == 200:
                    data = res.json().get("result")
                    if data:
                        return json.loads(data)
        except Exception as e:
            app_logger.warning(f"Upstash Redis get_session_history failed: {e}. Falling back to memory.")
        return self._memory_fallback.get(session_id, [])

    async def add_message(self, session_id: str, role: str, content: str):
        """Appends a user/assistant message to Redis and updates last_query."""
        history = await self.get_session_history(session_id)
        history.append({"role": role, "content": content})

        # Update last_query if role is user
        if role == "user" and content:
            await self.set_last_query(session_id, content)

        # Save to Redis
        key = f"session:{session_id}:history"
        try:
            json_payload = json.dumps(history)
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(f"{self.redis_url}/set/{key}", headers=self.headers, content=json_payload)
                app_logger.info(f"Persisted message ({role}) to Upstash Redis for session {session_id}")
        except Exception as e:
            app_logger.warning(f"Upstash Redis add_message failed: {e}. Saving to fallback.")
            self._memory_fallback[session_id] = history

    async def set_last_query(self, session_id: str, query: str):
        """Saves last user query in Upstash Redis."""
        key = f"session:{session_id}:last_query"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(f"{self.redis_url}/set/{key}", headers=self.headers, content=query)
        except Exception as e:
            self._last_query_fallback[session_id] = query

    async def get_last_query(self, session_id: str) -> Optional[str]:
        """Retrieves last user query from Upstash Redis."""
        key = f"session:{session_id}:last_query"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.redis_url}/get/{key}", headers=self.headers)
                if res.status_code == 200:
                    val = res.json().get("result")
                    if val:
                        return val
        except Exception:
            pass
        return self._last_query_fallback.get(session_id)

    async def store_memory_item(self, session_id: str, key: str, value: str):
        """Stores a key-value memory item in Upstash Redis."""
        redis_key = f"session:{session_id}:memories"
        items = await self.get_memory_items(session_id)
        items[key] = value
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(f"{self.redis_url}/set/{redis_key}", headers=self.headers, content=json.dumps(items))
                app_logger.info(f"Stored memory item '{key}' in Upstash Redis for session {session_id}")
        except Exception as e:
            if session_id not in self._key_value_fallback:
                self._key_value_fallback[session_id] = {}
            self._key_value_fallback[session_id][key] = value

    async def get_memory_items(self, session_id: str) -> Dict[str, str]:
        """Retrieves key-value memory items for session from Upstash Redis."""
        redis_key = f"session:{session_id}:memories"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(f"{self.redis_url}/get/{redis_key}", headers=self.headers)
                if res.status_code == 200:
                    data = res.json().get("result")
                    if data:
                        return json.loads(data)
        except Exception:
            pass
        return self._key_value_fallback.get(session_id, {})

memory_service = MemoryService()
