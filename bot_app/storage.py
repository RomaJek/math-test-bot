from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType
from asgiref.sync import sync_to_async
from .models import BotState
from typing import Dict, Any, Optional

class DjangoORMStorage(BaseStorage):
    """Senior Level: Django ORM tiykkarındaǵı FSM Persistent Storage"""
    
    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        state_str = state.state if hasattr(state, 'state') else state
        obj, _ = await sync_to_async(BotState.objects.get_or_create)(user_id=key.user_id)
        obj.state = state_str
        await sync_to_async(obj.save)()

    async def get_state(self, key: StorageKey) -> Optional[str]:
        obj = await sync_to_async(BotState.objects.filter(user_id=key.user_id).first)()
        return obj.state if obj else None

    async def set_data(self, key: StorageKey, data: Dict[str, Any]) -> None:
        obj, _ = await sync_to_async(BotState.objects.get_or_create)(user_id=key.user_id)
        obj.data = data
        await sync_to_async(obj.save)()

    async def get_data(self, key: StorageKey) -> Dict[str, Any]:
        obj = await sync_to_async(BotState.objects.filter(user_id=key.user_id).first)()
        return obj.data if obj else {}

    async def close(self) -> None:
        pass # Django baylanıstı ózi basqaradı