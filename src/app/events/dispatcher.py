import asyncio
from typing import Type, Callable, Dict, List


class EventDispatcher:

    def __init__(self):
        self._handlers: Dict[str, List] = {}

    def register_handler(self, event_type: Type, handler: Callable):

        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)

    async def dispatch(self, event):

        event_type = type(event)
        handlers = self._handlers.get(event_type, [])

        await asyncio.gather(*[handler(event) for handler in handlers])
