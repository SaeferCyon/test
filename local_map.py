"""
local_map.py - Local Map for ENGI

100x100 grid of ZColumn objects with Z-level support.
Represents a single area tile at 1:1 meter scale with +/-32 Z-levels.
"""

import math

from data import (
    LOCAL_H,
    LOCAL_W,
    LOCAL_TERRAIN,
    LOCAL_MOVE_COST,
    LT_AIR,
    MIN_Z,
    MAX_Z,
)
from z_level import ZColumn, ZTile


# ─────────────────────────────────────────────────────────────
# LocalMap
# ─────────────────────────────────────────────────────────────


class LocalMap:
    """100x100 grid of ZColumn objects with Z-level support.

    Coordinates: columns[row][col], accessed via get_tile(x, y, z).
    Origin is identified by (region_col, region_row, area_x, area_y).
    """

    def __init__(self, region_col, region_row, area_x, area_y):
        self.region_col = region_col
        self.region_row = region_row
        self.area_x = area_x
        self.area_y = area_y
        self.columns = [[ZColumn() for _ in range(LOCAL_W)] for _ in range(LOCAL_H)]
        self.modified = False
        self.npcs = {}  # {npc_id: npc_object}
        self.items = {}  # {item_id: item_dict}
        self.lit_tiles = set()  # set of (x, y, z)
        self.seen_tiles = set()  # set of (x, y, z)

    # ── bounds check ─────────────────────────────────────────

    def _in_bounds(self, x, y):
        """Return True if (x, y) is within the grid."""
        return 0 <= x < LOCAL_W and 0 <= y < LOCAL_H

    # ── tile access ──────────────────────────────────────────

    def get_tile(self, x, y, z):
        """Return ZTile at (x, y, z), or None if out of bounds."""
        if not self._in_bounds(x, y):
            return None
        return self.columns[y][x].get(z)

    def set_tile(self, x, y, z, tile):
        """Set a ZTile at (x, y, z). Marks map as modified."""
        if not self._in_bounds(x, y):
            return
        self.columns[y][x].set(z, tile)
        self.modified = True

    def get_column(self, x, y):
        """Return ZColumn at (x, y), or None if out of bounds."""
        if not self._in_bounds(x, y):
            return None
        return self.columns[y][x]

    # ── walkability ──────────────────────────────────────────

    def is_walkable(self, x, y, z):
        """True if tile at (x,y,z) is in bounds, walkable, and unoccupied."""
        if not self._in_bounds(x, y):
            return False
        tile = self.columns[y][x].get(z)
        tdef = LOCAL_TERRAIN.get(tile.terrain)
        if tdef is None or not tdef["walk"]:
            return False
        # Check if an NPC occupies this position
        for npc in self.npcs.values():
            pos = getattr(npc, "pos", None)
            if pos and pos == (x, y, z):
                return False
        return True

    def get_move_cost(self, x, y, z):
        """Return movement cost for tile at (x,y,z). Default 1."""
        tile = self.get_tile(x, y, z)
        if tile is None:
            return 1
        return LOCAL_MOVE_COST.get(tile.terrain, 1)

    # ── FOV (field of view) ──────────────────────────────────

    def compute_fov(self, origin_x, origin_y, origin_z, radius):
        """Raycasting FOV on the current Z-level.

        Casts 360 rays at 1-degree increments. Tiles that block
        sight have LOCAL_TERRAIN[terrain]["sight"] == True.
        """
        self.lit_tiles = set()
        # Origin is always visible
        self.lit_tiles.add((origin_x, origin_y, origin_z))
        self.seen_tiles.add((origin_x, origin_y, origin_z))
        num_rays = 360
        for i in range(num_rays):
            angle = math.radians(i)
            self._cast_ray(
                origin_x,
                origin_y,
                origin_z,
                math.cos(angle),
                math.sin(angle),
                radius,
            )

    def _cast_ray(self, ox, oy, oz, dx, dy, radius):
        """Cast a single ray, marking lit/seen tiles."""
        for step in range(1, radius + 1):
            tx = ox + round(dx * step)
            ty = oy + round(dy * step)
            if not self._in_bounds(tx, ty):
                break
            self.lit_tiles.add((tx, ty, oz))
            self.seen_tiles.add((tx, ty, oz))
            tile = self.columns[ty][tx].get(oz)
            tdef = LOCAL_TERRAIN.get(tile.terrain)
            if tdef and tdef.get("sight", False):
                break

    # ── entity management: NPCs ──────────────────────────────

    def place_npc(self, npc, x, y, z):
        """Place an NPC on the map and record its position."""
        npc.pos = (x, y, z)
        self.npcs[npc.npc_id] = npc
        tile = self.get_tile(x, y, z)
        if tile is not None:
            tile.npc_id = npc.npc_id

    def move_npc(self, npc, new_x, new_y, new_z):
        """Update NPC position to new coordinates."""
        old_pos = getattr(npc, "pos", None)
        if old_pos:
            old_tile = self.get_tile(*old_pos)
            if old_tile is not None:
                old_tile.npc_id = None
        npc.pos = (new_x, new_y, new_z)
        new_tile = self.get_tile(new_x, new_y, new_z)
        if new_tile is not None:
            new_tile.npc_id = npc.npc_id

    def remove_npc(self, npc_id):
        """Remove an NPC from tracking."""
        npc = self.npcs.pop(npc_id, None)
        if npc is None:
            return
        pos = getattr(npc, "pos", None)
        if pos:
            tile = self.get_tile(*pos)
            if tile is not None:
                tile.npc_id = None

    def get_npc_at(self, x, y, z):
        """Return the NPC at (x, y, z), or None."""
        for npc in self.npcs.values():
            pos = getattr(npc, "pos", None)
            if pos and pos == (x, y, z):
                return npc
        return None

    # ── entity management: items ─────────────────────────────

    def place_item(self, item, item_id, x, y, z):
        """Place an item on the map."""
        item["pos"] = (x, y, z)
        item["item_id"] = item_id
        self.items[item_id] = item
        tile = self.get_tile(x, y, z)
        if tile is not None:
            tile.items.append(item_id)

    def get_items_at(self, x, y, z):
        """Return list of item dicts at (x, y, z)."""
        result = []
        for item in self.items.values():
            if item.get("pos") == (x, y, z):
                result.append(item)
        return result

    # ── serialization ────────────────────────────────────────

    def to_save_data(self):
        """Return dict suitable for pickle serialization."""
        col_data = []
        for row in self.columns:
            row_data = []
            for col in row:
                tiles = {}
                for z, tile in col._tiles.items():
                    tiles[z] = {
                        "terrain": tile.terrain,
                        "items": list(tile.items),
                        "npc_id": tile.npc_id,
                    }
                row_data.append(tiles)
            col_data.append(row_data)
        npc_positions = {}
        for npc_id, npc in self.npcs.items():
            npc_positions[npc_id] = getattr(npc, "pos", None)
        return {
            "region_col": self.region_col,
            "region_row": self.region_row,
            "area_x": self.area_x,
            "area_y": self.area_y,
            "columns": col_data,
            "items": dict(self.items),
            "npc_positions": npc_positions,
            "seen_tiles": list(self.seen_tiles),
        }

    @classmethod
    def from_save_data(cls, data):
        """Reconstruct a LocalMap from saved data."""
        lm = cls(
            data["region_col"],
            data["region_row"],
            data["area_x"],
            data["area_y"],
        )
        _restore_columns(lm, data["columns"])
        lm.items = data.get("items", {})
        lm.seen_tiles = set(tuple(t) for t in data.get("seen_tiles", []))
        return lm


def _restore_columns(lm, col_data):
    """Restore column tile data from serialized format."""
    for y, row_data in enumerate(col_data):
        for x, tiles_dict in enumerate(row_data):
            col = lm.columns[y][x]
            for z_str, tdata in tiles_dict.items():
                z = int(z_str) if isinstance(z_str, str) else z_str
                tile = ZTile(
                    terrain=tdata["terrain"],
                    items=tdata.get("items", []),
                    npc_id=tdata.get("npc_id"),
                )
                col.set(z, tile)
