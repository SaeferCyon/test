"""Area map layer — 100x100 tile grid generated per region tile.

Each region tile expands into an AreaMap of AREA_W x AREA_H AreaTiles,
providing the intermediate zoom level between region and local maps.
"""

import math
import random

from data import (
    AREA_W,
    AREA_H,
    REGION_TO_LOCAL_BIOME,
    T_RIVER,
    T_SEA,
    T_DEEP_SEA,
    T_COAST,
    T_SWAMP,
    T_VILLAGE,
    T_TOWN,
    T_CASTLE,
    T_TEMPLE,
    T_ROAD,
    T_PORT,
    T_FOREST,
    T_PINE,
    T_BAMBOO,
    T_DENSE_FOREST,
    T_MOUNTAIN,
    T_HIGH_PEAK,
)


# ─────────────────────────────────────────────────────────────
# HELPER — deterministic seed from coordinates
# ─────────────────────────────────────────────────────────────


def generate_area_seed(region_col, region_row, area_x=0, area_y=0):
    """Return a deterministic integer seed from map coordinates.

    Same inputs always produce the same seed; different inputs produce
    different seeds (with very high probability).
    """
    # Large primes for mixing to minimise collisions.
    h = (
        region_col * 374761393
        + region_row * 668265263
        + area_x * 2147483647
        + area_y * 1500450271
    )
    # Collapse into a positive 64-bit value.
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFFFFFFFFFF
    return int(h)


# ─────────────────────────────────────────────────────────────
# VALUE NOISE (lightweight copy from world.py pattern)
# ─────────────────────────────────────────────────────────────


class _AreaNoise:
    """Simple value noise for area-level procedural variation."""

    __slots__ = ("table",)

    def __init__(self, seed):
        rng = random.Random(seed)
        self.table = [rng.random() for _ in range(512)]

    def _smooth(self, t):
        return t * t * t * (t * (t * 6 - 15) + 10)

    def get(self, x, y):
        xi = int(math.floor(x)) & 255
        yi = int(math.floor(y)) & 255
        xf = x - math.floor(x)
        yf = y - math.floor(y)
        u = self._smooth(xf)
        v = self._smooth(yf)
        a = self.table[(xi + yi * 13) % 512]
        b = self.table[(xi + 1 + yi * 13) % 512]
        c = self.table[(xi + (yi + 1) * 13) % 512]
        d = self.table[(xi + 1 + (yi + 1) * 13) % 512]
        x0 = a + (b - a) * u
        x1 = c + (d - c) * u
        return x0 + (x1 - x0) * v


# ─────────────────────────────────────────────────────────────
# AREA TILE
# ─────────────────────────────────────────────────────────────


class AreaTile:
    """Single tile within an area map."""

    __slots__ = (
        "biome",
        "base_elevation",
        "road_type",
        "road_dir",
        "building_type",
        "poi_ref",
        "vegetation_density",
        "is_water",
        "is_bridge",
    )

    def __init__(self):
        self.biome = "grassland"
        self.base_elevation = 0.0
        self.road_type = None
        self.road_dir = None
        self.building_type = None
        self.poi_ref = None
        self.vegetation_density = 0.0
        self.is_water = False
        self.is_bridge = False


# ─────────────────────────────────────────────────────────────
# BIOME VEGETATION DEFAULTS
# ─────────────────────────────────────────────────────────────

_BIOME_VEG = {
    "grassland": (0.1, 0.35),
    "farmland": (0.2, 0.5),
    "rice_paddy": (0.3, 0.6),
    "forest": (0.6, 0.9),
    "pine_forest": (0.5, 0.85),
    "bamboo_grove": (0.65, 0.95),
    "dense_forest": (0.75, 0.98),
    "mountain": (0.05, 0.3),
    "peak": (0.0, 0.1),
    "beach": (0.0, 0.1),
    "swamp": (0.4, 0.7),
    "river": (0.05, 0.2),
    "road": (0.0, 0.15),
    "village": (0.1, 0.3),
    "town": (0.05, 0.2),
    "castle_town": (0.05, 0.2),
    "temple_grounds": (0.3, 0.6),
    "hot_spring": (0.1, 0.3),
    "ruins": (0.2, 0.5),
    "port_town": (0.05, 0.15),
    "sea": (0.0, 0.0),
    "coast": (0.0, 0.05),
    "deep_sea": (0.0, 0.0),
}

# Terrain types that are predominantly water
_WATER_TERRAINS = {T_SEA, T_DEEP_SEA, T_COAST, T_RIVER}


# ─────────────────────────────────────────────────────────────
# AREA MAP
# ─────────────────────────────────────────────────────────────


class AreaMap:
    """100x100 area grid representing one region tile at higher detail."""

    def __init__(self, region_col, region_row):
        self.region_col = region_col
        self.region_row = region_row
        self.tiles = [[AreaTile() for _ in range(AREA_W)] for _ in range(AREA_H)]

    # ── access ────────────────────────────────────────────────

    def get_tile(self, x, y):
        """Return the AreaTile at (x, y) or None if out of bounds."""
        if 0 <= x < AREA_W and 0 <= y < AREA_H:
            return self.tiles[y][x]
        return None

    # ── generation ────────────────────────────────────────────

    def generate(self, region_terrain, region_elevation, seed):
        """Populate tiles from region data using deterministic RNG.

        Parameters
        ----------
        region_terrain : int
            Terrain constant from data.py (e.g. T_PLAINS).
        region_elevation : float
            Base elevation inherited from the region model.
        seed : int
            Deterministic seed for this area.
        """
        rng = random.Random(seed)
        noise = _AreaNoise(seed)

        biome = REGION_TO_LOCAL_BIOME.get(region_terrain, "grassland")
        veg_lo, veg_hi = _BIOME_VEG.get(biome, (0.1, 0.3))
        is_water_terrain = region_terrain in _WATER_TERRAINS

        # Fill base tiles
        for r in range(AREA_H):
            for c in range(AREA_W):
                tile = self.tiles[r][c]
                tile.biome = biome

                # Elevation with noise variation
                n = noise.get(c * 0.08, r * 0.08)
                tile.base_elevation = max(
                    0.0, min(10.0, region_elevation + (n - 0.5) * 2.0)
                )

                # Vegetation
                vn = noise.get(c * 0.12 + 100.0, r * 0.12 + 100.0)
                tile.vegetation_density = veg_lo + (veg_hi - veg_lo) * vn

                # Water
                if is_water_terrain:
                    tile.is_water = True
                    tile.vegetation_density = 0.0

        # Swamp: partial water patches
        if region_terrain == T_SWAMP:
            self._gen_swamp_water(noise)

        # River: carve a water channel across the area
        if region_terrain == T_RIVER:
            self._gen_river_channel(rng)

        # Settlement generation
        if region_terrain == T_VILLAGE:
            self._gen_village(rng)
        elif region_terrain in (T_TOWN, T_PORT):
            self._gen_town(rng)
        elif region_terrain == T_CASTLE:
            self._gen_castle(rng)
        elif region_terrain == T_TEMPLE:
            self._gen_temple(rng)

    # ── road placement ────────────────────────────────────────

    def place_road(self, entry_side, exit_side, road_type="highway"):
        """Draw a road across the area map between two sides.

        Parameters
        ----------
        entry_side, exit_side : str
            One of "north", "south", "east", "west".
        road_type : str
            "highway", "secondary", or "path".
        """
        start = self._side_midpoint(entry_side)
        end = self._side_midpoint(exit_side)
        if start is None or end is None:
            return

        sx, sy = start
        ex, ey = end

        # Simple Bresenham-ish walk with slight random curve
        rng = random.Random(
            generate_area_seed(self.region_col, self.region_row, sx, sy)
        )

        cx, cy = float(sx), float(sy)
        steps = max(abs(ex - sx), abs(ey - sy), 1)
        dx = (ex - sx) / steps
        dy = (ey - sy) / steps

        for _ in range(steps + 1):
            ix, iy = int(round(cx)), int(round(cy))
            # Paint a 1-wide road (with slight jitter)
            for offset in range(-1, 2):
                if abs(dx) >= abs(dy):
                    tx, ty = ix, iy + offset
                else:
                    tx, ty = ix + offset, iy
                tile = self.get_tile(tx, ty)
                if tile is not None:
                    tile.road_type = road_type
                    tile.road_dir = (
                        1 if dx > 0 else (-1 if dx < 0 else 0),
                        1 if dy > 0 else (-1 if dy < 0 else 0),
                    )
                    if tile.is_water:
                        tile.is_bridge = True
                    tile.vegetation_density *= 0.2
            cx += dx + rng.uniform(-0.3, 0.3)
            cy += dy + rng.uniform(-0.3, 0.3)
            # Clamp to bounds
            cx = max(0.0, min(float(AREA_W - 1), cx))
            cy = max(0.0, min(float(AREA_H - 1), cy))

    # ── private generators ────────────────────────────────────

    def _side_midpoint(self, side):
        """Return (x, y) at the midpoint of the given map edge."""
        mid_x = AREA_W // 2
        mid_y = AREA_H // 2
        if side == "north":
            return (mid_x, 0)
        if side == "south":
            return (mid_x, AREA_H - 1)
        if side == "west":
            return (0, mid_y)
        if side == "east":
            return (AREA_W - 1, mid_y)
        return None

    def _gen_swamp_water(self, noise):
        """Scatter water patches through a swamp area."""
        for r in range(AREA_H):
            for c in range(AREA_W):
                n = noise.get(c * 0.15 + 200.0, r * 0.15 + 200.0)
                if n > 0.55:
                    self.tiles[r][c].is_water = True
                    self.tiles[r][c].vegetation_density *= 0.5

    def _gen_river_channel(self, rng):
        """Carve a winding river channel through the map."""
        cx = AREA_W // 2 + rng.randint(-10, 10)
        width = rng.randint(3, 6)
        for r in range(AREA_H):
            cx += rng.randint(-1, 1)
            cx = max(width, min(AREA_W - width - 1, cx))
            for c in range(cx - width, cx + width + 1):
                if 0 <= c < AREA_W:
                    self.tiles[r][c].is_water = True
                    self.tiles[r][c].vegetation_density = 0.0
            # Shore vegetation
            for c in (cx - width - 1, cx + width + 1):
                if 0 <= c < AREA_W:
                    self.tiles[r][c].vegetation_density = min(
                        0.8, self.tiles[r][c].vegetation_density + 0.3
                    )

    def _gen_village(self, rng):
        """Place a village: road with 5-15 buildings along it."""
        self.place_road("west", "east", "secondary")
        num_buildings = rng.randint(5, 15)
        road_y = AREA_H // 2
        placed = 0
        attempts = 0
        while placed < num_buildings and attempts < num_buildings * 5:
            attempts += 1
            bx = rng.randint(10, AREA_W - 11)
            side = rng.choice([-1, 1])
            by = road_y + side * rng.randint(3, 8)
            if not (0 <= by < AREA_H):
                continue
            tile = self.tiles[by][bx]
            if tile.building_type is not None or tile.is_water:
                continue
            tile.building_type = rng.choice(
                [
                    "house",
                    "house",
                    "house",
                    "storehouse",
                    "workshop",
                    "inn",
                    "shrine",
                ]
            )
            tile.vegetation_density = 0.0
            placed += 1

    def _gen_town(self, rng):
        """Place a town: grid of buildings with market centre."""
        self.place_road("north", "south", "highway")
        self.place_road("west", "east", "highway")

        cx, cy = AREA_W // 2, AREA_H // 2
        # Market square
        for dr in range(-3, 4):
            for dc in range(-3, 4):
                tile = self.get_tile(cx + dc, cy + dr)
                if tile:
                    tile.building_type = "market"
                    tile.vegetation_density = 0.0

        # Building grid around centre
        building_types = [
            "house",
            "house",
            "house",
            "shop",
            "shop",
            "warehouse",
            "inn",
            "shrine",
            "workshop",
        ]
        for dr in range(-20, 21, 5):
            for dc in range(-20, 21, 5):
                if abs(dr) <= 3 and abs(dc) <= 3:
                    continue  # skip market area
                bx, by = cx + dc, cy + dr
                tile = self.get_tile(bx, by)
                if tile and not tile.is_water and tile.road_type is None:
                    tile.building_type = rng.choice(building_types)
                    tile.vegetation_density = 0.0

    def _gen_castle(self, rng):
        """Place a castle: central keep, walls, surrounding town."""
        cx, cy = AREA_W // 2, AREA_H // 2

        # Inner keep (3x3)
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                tile = self.get_tile(cx + dc, cy + dr)
                if tile:
                    tile.building_type = "keep"
                    tile.vegetation_density = 0.0

        # Castle walls (ring at radius 6-7)
        for dr in range(-7, 8):
            for dc in range(-7, 8):
                dist = max(abs(dr), abs(dc))
                if dist in (6, 7):
                    tile = self.get_tile(cx + dc, cy + dr)
                    if tile:
                        tile.building_type = "wall"
                        tile.vegetation_density = 0.0

        # Surrounding town buildings
        building_types = [
            "house",
            "house",
            "shop",
            "barracks",
            "warehouse",
            "inn",
            "shrine",
        ]
        for dr in range(-25, 26, 4):
            for dc in range(-25, 26, 4):
                dist = max(abs(dr), abs(dc))
                if dist <= 8 or dist > 25:
                    continue
                bx, by = cx + dc + rng.randint(-1, 1), cy + dr + rng.randint(-1, 1)
                tile = self.get_tile(bx, by)
                if tile and not tile.is_water and tile.building_type is None:
                    tile.building_type = rng.choice(building_types)
                    tile.vegetation_density = 0.0

        # Roads from gates
        self.place_road("north", "south", "highway")
        self.place_road("west", "east", "highway")

    def _gen_temple(self, rng):
        """Place a temple complex: main hall, gate, garden."""
        cx, cy = AREA_W // 2, AREA_H // 2

        # Main hall
        for dr in range(-2, 3):
            for dc in range(-3, 4):
                tile = self.get_tile(cx + dc, cy + dr)
                if tile:
                    tile.building_type = "temple_hall"
                    tile.vegetation_density = 0.0

        # Torii gate south of hall
        for dc in range(-1, 2):
            tile = self.get_tile(cx + dc, cy + 10)
            if tile:
                tile.building_type = "torii_gate"
                tile.vegetation_density = 0.0

        # Garden around temple
        for dr in range(-8, 9):
            for dc in range(-8, 9):
                dist = max(abs(dr), abs(dc))
                if 3 <= dist <= 8:
                    tile = self.get_tile(cx + dc, cy + dr)
                    if tile and tile.building_type is None:
                        tile.vegetation_density = min(
                            0.9, tile.vegetation_density + 0.3
                        )

        # Approach path
        self.place_road("south", "north", "path")
