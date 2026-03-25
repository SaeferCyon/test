"""
z_level.py - Z-Level Data Structures for 縁起 ENGI

Provides ZTile, ZColumn, and vertical navigation utilities for the
3-tier map system with ±32 Z-levels.
"""

from data import (
    LT_AIR,
    LT_STAIRS_UP,
    LT_STAIRS_DOWN,
    LT_LADDER_UP,
    LT_LADDER_DOWN,
    LT_RAMP_UP,
    LT_RAMP_DOWN,
    MIN_Z,
    MAX_Z,
    SURFACE_Z,
    LOCAL_TERRAIN,
)


# ─────────────────────────────────────────────────────────────
# ZTile — single tile at a specific Z-level
# ─────────────────────────────────────────────────────────────


class ZTile:
    """A single tile at a specific Z-level.

    Attributes:
        terrain: Local terrain type ID (default LT_AIR).
        items: List of item IDs present on this tile.
        npc_id: NPC occupying this tile, or None.
        feature: Special feature dict, or None.
    """

    __slots__ = ("terrain", "items", "npc_id", "feature")

    def __init__(self, terrain=LT_AIR, items=None, npc_id=None, feature=None):
        self.terrain = terrain
        self.items = items if items is not None else []
        self.npc_id = npc_id
        self.feature = feature

    def __repr__(self):
        tdef = LOCAL_TERRAIN.get(self.terrain)
        name = tdef["name"] if tdef else f"id={self.terrain}"
        return f"ZTile({name})"


# Shared singleton for unstored air tiles (read-only convenience).
_AIR_TILE = ZTile(LT_AIR)


# ─────────────────────────────────────────────────────────────
# ZColumn — all Z-levels at a single (x, y) position
# ─────────────────────────────────────────────────────────────


class ZColumn:
    """Sparse column of Z-tiles at a single (x, y) map position.

    Only non-air levels are stored.  Accessing an unstored level
    returns a default air tile.
    """

    __slots__ = ("_tiles",)

    def __init__(self):
        self._tiles: dict[int, ZTile] = {}

    # -- access ----------------------------------------------------------

    def get(self, z: int) -> ZTile:
        """Return the tile at *z*, or an air tile if unstored."""
        return self._tiles.get(z, _AIR_TILE)

    def set(self, z: int, tile: ZTile) -> None:
        """Store *tile* at *z*.  Removes the entry if the tile is air
        (keeps the dict sparse)."""
        if tile.terrain == LT_AIR and not tile.items and tile.npc_id is None:
            self._tiles.pop(z, None)
        else:
            self._tiles[z] = tile

    # -- queries ---------------------------------------------------------

    @property
    def surface_z(self) -> int:
        """Highest z with a walkable solid tile, or MIN_Z if none."""
        best = None
        for z, tile in self._tiles.items():
            tdef = LOCAL_TERRAIN.get(tile.terrain)
            if tdef and tdef["walk"]:
                if best is None or z > best:
                    best = z
        return best if best is not None else MIN_Z

    def has_floor(self, z: int) -> bool:
        """True if *z* has a solid tile (walkable or wall/rock)."""
        tile = self.get(z)
        if tile.terrain == LT_AIR:
            return False
        tdef = LOCAL_TERRAIN.get(tile.terrain)
        # If terrain is defined and not air, it counts as solid.
        return tdef is not None

    def is_empty(self, z: int) -> bool:
        """True if *z* is air or not stored."""
        return self.get(z).terrain == LT_AIR

    def __repr__(self):
        levels = sorted(self._tiles.keys())
        return f"ZColumn({len(levels)} levels: {levels})"


# ─────────────────────────────────────────────────────────────
# Vertical navigation functions
# ─────────────────────────────────────────────────────────────

_ASCEND_TILES = frozenset({LT_STAIRS_UP, LT_LADDER_UP, LT_RAMP_UP})
_DESCEND_TILES = frozenset({LT_STAIRS_DOWN, LT_LADDER_DOWN, LT_RAMP_DOWN})


def can_ascend(column: ZColumn, z: int) -> bool:
    """True if the tile at *z* allows upward movement."""
    return column.get(z).terrain in _ASCEND_TILES


def can_descend(column: ZColumn, z: int) -> bool:
    """True if the tile at *z* allows downward movement."""
    return column.get(z).terrain in _DESCEND_TILES


def get_fall_distance(column: ZColumn, z: int) -> int:
    """Distance (in z-levels) to the next solid tile below *z*.

    Returns 0 if the current z-level has a floor (player is standing on
    solid ground). Only counts fall distance when the player is in air.
    """
    # If we're on solid ground, no fall.
    if column.has_floor(z):
        return 0
    # We're in air — find the nearest solid tile below.
    distance = 0
    current = z - 1
    while current >= MIN_Z:
        if column.has_floor(current):
            return distance + 1
        distance += 1
        current -= 1
    # Fell to the bottom of the map without hitting anything.
    return distance + 1


def calc_fall_damage(distance: int) -> int:
    """HP damage from falling *distance* z-levels.

    - 0-1 levels: 0 damage  (safe landing / short hop)
    - 2+ levels:  scales quadratically — ``(distance - 1) ** 2``
    """
    if distance <= 1:
        return 0
    return (distance - 1) ** 2


def can_climb(column: ZColumn, z: int) -> bool:
    """True if the terrain at *z* has ``climb=True`` in LOCAL_TERRAIN."""
    tile = column.get(z)
    tdef = LOCAL_TERRAIN.get(tile.terrain)
    if tdef is None:
        return False
    return bool(tdef.get("climb", False))


# ─────────────────────────────────────────────────────────────
# Surface detection
# ─────────────────────────────────────────────────────────────


def find_surface(column: ZColumn) -> int:
    """Return z of the highest walkable surface tile in *column*.

    Falls back to MIN_Z if no walkable tile exists.
    """
    return column.surface_z


def find_ground(column: ZColumn) -> int:
    """Return SURFACE_Z if it is solid, otherwise the nearest solid
    z-level below SURFACE_Z.  Falls back to MIN_Z."""
    z = SURFACE_Z
    while z >= MIN_Z:
        if column.has_floor(z):
            return z
        z -= 1
    return MIN_Z
