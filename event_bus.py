"""
event_bus.py - Simple Observer Pattern Event Bus for ENGI
Coordinates communication between modular society simulation systems.
"""

from topic_data import (
    EVT_TOPIC_DISCOVERED,
    EVT_CONVERSATION_END,
    EVT_RELATIONSHIP_CHANGE,
    EVT_MEMORY_CREATED,
    EVT_TRAIT_DISCOVERED,
    EVT_COMBAT_HIT,
    EVT_COMBAT_KILL,
    EVT_NPC_DEATH,
    EVT_PLAYER_DEATH,
    EVT_MARRIAGE,
    EVT_CHILD_BORN,
    EVT_RANK_CHANGE,
    EVT_CRIME_WITNESSED,
    EVT_GIFT_GIVEN,
    EVT_THEFT,
    EVT_INSULT,
    EVT_COMPLIMENT,
    EVT_BETRAYAL,
    EVT_RESCUE,
)


class EventBus:
    """Simple publish/subscribe event bus.

    Systems register callbacks for event types. When an event is emitted,
    all registered callbacks for that type are invoked with the event data.
    """

    def __init__(self):
        self._listeners = {}  # event_type -> list of callbacks

    def subscribe(self, event_type, callback):
        """Register a callback for an event type."""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)

    def unsubscribe(self, event_type, callback):
        """Remove a callback for an event type."""
        if event_type in self._listeners:
            self._listeners[event_type] = [
                cb for cb in self._listeners[event_type] if cb is not callback
            ]

    def emit(self, event_type, **data):
        """Emit an event, calling all registered callbacks.

        Returns list of messages from callbacks (if any return strings).
        """
        msgs = []
        for cb in self._listeners.get(event_type, []):
            result = cb(event_type=event_type, **data)
            if isinstance(result, str):
                msgs.append(result)
            elif isinstance(result, (list, tuple)):
                msgs.extend(result)
        return msgs

    def clear(self):
        """Remove all listeners."""
        self._listeners.clear()

    def listener_count(self, event_type=None):
        """Count registered listeners, optionally filtered by type."""
        if event_type:
            return len(self._listeners.get(event_type, []))
        return sum(len(cbs) for cbs in self._listeners.values())
