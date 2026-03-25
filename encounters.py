"""
encounters.py - Dynamic NPC encounters for the travel map.
Ticket: FR-1774474529
"""

from data import (
    T_ROAD,
    T_FOREST,
    T_MOUNTAIN,
    T_PLAINS,
    TERRAIN,
)


# ─────────────────────────────────────────────────────────────
# ENCOUNTER CLASS
# ─────────────────────────────────────────────────────────────
class Encounter:
    """A single encounter event on the travel map."""

    __slots__ = (
        "encounter_type",
        "npc_ids",
        "description",
        "is_hostile",
        "is_positive",
        "terrain",
        "region_col",
        "region_row",
    )

    def __init__(
        self,
        encounter_type,
        npc_ids=None,
        description="",
        is_hostile=False,
        is_positive=False,
        terrain=None,
        region_col=0,
        region_row=0,
    ):
        self.encounter_type = encounter_type
        self.npc_ids = npc_ids or []
        self.description = description
        self.is_hostile = is_hostile
        self.is_positive = is_positive
        self.terrain = terrain
        self.region_col = region_col
        self.region_row = region_row


# ─────────────────────────────────────────────────────────────
# ENCOUNTER TABLES  (terrain -> list of (type, weight))
# ─────────────────────────────────────────────────────────────
_ENCOUNTER_TABLES = {
    T_ROAD: [
        ("merchant_caravan", 30),
        ("pilgrim_group", 25),
        ("lone_traveler", 20),
        ("bandit_ambush", 10),
        ("army_march", 5),
        ("helpful_stranger", 10),
    ],
    T_FOREST: [
        ("bandit_ambush", 30),
        ("animal", 30),
        ("lone_traveler", 15),
        ("lost_person", 10),
        ("helpful_stranger", 15),
    ],
    T_MOUNTAIN: [
        ("animal", 35),
        ("bandit_ambush", 20),
        ("yamabushi", 20),
        ("lost_person", 15),
        ("refugee_column", 10),
    ],
    T_PLAINS: [
        ("merchant_caravan", 25),
        ("farmer", 25),
        ("army_march", 15),
        ("lone_traveler", 20),
        ("refugee_column", 15),
    ],
}

_DEFAULT_TABLE = [
    ("lone_traveler", 50),
    ("animal", 30),
    ("helpful_stranger", 20),
]


# ─────────────────────────────────────────────────────────────
# ENCOUNTER DESCRIPTIONS & METADATA
# ─────────────────────────────────────────────────────────────
_ENCOUNTER_META = {
    "merchant_caravan": {
        "desc": "A merchant caravan approaches, pack horses laden with goods.",
        "hostile": False,
        "positive": True,
    },
    "bandit_ambush": {
        "desc": "Figures emerge from the shadows. Bandits!",
        "hostile": True,
        "positive": False,
    },
    "pilgrim_group": {
        "desc": "A group of pilgrims in white robes walk the road, chanting.",
        "hostile": False,
        "positive": True,
    },
    "army_march": {
        "desc": "The ground trembles. An army marches past, banners flying.",
        "hostile": False,
        "positive": False,
    },
    "refugee_column": {
        "desc": "A weary column of refugees trudges along, carrying what little they own.",
        "hostile": False,
        "positive": False,
    },
    "lone_traveler": {
        "desc": "A lone traveler walks the path, straw hat low over their eyes.",
        "hostile": False,
        "positive": False,
    },
    "animal": {
        "desc": "A wild animal watches you from the undergrowth, eyes gleaming.",
        "hostile": True,
        "positive": False,
    },
    "helpful_stranger": {
        "desc": "A kindly stranger offers you directions and a sip of water.",
        "hostile": False,
        "positive": True,
    },
    "lost_person": {
        "desc": "A lost traveler stumbles toward you, begging for help.",
        "hostile": False,
        "positive": False,
    },
    "yamabushi": {
        "desc": "A mountain ascetic in tattered robes blocks the trail, staff in hand.",
        "hostile": False,
        "positive": True,
    },
    "farmer": {
        "desc": "A farmer rests by the roadside, wiping sweat from his brow.",
        "hostile": False,
        "positive": True,
    },
}

# Base encounter chances by terrain category
_BASE_CHANCE = {
    T_ROAD: 0.15,
    T_FOREST: 0.20,
    T_MOUNTAIN: 0.18,
    T_PLAINS: 0.12,
}
_DEFAULT_CHANCE = 0.10

# Night modifier
_NIGHT_CHANCE_BONUS = 0.05
_NIGHT_HOSTILE_BONUS = 0.20  # +20% hostile chance at night


def _is_night(hour):
    """Return True if the hour is considered nighttime (20-5)."""
    return hour >= 20 or hour < 5


def _weighted_choice(table, rng):
    """Pick a type from a weighted table using the given RNG."""
    total = sum(w for _, w in table)
    roll = rng.random() * total
    cumulative = 0
    for etype, weight in table:
        cumulative += weight
        if roll <= cumulative:
            return etype
    # Fallback (should not happen)
    return table[-1][0]


# ─────────────────────────────────────────────────────────────
# ENCOUNTER MANAGER
# ─────────────────────────────────────────────────────────────
class EncounterManager:
    """Manages dynamic encounters and traveling NPCs."""

    def __init__(self):
        self._travelers = []  # list of traveler dicts

    # ----------------------------------------------------------
    # Traveler management
    # ----------------------------------------------------------

    def spawn_travelers(self, world, count, rng):
        """Create *count* NPCs traveling between locations.

        *world* is expected to have a ``cities`` attribute (list of
        dicts with ``col``/``row`` keys) or at minimum be non-None.
        """
        cities = getattr(world, "cities", None) or []
        if len(cities) < 2:
            return

        npc_types = [
            "merchant",
            "pilgrim",
            "ronin",
            "farmer",
            "samurai",
        ]

        for _ in range(count):
            src = rng.choice(cities)
            dst = rng.choice(cities)
            while dst is src:
                dst = rng.choice(cities)

            traveler = {
                "id": rng.randint(100_000, 999_999),
                "from_col": src.get("col", 0),
                "from_row": src.get("row", 0),
                "to_col": dst.get("col", 0),
                "to_row": dst.get("row", 0),
                "progress": 0.0,
                "npc_type": rng.choice(npc_types),
            }
            self._travelers.append(traveler)

    def tick_travelers(self, world):
        """Advance all traveler positions one step along their route."""
        speed = 0.02  # progress per tick
        still_traveling = []
        for t in self._travelers:
            t["progress"] = min(1.0, t["progress"] + speed)
            if t["progress"] < 1.0:
                still_traveling.append(t)
            # else: arrived — remove from list
        self._travelers = still_traveling

    def get_nearby_travelers(self, col, row, radius=2):
        """Return travelers within *radius* of (col, row)."""
        nearby = []
        for t in self._travelers:
            # Interpolate current position
            p = t["progress"]
            cur_col = t["from_col"] + (t["to_col"] - t["from_col"]) * p
            cur_row = t["from_row"] + (t["to_row"] - t["from_row"]) * p
            if abs(cur_col - col) <= radius and abs(cur_row - row) <= radius:
                nearby.append(t)
        return nearby

    # ----------------------------------------------------------
    # Encounter generation
    # ----------------------------------------------------------

    def get_encounter_chance(self, terrain_type, hour):
        """Return base encounter probability for *terrain_type* and *hour*."""
        chance = _BASE_CHANCE.get(terrain_type, _DEFAULT_CHANCE)
        if _is_night(hour):
            chance += _NIGHT_CHANCE_BONUS
        return chance

    def generate_encounter(self, terrain_type, season, hour, rng):
        """Create a context-aware Encounter for the given conditions."""
        table = _ENCOUNTER_TABLES.get(terrain_type, _DEFAULT_TABLE)
        etype = _weighted_choice(table, rng)

        meta = _ENCOUNTER_META.get(
            etype,
            {
                "desc": "Something stirs nearby.",
                "hostile": False,
                "positive": False,
            },
        )

        is_hostile = meta["hostile"]
        # Night makes encounters more hostile
        if _is_night(hour) and not is_hostile:
            if rng.random() < _NIGHT_HOSTILE_BONUS:
                is_hostile = True

        return Encounter(
            encounter_type=etype,
            description=meta["desc"],
            is_hostile=is_hostile,
            is_positive=meta["positive"],
            terrain=terrain_type,
        )

    def check_encounter(self, player_col, player_row, terrain_type, season, hour, rng):
        """Roll for an encounter at the player's location.

        Returns an Encounter or None.
        """
        # First check nearby travelers
        nearby = self.get_nearby_travelers(player_col, player_row, radius=2)
        if nearby:
            t = rng.choice(nearby)
            meta = _ENCOUNTER_META.get("lone_traveler")
            return Encounter(
                encounter_type="lone_traveler",
                npc_ids=[t["id"]],
                description=meta["desc"],
                is_hostile=False,
                is_positive=False,
                terrain=terrain_type,
                region_col=player_col,
                region_row=player_row,
            )

        chance = self.get_encounter_chance(terrain_type, hour)
        if rng.random() < chance:
            enc = self.generate_encounter(terrain_type, season, hour, rng)
            enc.region_col = player_col
            enc.region_row = player_row
            return enc

        return None

    # ----------------------------------------------------------
    # Serialization
    # ----------------------------------------------------------

    def to_save_data(self):
        """Serialize manager state for saving."""
        return {
            "travelers": [dict(t) for t in self._travelers],
        }

    @classmethod
    def from_save_data(cls, data):
        """Restore an EncounterManager from saved data."""
        em = cls()
        em._travelers = [dict(t) for t in data.get("travelers", [])]
        return em
