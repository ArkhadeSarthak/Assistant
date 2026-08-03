import json
import asyncio
from typing import Dict, List, Optional, Any
from upstash_redis import Redis
from app.config.settings import settings
from app.utils.logger import app_logger

class MemoryService:
    def __init__(self):
        self.redis_url = settings.UPSTASH_REDIS_REST_URL
        self.redis_token = settings.UPSTASH_REDIS_REST_TOKEN
        self._client: Optional[Redis] = None
        if self.redis_url and self.redis_token:
            try:
                self._client = Redis(url=self.redis_url, token=self.redis_token)
                app_logger.info(f"Initialized Upstash Redis client for {self.redis_url}")
            except Exception as e:
                app_logger.warning(f"Failed to initialize Upstash Redis client: {e}")
        
        # In-memory fallback
        self._memory_fallback: Dict[str, List[Dict[str, Any]]] = {}
        self._key_value_fallback: Dict[str, Dict[str, str]] = {}
        self._last_query_fallback: Dict[str, str] = {}

    async def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        """Retrieves conversation history for session from Upstash Redis."""
        key = f"session:{session_id}:history"
        if self._client:
            try:
                def _get():
                    return self._client.get(key)
                data = await asyncio.to_thread(_get)
                if data:
                    if isinstance(data, str):
                        return json.loads(data)
                    elif isinstance(data, list):
                        return data
            except Exception as e:
                app_logger.warning(f"Upstash Redis get_session_history failed for {session_id}: {e}. Falling back to memory.")
        return self._memory_fallback.get(session_id, [])

    async def add_message(self, session_id: str, role: str, content: str):
        """Appends a user/assistant message to Redis and updates last_query."""
        if not content or not content.strip():
            return

        history = await self.get_session_history(session_id)
        # Avoid duplicate consecutive identical messages
        if not (history and history[-1].get("role") == role and history[-1].get("content") == content):
            history.append({"role": role, "content": content})

        # Keep last 20 messages to preserve sliding context window
        if len(history) > 20:
            history = history[-20:]

        if role == "user":
            await self.set_last_query(session_id, content)

        # Basic entity extraction (e.g. "my name is X")
        if role == "user":
            lowered = content.lower()
            if "my name is " in lowered:
                name = content.split("my name is ", 1)[1].split(".")[0].strip()
                if name:
                    await self.store_memory_item(session_id, "user_name", name.capitalize())

        # Save to Redis & Fallback
        key = f"session:{session_id}:history"
        json_payload = json.dumps(history)
        self._memory_fallback[session_id] = history
        
        if self._client:
            try:
                def _set():
                    return self._client.set(key, json_payload)
                await asyncio.to_thread(_set)
                app_logger.info(f"Persisted message ({role}) to Upstash Redis for session {session_id}")
            except Exception as e:
                app_logger.warning(f"Upstash Redis add_message failed: {e}. Saved to memory fallback.")

    async def set_last_query(self, session_id: str, query: str):
        """Saves last user query in Upstash Redis."""
        key = f"session:{session_id}:last_query"
        self._last_query_fallback[session_id] = query
        if self._client:
            try:
                def _set():
                    return self._client.set(key, query)
                await asyncio.to_thread(_set)
            except Exception:
                pass

    async def get_last_query(self, session_id: str) -> Optional[str]:
        """Retrieves last user query from Upstash Redis."""
        key = f"session:{session_id}:last_query"
        if self._client:
            try:
                def _get():
                    return self._client.get(key)
                val = await asyncio.to_thread(_get)
                if val:
                    return str(val)
            except Exception:
                pass
        return self._last_query_fallback.get(session_id)

    async def store_memory_item(self, session_id: str, key: str, value: str):
        """Stores a key-value memory item in Upstash Redis."""
        redis_key = f"session:{session_id}:memories"
        items = await self.get_memory_items(session_id)
        items[key] = value
        
        if session_id not in self._key_value_fallback:
            self._key_value_fallback[session_id] = {}
        self._key_value_fallback[session_id][key] = value

        if self._client:
            try:
                def _set():
                    return self._client.set(redis_key, json.dumps(items))
                await asyncio.to_thread(_set)
                app_logger.info(f"Stored memory item '{key}' in Upstash Redis for session {session_id}")
            except Exception as e:
                app_logger.warning(f"Failed storing memory item to Upstash: {e}")

    async def get_memory_items(self, session_id: str) -> Dict[str, str]:
        """Retrieves key-value memory items for session from Upstash Redis."""
        redis_key = f"session:{session_id}:memories"
        if self._client:
            try:
                def _get():
                    return self._client.get(redis_key)
                data = await asyncio.to_thread(_get)
                if data:
                    if isinstance(data, str):
                        return json.loads(data)
                    elif isinstance(data, dict):
                        return data
            except Exception:
                pass
        return self._key_value_fallback.get(session_id, {})

    async def clear_session_data(self, session_id: str):
        """Deletes all session data (history, memories, last query) from Redis and memory fallback."""
        if not session_id:
            return

        app_logger.info(f"[MemoryService] Clearing session data for session_id: '{session_id}'")
        
        # Clear in-memory fallbacks
        self._memory_fallback.pop(session_id, None)
        self._key_value_fallback.pop(session_id, None)
        self._last_query_fallback.pop(session_id, None)

        keys_to_delete = [
            f"session:{session_id}:history",
            f"session:{session_id}:last_query",
            f"session:{session_id}:memories"
        ]

        if self._client:
            try:
                def _delete():
                    for k in keys_to_delete:
                        try:
                            self._client.delete(k)
                        except Exception as err:
                            app_logger.warning(f"Error deleting Redis key '{k}': {err}")
                await asyncio.to_thread(_delete)
                app_logger.info(f"Successfully deleted Redis session keys for '{session_id}'")
            except Exception as e:
                app_logger.warning(f"Upstash Redis clear_session_data failed for '{session_id}': {e}")

memory_service = MemoryService()
