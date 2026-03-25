"""
memories.py - Memory and Gossip System for ENGI
Tracks what characters remember, how they feel about events, and how gossip spreads.
"""

from topic_data import (
    EVT_COMBAT_KILL,
    EVT_GIFT_GIVEN,
    EVT_THEFT,
    EVT_INSULT,
    EVT_RESCUE,
    EVT_BETRAYAL,
    EVT_COMPLIMENT,
)

# ─────────────────────────────────────────────────────────────
# EMOTIONAL IMPACT DEFAULTS BY EVENT TYPE
# ─────────────────────────────────────────────────────────────
_DEFAULT_EMOTIONAL_IMPACT = {
    EVT_COMBAT_KILL: -8,
    EVT_GIFT_GIVEN: 5.0,
    EVT_THEFT: -6.0,
    EVT_INSULT: -4.0,
    EVT_RESCUE: 8.0,
    EVT_BETRAYAL: -10.0,
    EVT_COMPLIMENT: 3.0,
}

# Gossip reduces emotional impact by this factor
_GOSSIP_IMPACT_FACTOR = 0.5


# ─────────────────────────────────────────────────────────────
# MEMORY CLASS
# ─────────────────────────────────────────────────────────────
class Memory:
    """A single remembered event."""

    __slots__ = (
        "event_type",
        "actor_id",
        "target_id",
        "location",
        "turn",
        "emotional_impact",
        "detail",
        "witnesses",
        "decay",
        "forgiven",
    )

    def __init__(
        self,
        event_type,
        actor_id,
        target_id,
        location="",
        turn=0,
        emotional_impact=0.0,
        detail="",
        witnesses=None,
        decay=1.0,
        forgiven=False,
    ):
        self.event_type = event_type
        self.actor_id = actor_id
        self.target_id = target_id
        self.location = location
        self.turn = turn
        self.emotional_impact = float(emotional_impact)
        self.detail = detail
        self.witnesses = witnesses if witnesses is not None else []
        self.decay = float(decay)
        self.forgiven = forgiven

    def __repr__(self):
        return (
            f"Memory({self.event_type!r}, {self.actor_id!r}->{self.target_id!r}, "
            f"impact={self.emotional_impact}, decay={self.decay:.2f})"
        )

    def to_dict(self):
        """Serialize to a plain dict."""
        return {
            "event_type": self.event_type,
            "actor_id": self.actor_id,
            "target_id": self.target_id,
            "location": self.location,
            "turn": self.turn,
            "emotional_impact": self.emotional_impact,
            "detail": self.detail,
            "witnesses": list(self.witnesses),
            "decay": self.decay,
            "forgiven": self.forgiven,
        }

    @classmethod
    def from_dict(cls, data):
        """Restore from a plain dict."""
        return cls(
            event_type=data["event_type"],
            actor_id=data["actor_id"],
            target_id=data["target_id"],
            location=data.get("location", ""),
            turn=data.get("turn", 0),
            emotional_impact=data.get("emotional_impact", 0.0),
            detail=data.get("detail", ""),
            witnesses=data.get("witnesses", []),
            decay=data.get("decay", 1.0),
            forgiven=data.get("forgiven", False),
        )


# ─────────────────────────────────────────────────────────────
# MEMORY MANAGER
# ─────────────────────────────────────────────────────────────
class MemoryManager:
    """Stores and queries memories for all characters."""

    def __init__(self):
        self._memories = {}  # character_id -> list[Memory]

    def add_memory(self, character_id, memory):
        """Store a memory for a character."""
        if character_id not in self._memories:
            self._memories[character_id] = []
        self._memories[character_id].append(memory)

    def get_memories(self, character_id, event_type=None, actor_id=None, limit=10):
        """Filtered recall of memories for a character.

        Returns most recent memories first, optionally filtered by
        event_type and/or actor_id.
        """
        mems = self._memories.get(character_id, [])
        if event_type is not None:
            mems = [m for m in mems if m.event_type == event_type]
        if actor_id is not None:
            mems = [m for m in mems if m.actor_id == actor_id]
        # Most recent first (highest turn), then insertion order reversed
        return list(reversed(mems))[:limit]

    def get_opinion_modifier(self, character_id, about_id):
        """Sum of emotional impacts for memories involving about_id,
        weighted by decay. Forgiven memories contribute at 20% strength.
        """
        mems = self._memories.get(character_id, [])
        total = 0.0
        for m in mems:
            if m.actor_id == about_id or m.target_id == about_id:
                weight = m.decay
                if m.forgiven:
                    weight *= 0.2
                total += m.emotional_impact * weight
        return total

    def tick_decay(self, amount=0.01):
        """Reduce decay on all memories. Never drops below 0.1."""
        for mems in self._memories.values():
            for m in mems:
                m.decay = max(0.1, m.decay - amount)

    def share_memory(self, from_id, to_id, memory):
        """Gossip: copy a memory to another character with reduced impact."""
        shared = Memory(
            event_type=memory.event_type,
            actor_id=memory.actor_id,
            target_id=memory.target_id,
            location=memory.location,
            turn=memory.turn,
            emotional_impact=memory.emotional_impact * _GOSSIP_IMPACT_FACTOR,
            detail=memory.detail,
            witnesses=list(memory.witnesses),
            decay=memory.decay,
            forgiven=memory.forgiven,
        )
        self.add_memory(to_id, shared)

    def spread_gossip(self, character_id, nearby_ids, rng, spread_chance=0.1):
        """Randomly share one memory with nearby characters."""
        mems = self._memories.get(character_id, [])
        if not mems:
            return
        memory = rng.choice(mems)
        for nid in nearby_ids:
            if rng.random() < spread_chance:
                self.share_memory(character_id, nid, memory)

    def forgive(self, character_id, memory):
        """Mark a memory as forgiven (reduces impact but keeps it)."""
        # Find the memory in the character's list and mark it
        mems = self._memories.get(character_id, [])
        for m in mems:
            if m is memory:
                m.forgiven = True
                return
        # If the exact object wasn't found, mark the passed reference
        memory.forgiven = True

    def get_relationship_summary(self, character_id, about_id):
        """One-line summary of how character feels about about_id."""
        mems = self._memories.get(character_id, [])
        relevant = [
            m for m in mems if m.actor_id == about_id or m.target_id == about_id
        ]
        if not relevant:
            return "You have no memories of them."

        # Pick the strongest (most impactful) memory
        strongest = max(relevant, key=lambda m: abs(m.emotional_impact * m.decay))
        if strongest.emotional_impact > 0:
            return f"They helped you: {strongest.detail}"
        elif strongest.emotional_impact < 0:
            return f"They wronged you: {strongest.detail}"
        else:
            return f"You remember them: {strongest.detail}"

    def to_save_data(self):
        """Serialize all memories for save/load."""
        data = {}
        for cid, mems in self._memories.items():
            data[cid] = [m.to_dict() for m in mems]
        return data

    @classmethod
    def from_save_data(cls, data):
        """Restore a MemoryManager from serialized data."""
        mgr = cls()
        for cid, mem_list in data.items():
            mgr._memories[cid] = [Memory.from_dict(d) for d in mem_list]
        return mgr


# ─────────────────────────────────────────────────────────────
# MODULE-LEVEL HELPERS
# ─────────────────────────────────────────────────────────────
def create_memory(
    event_type,
    actor_id,
    target_id,
    detail,
    location="",
    turn=0,
    witnesses=None,
):
    """Convenience constructor with default emotional_impact by event type."""
    impact = _DEFAULT_EMOTIONAL_IMPACT.get(event_type, 0.0)
    return Memory(
        event_type=event_type,
        actor_id=actor_id,
        target_id=target_id,
        location=location,
        turn=turn,
        emotional_impact=impact,
        detail=detail,
        witnesses=witnesses,
    )
