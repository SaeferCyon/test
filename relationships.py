"""
relationships.py - Relationship System for ENGI
Tracks relationships between characters: friendships, rivalries, family, feuds.
"""

from social_data import SOCIAL_RANKS

# ─────────────────────────────────────────────────────────────
# RELATIONSHIP TYPE CONSTANTS
# ─────────────────────────────────────────────────────────────
REL_STRANGER = 0
REL_ACQUAINTANCE = 1
REL_FRIEND = 2
REL_CLOSE_FRIEND = 3
REL_RIVAL = 4
REL_ENEMY = 5
REL_LOVER = 6
REL_SPOUSE = 7
REL_FAMILY = 8


# ─────────────────────────────────────────────────────────────
# RELATIONSHIP CLASS
# ─────────────────────────────────────────────────────────────
class Relationship:
    """A relationship between two characters."""

    __slots__ = (
        "char_a_id",
        "char_b_id",
        "score",
        "rel_type",
        "family_type",
        "feud",
        "turns_known",
    )

    def __init__(
        self,
        char_a_id,
        char_b_id,
        score=0,
        rel_type=REL_STRANGER,
        family_type=None,
        feud=False,
        turns_known=0,
    ):
        self.char_a_id = char_a_id
        self.char_b_id = char_b_id
        self.score = score
        self.rel_type = rel_type
        self.family_type = family_type
        self.feud = feud
        self.turns_known = turns_known

    def __repr__(self):
        return (
            f"Relationship({self.char_a_id!r}, {self.char_b_id!r}, "
            f"score={self.score}, type={self.rel_type})"
        )

    def to_dict(self):
        """Serialize to a plain dict."""
        return {
            "char_a_id": self.char_a_id,
            "char_b_id": self.char_b_id,
            "score": self.score,
            "rel_type": self.rel_type,
            "family_type": self.family_type,
            "feud": self.feud,
            "turns_known": self.turns_known,
        }

    @classmethod
    def from_dict(cls, data):
        """Restore from a plain dict."""
        return cls(
            char_a_id=data["char_a_id"],
            char_b_id=data["char_b_id"],
            score=data.get("score", 0),
            rel_type=data.get("rel_type", REL_STRANGER),
            family_type=data.get("family_type"),
            feud=data.get("feud", False),
            turns_known=data.get("turns_known", 0),
        )


def _sorted_key(id_a, id_b):
    """Return a canonical sorted key pair for relationship lookup."""
    if str(id_a) <= str(id_b):
        return (id_a, id_b)
    return (id_b, id_a)


# ─────────────────────────────────────────────────────────────
# SCORE THRESHOLD HELPERS
# ─────────────────────────────────────────────────────────────
_SCORE_THRESHOLDS = [
    (-100, -50, "enemy", REL_ENEMY),
    (-50, -20, "rival", REL_RIVAL),
    (-20, 10, "stranger", REL_STRANGER),
    (10, 30, "acquaintance", REL_ACQUAINTANCE),
    (30, 60, "friend", REL_FRIEND),
    (60, 80, "close friend", REL_CLOSE_FRIEND),
]
# 80+ is "special" (lover/spouse set explicitly); default label "close friend"


def _type_from_score(score, current_type=REL_STRANGER):
    """Determine relationship type from score.

    Lover, spouse, and family types are never overwritten by score changes.
    """
    if current_type in (REL_LOVER, REL_SPOUSE, REL_FAMILY):
        return current_type
    for low, high, _label, rtype in _SCORE_THRESHOLDS:
        if low <= score < high:
            return rtype
    # score >= 80 stays at current type unless it was a basic type
    if score >= 80:
        if current_type in (REL_LOVER, REL_SPOUSE, REL_FAMILY):
            return current_type
        return REL_CLOSE_FRIEND
    return REL_STRANGER


def _label_from_score(score):
    """Return a human-readable label for a score value."""
    for low, high, label, _rtype in _SCORE_THRESHOLDS:
        if low <= score < high:
            return label
    if score >= 80:
        return "close friend"
    return "stranger"


# ─────────────────────────────────────────────────────────────
# RELATIONSHIP MANAGER
# ─────────────────────────────────────────────────────────────
class RelationshipManager:
    """Manages all relationships between characters."""

    def __init__(self, trait_manager=None, memory_manager=None):
        self._relationships = {}  # (id_a, id_b) -> Relationship
        self._trait_manager = trait_manager
        self._memory_manager = memory_manager

    def get_relationship(self, id_a, id_b):
        """Return the Relationship between two characters, or None."""
        key = _sorted_key(id_a, id_b)
        return self._relationships.get(key)

    def get_or_create(self, id_a, id_b):
        """Return existing Relationship or create a stranger one."""
        key = _sorted_key(id_a, id_b)
        rel = self._relationships.get(key)
        if rel is None:
            rel = Relationship(
                char_a_id=key[0],
                char_b_id=key[1],
                score=0,
                rel_type=REL_STRANGER,
            )
            self._relationships[key] = rel
        return rel

    def get_score(self, id_a, id_b):
        """Return the relationship score, or 0 if no relationship."""
        rel = self.get_relationship(id_a, id_b)
        if rel is None:
            return 0
        return rel.score

    def modify_score(self, id_a, id_b, delta, reason=""):
        """Adjust relationship score by delta, clamped to -100..100.

        Updates rel_type based on new score thresholds.
        Returns the new score.
        """
        rel = self.get_or_create(id_a, id_b)
        rel.score = max(-100, min(100, rel.score + delta))
        rel.rel_type = _type_from_score(rel.score, rel.rel_type)
        return rel.score

    def set_family(self, id_a, id_b, family_type):
        """Mark a family relationship between two characters."""
        rel = self.get_or_create(id_a, id_b)
        rel.family_type = family_type
        rel.rel_type = REL_FAMILY

    def start_feud(self, family_a_ids, family_b_ids):
        """Mark all cross-family pairs as feuding."""
        for a_id in family_a_ids:
            for b_id in family_b_ids:
                if a_id == b_id:
                    continue
                rel = self.get_or_create(a_id, b_id)
                rel.feud = True

    def get_all_relationships(self, char_id):
        """Return all Relationships involving char_id."""
        result = []
        for key, rel in self._relationships.items():
            if char_id in key:
                result.append(rel)
        return result

    def get_family(self, char_id):
        """Return list of (other_id, family_type) for family members."""
        result = []
        for key, rel in self._relationships.items():
            if char_id in key and rel.family_type is not None:
                other = key[1] if key[0] == char_id else key[0]
                result.append((other, rel.family_type))
        return result

    def get_friends(self, char_id):
        """Return list of character ids with score > 30."""
        result = []
        for key, rel in self._relationships.items():
            if char_id in key and rel.score > 30:
                other = key[1] if key[0] == char_id else key[0]
                result.append(other)
        return result

    def get_enemies(self, char_id):
        """Return list of character ids with score < -30."""
        result = []
        for key, rel in self._relationships.items():
            if char_id in key and rel.score < -30:
                other = key[1] if key[0] == char_id else key[0]
                result.append(other)
        return result

    def calculate_compatibility(self, id_a, id_b, traits_a, traits_b, rank_a, rank_b):
        """Calculate compatibility between two characters.

        Factors: trait compatibility, social class distance, memory opinions.
        Returns a float (higher = more compatible).
        """
        score = 0.0

        # Trait compatibility (uses TraitManager if available)
        if self._trait_manager is not None:
            score += self._trait_manager.get_compatibility_score(traits_a, traits_b)

        # Social class distance penalty
        rank_a_info = SOCIAL_RANKS.get(rank_a, {})
        rank_b_info = SOCIAL_RANKS.get(rank_b, {})
        tier_a = rank_a_info.get("tier", 5)
        tier_b = rank_b_info.get("tier", 5)
        tier_distance = abs(tier_a - tier_b)
        score -= tier_distance * 0.5

        # Memory-based opinion modifier
        if self._memory_manager is not None:
            opinion_a = self._memory_manager.get_opinion_modifier(id_a, id_b)
            opinion_b = self._memory_manager.get_opinion_modifier(id_b, id_a)
            score += (opinion_a + opinion_b) * 0.1

        return score

    def tick_autonomous(self, npc_pairs, rng):
        """NPCs form or break relationships autonomously.

        Small chance per pair per tick. Uses trait compatibility when
        trait data is available.

        Args:
            npc_pairs: list of (id_a, id_b, traits_a, traits_b, rank_a, rank_b)
                       tuples, or (id_a, id_b) for simple mode.
            rng: random.Random instance.

        Returns:
            list of event dicts describing what happened.
        """
        events = []
        for pair in npc_pairs:
            if len(pair) >= 6:
                id_a, id_b, traits_a, traits_b, rank_a, rank_b = pair[:6]
            else:
                id_a, id_b = pair[0], pair[1]
                traits_a, traits_b = [], []
                rank_a, rank_b = None, None

            # 5% base chance of interaction per tick
            if rng.random() > 0.05:
                continue

            compat = self.calculate_compatibility(
                id_a, id_b, traits_a, traits_b, rank_a, rank_b
            )

            # Compatibility influences score change direction and magnitude
            if compat > 0:
                delta = rng.randint(1, max(1, int(compat * 2)))
            elif compat < 0:
                delta = -rng.randint(1, max(1, int(abs(compat) * 2)))
            else:
                delta = rng.choice([-1, 0, 1])

            if delta == 0:
                continue

            old_score = self.get_score(id_a, id_b)
            new_score = self.modify_score(id_a, id_b, delta)
            old_label = self.get_type_label(old_score)
            new_label = self.get_type_label(new_score)

            event = {
                "type": "relationship_change",
                "id_a": id_a,
                "id_b": id_b,
                "delta": delta,
                "old_score": old_score,
                "new_score": new_score,
            }

            if old_label != new_label:
                event["transition"] = f"{old_label} -> {new_label}"

            events.append(event)

        return events

    def propagate_opinion(self, source_id, target_id, connected_ids, factor=0.3):
        """When source's opinion of target changes, connected characters
        shift their opinion of target slightly too.

        Args:
            source_id: the character whose opinion changed
            target_id: the character opinion is about
            connected_ids: ids of characters connected to source
            factor: how much of source's opinion to propagate (0.0-1.0)
        """
        source_score = self.get_score(source_id, target_id)
        propagation_delta = int(source_score * factor)
        if propagation_delta == 0:
            return

        for cid in connected_ids:
            if cid == source_id or cid == target_id:
                continue
            # Scale by how much the connected character trusts source
            trust = self.get_score(cid, source_id)
            if trust <= 0:
                continue  # don't propagate from untrusted sources
            # Stronger trust = stronger propagation
            scaled = int(propagation_delta * (trust / 100.0))
            if scaled != 0:
                self.modify_score(cid, target_id, scaled)

    def get_type_label(self, score):
        """Return a human-readable label for a relationship score."""
        return _label_from_score(score)

    def to_save_data(self):
        """Serialize all relationships for save/load."""
        data = {}
        for key, rel in self._relationships.items():
            str_key = f"{key[0]}|{key[1]}"
            data[str_key] = rel.to_dict()
        return data

    @classmethod
    def from_save_data(cls, data, trait_manager=None, memory_manager=None):
        """Restore a RelationshipManager from serialized data."""
        mgr = cls(trait_manager=trait_manager, memory_manager=memory_manager)
        for _str_key, rel_data in data.items():
            rel = Relationship.from_dict(rel_data)
            key = _sorted_key(rel.char_a_id, rel.char_b_id)
            mgr._relationships[key] = rel
        return mgr
