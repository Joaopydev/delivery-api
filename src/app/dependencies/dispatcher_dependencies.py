from app.events.dispatcher_instance import dispatcher
from app.events.dispatcher import EventDispatcher

def get_event_dispatcher() -> EventDispatcher:
    return dispatcher
