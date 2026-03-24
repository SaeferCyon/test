"""
poi_data.py - POI Templates and Overrides for ENGI

Hand-crafted point-of-interest building templates defined as Python dicts.
Each template specifies a tile layout, NPC spawn points, item spawn points,
and entrance locations.
"""

from data import (
    LT_WOOD_WALL,
    LT_STONE_WALL,
    LT_CASTLE_WALL,
    LT_WOOD_FLOOR,
    LT_STONE_FLOOR,
    LT_TATAMI,
    LT_EARTH_FLOOR,
    LT_DOOR,
    LT_GATE,
    LT_TORII,
    LT_FUTON,
    LT_TABLE,
    LT_CHEST,
    LT_ALTAR,
    LT_HEARTH,
    LT_BARREL,
    LT_RACK,
    LT_SIGNPOST,
    LT_STAIRS_UP,
    LT_STAIRS_DOWN,
    LT_LADDER_UP,
    LT_LADDER_DOWN,
)


# ─────────────────────────────────────────────────────────────
# Helper: generate rectangular wall outlines and floors
# ─────────────────────────────────────────────────────────────


def _rect_walls(w, h, z, wall_type, floor_type):
    """Return tiles list for a rectangular room: walls on perimeter, floor inside."""
    tiles = []
    for x in range(w):
        for y in range(h):
            if x == 0 or x == w - 1 or y == 0 or y == h - 1:
                tiles.append((x, y, z, wall_type))
            else:
                tiles.append((x, y, z, floor_type))
    return tiles


# ─────────────────────────────────────────────────────────────
# Templates
# ─────────────────────────────────────────────────────────────


def _build_small_house():
    """5x5 wood house with tatami floor, one door on south wall."""
    tiles = _rect_walls(5, 5, 0, LT_WOOD_WALL, LT_TATAMI)
    # Replace south-center wall with door
    tiles = [(x, y, z, t) for (x, y, z, t) in tiles if not (x == 2 and y == 4)]
    tiles.append((2, 4, 0, LT_DOOR))
    return {
        "name": "small_house",
        "width": 5,
        "height": 5,
        "z_levels": 1,
        "tiles": tiles,
        "npc_spawns": [(2, 2, 0, "villager")],
        "item_spawns": [(3, 1, 0, "rice_ball", 0.5)],
        "entrances": [(2, 4, 0)],
    }


def _build_large_house():
    """8x6 wood house, two rooms divided by internal wall, two doors."""
    tiles = _rect_walls(8, 6, 0, LT_WOOD_WALL, LT_TATAMI)
    # Internal dividing wall at x=4 (y=1..4)
    for y in range(1, 5):
        tiles = [
            (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 4 and ty == y)
        ]
        tiles.append((4, y, 0, LT_WOOD_WALL))
    # Internal doorway at x=4, y=3
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 4 and ty == 3)
    ]
    tiles.append((4, 3, 0, LT_DOOR))
    # Front door at south wall center
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 2 and ty == 5)
    ]
    tiles.append((2, 5, 0, LT_DOOR))
    return {
        "name": "large_house",
        "width": 8,
        "height": 6,
        "z_levels": 1,
        "tiles": tiles,
        "npc_spawns": [(2, 2, 0, "villager"), (6, 2, 0, "villager")],
        "item_spawns": [
            (1, 1, 0, "futon", 0.8),
            (6, 1, 0, "tea_set", 0.6),
        ],
        "entrances": [(2, 5, 0)],
    }


def _build_inn():
    """10x8 inn with common area, hearth, and guest rooms."""
    tiles = _rect_walls(10, 8, 0, LT_WOOD_WALL, LT_TATAMI)
    # Hearth in common area
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 3 and ty == 3)
    ]
    tiles.append((3, 3, 0, LT_HEARTH))
    # Internal wall dividing guest rooms (y=4, x=1..8)
    for x in range(1, 9):
        tiles = [
            (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == x and ty == 4)
        ]
        tiles.append((x, 4, 0, LT_WOOD_WALL))
    # Doorways into guest rooms at x=3 and x=6
    for dx in (3, 6):
        tiles = [
            (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == dx and ty == 4)
        ]
        tiles.append((dx, 4, 0, LT_DOOR))
    # Front door
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 5 and ty == 7)
    ]
    tiles.append((5, 7, 0, LT_DOOR))
    return {
        "name": "inn",
        "width": 10,
        "height": 8,
        "z_levels": 1,
        "tiles": tiles,
        "npc_spawns": [
            (2, 2, 0, "innkeeper"),
            (5, 5, 0, "traveler"),
        ],
        "item_spawns": [
            (1, 5, 0, "futon", 0.9),
            (8, 5, 0, "futon", 0.9),
            (4, 2, 0, "sake", 0.7),
        ],
        "entrances": [(5, 7, 0)],
    }


def _build_temple():
    """12x10 stone temple with altar and torii gate entrance."""
    tiles = _rect_walls(12, 10, 0, LT_STONE_WALL, LT_STONE_FLOOR)
    # Altar at the back center
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 6 and ty == 1)
    ]
    tiles.append((6, 1, 0, LT_ALTAR))
    # Torii gate at entrance (south center)
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 6 and ty == 9)
    ]
    tiles.append((6, 9, 0, LT_TORII))
    return {
        "name": "temple",
        "width": 12,
        "height": 10,
        "z_levels": 1,
        "tiles": tiles,
        "npc_spawns": [
            (6, 3, 0, "monk"),
            (4, 5, 0, "monk"),
        ],
        "item_spawns": [
            (5, 1, 0, "incense", 0.8),
            (7, 1, 0, "prayer_beads", 0.4),
        ],
        "entrances": [(6, 9, 0)],
    }


def _build_shrine():
    """6x6 wood shrine with small altar and torii gate."""
    tiles = _rect_walls(6, 6, 0, LT_WOOD_WALL, LT_WOOD_FLOOR)
    # Altar at back center
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 3 and ty == 1)
    ]
    tiles.append((3, 1, 0, LT_ALTAR))
    # Torii gate entrance
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 3 and ty == 5)
    ]
    tiles.append((3, 5, 0, LT_TORII))
    return {
        "name": "shrine",
        "width": 6,
        "height": 6,
        "z_levels": 1,
        "tiles": tiles,
        "npc_spawns": [(3, 3, 0, "shrine_maiden")],
        "item_spawns": [(2, 1, 0, "ofuda", 0.5)],
        "entrances": [(3, 5, 0)],
    }


def _build_blacksmith():
    """6x6 blacksmith with stone floor, hearth, and weapon rack."""
    tiles = _rect_walls(6, 6, 0, LT_WOOD_WALL, LT_STONE_FLOOR)
    # Hearth
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 2 and ty == 2)
    ]
    tiles.append((2, 2, 0, LT_HEARTH))
    # Weapon rack
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 4 and ty == 1)
    ]
    tiles.append((4, 1, 0, LT_RACK))
    # Door
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 3 and ty == 5)
    ]
    tiles.append((3, 5, 0, LT_DOOR))
    return {
        "name": "blacksmith",
        "width": 6,
        "height": 6,
        "z_levels": 1,
        "tiles": tiles,
        "npc_spawns": [(3, 3, 0, "blacksmith")],
        "item_spawns": [
            (4, 2, 0, "katana", 0.3),
            (4, 3, 0, "iron_ingot", 0.6),
        ],
        "entrances": [(3, 5, 0)],
    }


def _build_market_stall():
    """4x4 open-front market stall with chest and barrel."""
    tiles = []
    # Floor
    for x in range(4):
        for y in range(4):
            tiles.append((x, y, 0, LT_EARTH_FLOOR))
    # Walls on three sides (not south / y=3 — open front)
    for x in range(4):
        tiles = [
            (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == x and ty == 0)
        ]
        tiles.append((x, 0, 0, LT_WOOD_WALL))
    for y in range(4):
        if y == 3:
            continue  # open front
        tiles = [
            (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 0 and ty == y)
        ]
        tiles.append((0, y, 0, LT_WOOD_WALL))
        tiles = [
            (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 3 and ty == y)
        ]
        tiles.append((3, y, 0, LT_WOOD_WALL))
    # Chest and barrel
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 1 and ty == 1)
    ]
    tiles.append((1, 1, 0, LT_CHEST))
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 2 and ty == 1)
    ]
    tiles.append((2, 1, 0, LT_BARREL))
    return {
        "name": "market_stall",
        "width": 4,
        "height": 4,
        "z_levels": 1,
        "tiles": tiles,
        "npc_spawns": [(1, 2, 0, "merchant")],
        "item_spawns": [
            (1, 1, 0, "trade_goods", 0.8),
            (2, 1, 0, "sake", 0.5),
        ],
        "entrances": [(1, 3, 0), (2, 3, 0)],
    }


def _build_watchtower():
    """4x4 stone watchtower, 2 Z-levels with ladder between."""
    # Ground floor
    tiles = _rect_walls(4, 4, 0, LT_STONE_WALL, LT_STONE_FLOOR)
    # Door on ground floor
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 2 and ty == 3)
    ]
    tiles.append((2, 3, 0, LT_DOOR))
    # Ladder up on ground floor
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 1 and ty == 1)
    ]
    tiles.append((1, 1, 0, LT_LADDER_UP))
    # Upper floor (z=1)
    upper = _rect_walls(4, 4, 1, LT_STONE_WALL, LT_STONE_FLOOR)
    # Ladder down on upper floor
    upper = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in upper if not (tx == 1 and ty == 1)
    ]
    upper.append((1, 1, 1, LT_LADDER_DOWN))
    tiles.extend(upper)
    return {
        "name": "watchtower",
        "width": 4,
        "height": 4,
        "z_levels": 2,
        "tiles": tiles,
        "npc_spawns": [(2, 2, 1, "guard")],
        "item_spawns": [(2, 1, 1, "bow", 0.4)],
        "entrances": [(2, 3, 0)],
    }


def _build_waystation():
    """8x6 waystation — inn-like rest stop with signpost outside."""
    tiles = _rect_walls(8, 6, 0, LT_WOOD_WALL, LT_TATAMI)
    # Hearth in common area
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 4 and ty == 2)
    ]
    tiles.append((4, 2, 0, LT_HEARTH))
    # Front door
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 4 and ty == 5)
    ]
    tiles.append((4, 5, 0, LT_DOOR))
    # Signpost placed just outside the door (not inside the footprint,
    # but we include it as a tile at y=6 which is one past the south wall)
    # Actually, keep within footprint: place signpost at interior spot
    # Instead, widen conceptually — signpost at (4, 5) would overlap door.
    # Place signpost to the right of the door outside:
    # We'll note it as an extra tile outside the strict bounding box.
    # For simplicity, place it at (6, 5, 0) replacing a wall tile.
    tiles = [
        (tx, ty, tz, tt) for (tx, ty, tz, tt) in tiles if not (tx == 6 and ty == 5)
    ]
    tiles.append((6, 5, 0, LT_SIGNPOST))
    return {
        "name": "waystation",
        "width": 8,
        "height": 6,
        "z_levels": 1,
        "tiles": tiles,
        "npc_spawns": [
            (3, 3, 0, "innkeeper"),
            (5, 3, 0, "traveler"),
        ],
        "item_spawns": [
            (1, 1, 0, "futon", 0.9),
            (6, 1, 0, "futon", 0.9),
            (3, 2, 0, "rice_ball", 0.7),
        ],
        "entrances": [(4, 5, 0)],
    }


def _build_castle_keep():
    """15x15 castle keep, 3 Z-levels, thick (2-tile) stone walls, gate."""
    tiles = []

    # --- Ground floor (z=0) ---
    for x in range(15):
        for y in range(15):
            # Thick outer wall: 2 tiles on each side
            if x <= 1 or x >= 13 or y <= 1 or y >= 13:
                tiles.append((x, y, 0, LT_CASTLE_WALL))
            else:
                tiles.append((x, y, 0, LT_STONE_FLOOR))
    # Gate at south center (clear wall tiles, place gate)
    for gx in (7,):
        for gy in (13, 14):
            tiles = [
                (tx, ty, tz, tt)
                for (tx, ty, tz, tt) in tiles
                if not (tx == gx and ty == gy and tz == 0)
            ]
            tiles.append((gx, gy, 0, LT_GATE))
    # Stairs up in corner
    tiles = [
        (tx, ty, tz, tt)
        for (tx, ty, tz, tt) in tiles
        if not (tx == 3 and ty == 3 and tz == 0)
    ]
    tiles.append((3, 3, 0, LT_STAIRS_UP))

    # --- Second floor (z=1) ---
    for x in range(15):
        for y in range(15):
            if x <= 1 or x >= 13 or y <= 1 or y >= 13:
                tiles.append((x, y, 1, LT_CASTLE_WALL))
            else:
                tiles.append((x, y, 1, LT_STONE_FLOOR))
    # Stairs down (from ground)
    tiles = [
        (tx, ty, tz, tt)
        for (tx, ty, tz, tt) in tiles
        if not (tx == 3 and ty == 3 and tz == 1)
    ]
    tiles.append((3, 3, 1, LT_STAIRS_DOWN))
    # Stairs up to third floor
    tiles = [
        (tx, ty, tz, tt)
        for (tx, ty, tz, tt) in tiles
        if not (tx == 11 and ty == 3 and tz == 1)
    ]
    tiles.append((11, 3, 1, LT_STAIRS_UP))

    # --- Third floor (z=2) ---
    for x in range(15):
        for y in range(15):
            if x <= 1 or x >= 13 or y <= 1 or y >= 13:
                tiles.append((x, y, 2, LT_CASTLE_WALL))
            else:
                tiles.append((x, y, 2, LT_STONE_FLOOR))
    # Stairs down from second floor
    tiles = [
        (tx, ty, tz, tt)
        for (tx, ty, tz, tt) in tiles
        if not (tx == 11 and ty == 3 and tz == 2)
    ]
    tiles.append((11, 3, 2, LT_STAIRS_DOWN))
    # Altar / throne at back center of top floor
    tiles = [
        (tx, ty, tz, tt)
        for (tx, ty, tz, tt) in tiles
        if not (tx == 7 and ty == 2 and tz == 2)
    ]
    tiles.append((7, 2, 2, LT_ALTAR))

    return {
        "name": "castle_keep",
        "width": 15,
        "height": 15,
        "z_levels": 3,
        "tiles": tiles,
        "npc_spawns": [
            (7, 7, 0, "samurai"),
            (5, 7, 0, "samurai"),
            (9, 7, 0, "samurai"),
            (7, 7, 1, "guard"),
            (7, 5, 2, "daimyo"),
        ],
        "item_spawns": [
            (7, 3, 2, "scroll", 0.6),
            (6, 2, 2, "gold", 0.4),
        ],
        "entrances": [(7, 13, 0), (7, 14, 0)],
    }


# ─────────────────────────────────────────────────────────────
# TEMPLATES registry
# ─────────────────────────────────────────────────────────────

TEMPLATES = {
    "small_house": _build_small_house(),
    "large_house": _build_large_house(),
    "inn": _build_inn(),
    "temple": _build_temple(),
    "shrine": _build_shrine(),
    "blacksmith": _build_blacksmith(),
    "market_stall": _build_market_stall(),
    "watchtower": _build_watchtower(),
    "waystation": _build_waystation(),
    "castle_keep": _build_castle_keep(),
}

# ─────────────────────────────────────────────────────────────
# OVERRIDES — location-specific POI customizations
# ─────────────────────────────────────────────────────────────

OVERRIDES = {
    "Edo": {
        "template": "castle_keep",
        "scale": 2.0,
        "desc": "Tokugawa stronghold, seat of the Shogunate",
    },
    "Kyoto": {
        "template": "castle_keep",
        "scale": 1.5,
        "desc": "Imperial Palace, ancient capital",
    },
    "Osaka": {
        "template": "castle_keep",
        "scale": 1.8,
        "desc": "Osaka Castle, merchant city fortress",
    },
    "Nagasaki": {
        "template": "inn",
        "scale": 1.3,
        "desc": "Foreign trading post, Dejima gateway",
    },
    "Kamakura": {
        "template": "temple",
        "scale": 1.5,
        "desc": "Great Buddha temple complex",
    },
    "Ise": {
        "template": "shrine",
        "scale": 2.0,
        "desc": "Grand Shrine of Ise, holiest Shinto site",
    },
}
