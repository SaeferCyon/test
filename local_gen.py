"""
local_gen.py - Procedural Generation Engine for ENGI

Generates 1:1 meter-scale local terrain (100x100 ZColumn grid)
from AreaTile data. Each biome produces distinct terrain patterns
using value noise and seeded RNG.
"""

import random

from world import ValueNoise
from data import (
    LOCAL_W,
    LOCAL_H,
    SURFACE_Z,
    LT_AIR,
    LT_DIRT,
    LT_GRASS,
    LT_TALL_GRASS,
    LT_MUD,
    LT_SAND,
    LT_GRAVEL,
    LT_ROCK,
    LT_SNOW,
    LT_TREE_TRUNK,
    LT_PINE_TRUNK,
    LT_BAMBOO_STALK,
    LT_BUSH,
    LT_FLOWERS,
    LT_RICE_PLANT,
    LT_CROP,
    LT_SHALLOW_WATER,
    LT_DEEP_WATER,
    LT_HOT_SPRING,
    LT_WOOD_WALL,
    LT_STONE_WALL,
    LT_CASTLE_WALL,
    LT_TATAMI,
    LT_WOOD_FLOOR,
    LT_STONE_FLOOR,
    LT_DOOR,
    LT_GATE,
    LT_TORII,
    LT_PACKED_EARTH,
    LT_STONE_ROAD,
    LT_DIRT_PATH,
    LT_WELL,
    LT_JIZO_STATUE,
    LT_CAVE_FLOOR,
    LT_BRIDGE,
    LT_FENCE,
)
from z_level import ZTile
from local_map import LocalMap


# ─────────────────────────────────────────────────────────────
# Biome dispatch table
# ─────────────────────────────────────────────────────────────

_BIOME_GENERATORS = {
    "grassland": "_gen_grassland",
    "forest": "_gen_forest",
    "pine_forest": "_gen_pine_forest",
    "bamboo_grove": "_gen_bamboo_grove",
    "dense_forest": "_gen_dense_forest",
    "mountain": "_gen_mountain",
    "peak": "_gen_peak",
    "beach": "_gen_beach",
    "swamp": "_gen_swamp",
    "farmland": "_gen_farmland",
    "rice_paddy": "_gen_rice_paddy",
    "river": "_gen_river",
    "village": "_generate_village",
    "town": "_generate_town",
    "castle_town": "_generate_castle",
    "temple_grounds": "_generate_temple",
    "road": "_gen_road_biome",
    "hot_spring": "_gen_hot_spring",
}


# ─────────────────────────────────────────────────────────────
# LocalGenerator
# ─────────────────────────────────────────────────────────────


class LocalGenerator:
    """Generates a LocalMap from AreaTile properties."""

    def __init__(self, seed):
        self.rng = random.Random(seed)
        self.noise = ValueNoise(seed)

    # ── public entry point ────────────────────────────────────

    def generate(self, local_map, area_tile):
        """Fill a LocalMap based on an AreaTile's properties."""
        biome = area_tile.biome
        method_name = _BIOME_GENERATORS.get(biome, "_gen_grassland")
        getattr(self, method_name)(local_map)
        self._apply_z_levels(local_map, area_tile.base_elevation)
        if area_tile.road_type is not None:
            self._apply_road(local_map, area_tile)
        if area_tile.building_type is not None:
            self._apply_building(local_map, area_tile)
        self._apply_vegetation_overlay(local_map, area_tile)

    # ── biome generators (surface Z=0) ────────────────────────

    def _gen_grassland(self, lm):
        """Grassland: mostly grass with patches of flowers/dirt."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                n = self.noise.get(x * 0.1, y * 0.1)
                if n > 0.85:
                    t = LT_FLOWERS
                elif n > 0.75:
                    t = LT_TALL_GRASS
                elif n < 0.08:
                    t = LT_DIRT
                else:
                    t = LT_GRASS
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_forest(self, lm):
        """Forest: grass ground with clustered trees."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                n = self.noise.get(x * 0.15, y * 0.15)
                if n > 0.6:
                    t = LT_TREE_TRUNK
                elif n > 0.5:
                    t = LT_BUSH
                else:
                    t = LT_GRASS
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_pine_forest(self, lm):
        """Pine forest: grass ground with pine tree clusters."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                n = self.noise.get(x * 0.14, y * 0.14)
                if n > 0.6:
                    t = LT_PINE_TRUNK
                elif n > 0.52:
                    t = LT_BUSH
                else:
                    t = LT_GRASS
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_bamboo_grove(self, lm):
        """Bamboo grove: grass with bamboo stalk clusters."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                n = self.noise.get(x * 0.12, y * 0.12)
                if n > 0.55:
                    t = LT_BAMBOO_STALK
                else:
                    t = LT_GRASS
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_dense_forest(self, lm):
        """Dense forest: heavy trees and bushes, little open ground."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                n = self.noise.get(x * 0.13, y * 0.13)
                if n > 0.45:
                    t = LT_TREE_TRUNK
                elif n > 0.3:
                    t = LT_BUSH
                elif n > 0.2:
                    t = LT_TALL_GRASS
                else:
                    t = LT_GRASS
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_mountain(self, lm):
        """Mountain: rock and gravel with sparse grass/dirt."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                n = self.noise.get(x * 0.08, y * 0.08)
                if n > 0.6:
                    t = LT_ROCK
                elif n > 0.4:
                    t = LT_GRAVEL
                elif n > 0.25:
                    t = LT_DIRT
                else:
                    t = LT_GRASS
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_peak(self, lm):
        """Peak: mostly rock with snow at high points."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                n = self.noise.get(x * 0.07, y * 0.07)
                if n > 0.7:
                    t = LT_SNOW
                elif n > 0.2:
                    t = LT_ROCK
                else:
                    t = LT_GRAVEL
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_beach(self, lm):
        """Beach: sand near water edge, grass further inland."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                # Water on the south side, sand middle, grass north
                ratio = y / LOCAL_H
                n = self.noise.get(x * 0.1, y * 0.1) * 0.15
                if ratio + n > 0.75:
                    t = LT_SHALLOW_WATER
                elif ratio + n > 0.4:
                    t = LT_SAND
                else:
                    t = LT_GRASS
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_swamp(self, lm):
        """Swamp: mud, shallow water, tall grass patches."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                n = self.noise.get(x * 0.12, y * 0.12)
                if n > 0.65:
                    t = LT_SHALLOW_WATER
                elif n > 0.45:
                    t = LT_MUD
                elif n > 0.3:
                    t = LT_TALL_GRASS
                else:
                    t = LT_MUD
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_farmland(self, lm):
        """Farmland: organized crop rows with dirt paths."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                if y % 6 == 0 or x % 20 == 0:
                    t = LT_DIRT
                elif y % 6 in (1, 2, 3, 4):
                    t = LT_CROP
                else:
                    t = LT_DIRT
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_rice_paddy(self, lm):
        """Rice paddy: flooded fields with rice plants."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                if y % 8 == 0 or x % 12 == 0:
                    t = LT_DIRT
                elif (y % 8) % 2 == 0:
                    t = LT_RICE_PLANT
                else:
                    t = LT_SHALLOW_WATER
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_river(self, lm):
        """River: deep water center, shallow edges, grass banks."""
        cx = LOCAL_W // 2
        for y in range(LOCAL_H):
            cx += self.rng.randint(-1, 1)
            cx = max(8, min(LOCAL_W - 9, cx))
            for x in range(LOCAL_W):
                dist = abs(x - cx)
                if dist <= 3:
                    t = LT_DEEP_WATER
                elif dist <= 6:
                    t = LT_SHALLOW_WATER
                else:
                    t = LT_GRASS
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    def _gen_road_biome(self, lm):
        """Road biome: grass with a road through the center."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                lm.set_tile(x, y, SURFACE_Z, ZTile(LT_GRASS))
        self._place_road(
            lm, LOCAL_W // 2, 0, LOCAL_W // 2, LOCAL_H - 1, LT_PACKED_EARTH
        )

    def _gen_hot_spring(self, lm):
        """Hot spring: central pool with rock surround."""
        cx, cy = LOCAL_W // 2, LOCAL_H // 2
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                dist = ((x - cx) ** 2 + (y - cy) ** 2) ** 0.5
                if dist < 8:
                    t = LT_HOT_SPRING
                elif dist < 14:
                    t = LT_ROCK
                elif dist < 20:
                    t = LT_GRAVEL
                else:
                    t = LT_GRASS
                lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    # ── settlement generators ─────────────────────────────────

    def _generate_village(self, lm):
        """Village: road through center, houses along it, well, shrine."""
        self._fill_ground(lm, LT_GRASS)
        self._place_road(
            lm, LOCAL_W // 2, 0, LOCAL_W // 2, LOCAL_H - 1, LT_PACKED_EARTH
        )
        road_x = LOCAL_W // 2
        placed = 0
        for _ in range(80):
            if placed >= 12:
                break
            bx = road_x + self.rng.choice([-1, 1]) * self.rng.randint(4, 12)
            by = self.rng.randint(10, LOCAL_H - 15)
            if not (0 <= bx < LOCAL_W - 6 and 0 <= by < LOCAL_H - 6):
                continue
            self._place_building(lm, bx, by, SURFACE_Z, 5, 5, LT_WOOD_WALL, LT_TATAMI)
            placed += 1
        # Well near center
        lm.set_tile(road_x - 3, LOCAL_H // 2, SURFACE_Z, ZTile(LT_WELL))
        # Shrine
        self._place_building(
            lm, road_x + 5, 5, SURFACE_Z, 4, 4, LT_WOOD_WALL, LT_WOOD_FLOOR
        )
        lm.set_tile(road_x + 5, 4, SURFACE_Z, ZTile(LT_TORII))

    def _generate_town(self, lm):
        """Town: grid streets, market square, many buildings."""
        self._fill_ground(lm, LT_GRASS)
        # Grid streets
        for gx in range(10, LOCAL_W - 10, 15):
            self._place_road(lm, gx, 5, gx, LOCAL_H - 6, LT_STONE_ROAD)
        for gy in range(10, LOCAL_H - 10, 15):
            self._place_road(lm, 5, gy, LOCAL_W - 6, gy, LT_STONE_ROAD)
        # Market square
        cx, cy = LOCAL_W // 2, LOCAL_H // 2
        for dy in range(-4, 5):
            for dx in range(-4, 5):
                lm.set_tile(cx + dx, cy + dy, SURFACE_Z, ZTile(LT_STONE_FLOOR))
        # Buildings in grid cells
        for gx in range(12, LOCAL_W - 15, 15):
            for gy in range(12, LOCAL_H - 15, 15):
                if abs(gx - cx) < 6 and abs(gy - cy) < 6:
                    continue
                w = self.rng.randint(5, 8)
                h = self.rng.randint(5, 6)
                self._place_building(
                    lm, gx, gy, SURFACE_Z, w, h, LT_WOOD_WALL, LT_TATAMI
                )

    def _generate_castle(self, lm):
        """Castle: central keep (multi-Z), inner/outer walls, moat."""
        self._fill_ground(lm, LT_GRASS)
        cx, cy = LOCAL_W // 2, LOCAL_H // 2
        # Moat (outer ring)
        self._draw_ring(lm, cx, cy, 28, 30, LT_DEEP_WATER)
        # Outer walls
        self._draw_ring(lm, cx, cy, 24, 26, LT_CASTLE_WALL)
        # Courtyard
        self._fill_rect(lm, cx - 23, cy - 23, 46, 46, LT_GRAVEL)
        # Inner walls
        self._draw_ring(lm, cx, cy, 12, 14, LT_CASTLE_WALL)
        # Inner courtyard
        self._fill_rect(lm, cx - 11, cy - 11, 22, 22, LT_STONE_FLOOR)
        # Central keep
        self._place_building(
            lm, cx - 5, cy - 4, SURFACE_Z, 10, 8, LT_CASTLE_WALL, LT_STONE_FLOOR
        )
        # Keep upper floor (Z=1)
        self._place_building(
            lm, cx - 5, cy - 4, 1, 10, 8, LT_CASTLE_WALL, LT_STONE_FLOOR
        )
        # Gates
        for gx, gy in [(cx, cy - 26), (cx, cy + 26), (cx - 26, cy), (cx + 26, cy)]:
            lm.set_tile(gx, gy, SURFACE_Z, ZTile(LT_GATE))
        # Town buildings outside moat
        for _ in range(15):
            bx = self.rng.randint(5, LOCAL_W - 12)
            by = self.rng.randint(5, LOCAL_H - 12)
            dist = max(abs(bx - cx), abs(by - cy))
            if dist > 32:
                self._place_building(
                    lm, bx, by, SURFACE_Z, 5, 5, LT_WOOD_WALL, LT_TATAMI
                )

    def _generate_temple(self, lm):
        """Temple: torii gate, path, main hall, garden, pond."""
        self._fill_ground(lm, LT_GRASS)
        cx, cy = LOCAL_W // 2, LOCAL_H // 2
        # Approach path from south
        self._place_road(lm, cx, LOCAL_H - 5, cx, cy + 12, LT_STONE_ROAD)
        # Torii gate
        for dx in range(-1, 2):
            lm.set_tile(cx + dx, LOCAL_H - 10, SURFACE_Z, ZTile(LT_TORII))
        # Main hall
        self._place_building(
            lm, cx - 5, cy - 4, SURFACE_Z, 10, 8, LT_WOOD_WALL, LT_TATAMI
        )
        # Garden around hall (trees and flowers)
        for dy in range(-15, 16):
            for dx in range(-15, 16):
                gx, gy = cx + dx, cy + dy
                if not (0 <= gx < LOCAL_W and 0 <= gy < LOCAL_H):
                    continue
                dist = (dx**2 + dy**2) ** 0.5
                if 8 < dist < 15:
                    n = self.noise.get(gx * 0.2, gy * 0.2)
                    if n > 0.7:
                        lm.set_tile(gx, gy, SURFACE_Z, ZTile(LT_TREE_TRUNK))
                    elif n > 0.6:
                        lm.set_tile(gx, gy, SURFACE_Z, ZTile(LT_FLOWERS))
        # Pond
        for dy in range(-4, 5):
            for dx in range(-5, 6):
                px, py = cx + dx + 12, cy + dy
                if (dx**2 + dy**2) ** 0.5 < 4.5:
                    if 0 <= px < LOCAL_W and 0 <= py < LOCAL_H:
                        lm.set_tile(px, py, SURFACE_Z, ZTile(LT_SHALLOW_WATER))

    # ── Z-level terrain ───────────────────────────────────────

    def _apply_z_levels(self, lm, base_elevation):
        """Fill Z-levels based on area_tile.base_elevation."""
        elev = int(base_elevation)
        if elev <= 2:
            return  # flat terrain, only Z=0
        if elev <= 5:
            self._apply_gentle_hills(lm, elev)
        elif elev <= 8:
            self._apply_mountains(lm, elev)
        else:
            self._apply_peaks(lm, elev)

    def _apply_gentle_hills(self, lm, elev):
        """Gentle hills: fill sub-surface with rock, surface on top."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                n = self.noise.get(x * 0.05, y * 0.05)
                h = int(n * elev)
                for z in range(-1, h):
                    lm.set_tile(x, y, z, ZTile(LT_ROCK))
                surface = lm.get_tile(x, y, SURFACE_Z)
                if surface and h > 0:
                    lm.set_tile(x, y, h, ZTile(surface.terrain))

    def _apply_mountains(self, lm, elev):
        """Mountains: multi-Z rock, some cave floors at negative Z."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                n = self.noise.get(x * 0.04, y * 0.04)
                h = int(n * elev)
                for z in range(-2, h):
                    lm.set_tile(x, y, z, ZTile(LT_ROCK))
                # Cave floors at negative Z
                if n < 0.3:
                    lm.set_tile(x, y, -1, ZTile(LT_CAVE_FLOOR))
                surface = lm.get_tile(x, y, SURFACE_Z)
                if surface and h > 0:
                    lm.set_tile(x, y, h, ZTile(surface.terrain))

    def _apply_peaks(self, lm, elev):
        """Peaks: tall rock columns with snow on top."""
        capped = min(elev, 10)
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                n = self.noise.get(x * 0.03, y * 0.03)
                h = int(n * capped)
                for z in range(-3, h):
                    lm.set_tile(x, y, z, ZTile(LT_ROCK))
                if h > 0:
                    lm.set_tile(x, y, h, ZTile(LT_SNOW))

    # ── road placement ────────────────────────────────────────

    def _apply_road(self, lm, area_tile):
        """Place a road across the map based on area_tile road info."""
        rt = area_tile.road_type
        road_tile = LT_STONE_ROAD if rt == "highway" else LT_PACKED_EARTH
        dx, dy = area_tile.road_dir or (0, 1)
        if abs(dx) >= abs(dy):
            sx, sy = 0, LOCAL_H // 2
            ex, ey = LOCAL_W - 1, LOCAL_H // 2
        else:
            sx, sy = LOCAL_W // 2, 0
            ex, ey = LOCAL_W // 2, LOCAL_H - 1
        width = 3 if rt == "highway" else (2 if rt == "secondary" else 1)
        self._place_road(lm, sx, sy, ex, ey, road_tile, width)

    def _place_road(self, lm, sx, sy, ex, ey, road_type, width=2):
        """Draw a road between two points at Z=0."""
        steps = max(abs(ex - sx), abs(ey - sy), 1)
        dx = (ex - sx) / steps
        dy = (ey - sy) / steps
        cx, cy = float(sx), float(sy)
        for _ in range(steps + 1):
            ix, iy = int(round(cx)), int(round(cy))
            half = width // 2
            for off in range(-half, half + 1):
                if abs(dx) >= abs(dy):
                    tx, ty = ix, iy + off
                else:
                    tx, ty = ix + off, iy
                if 0 <= tx < LOCAL_W and 0 <= ty < LOCAL_H:
                    lm.set_tile(tx, ty, SURFACE_Z, ZTile(road_type))
            cx += dx
            cy += dy

    # ── building placement ────────────────────────────────────

    def _apply_building(self, lm, area_tile):
        """Place a building based on area_tile.building_type."""
        bt = area_tile.building_type
        sizes = {
            "house": (5, 5),
            "inn": (8, 6),
            "temple": (10, 8),
            "shop": (5, 5),
            "workshop": (6, 6),
            "shrine": (4, 4),
        }
        w, h = sizes.get(bt, (5, 5))
        bx = (LOCAL_W - w) // 2
        by = (LOCAL_H - h) // 2
        self._place_building(lm, bx, by, SURFACE_Z, w, h, LT_WOOD_WALL, LT_TATAMI)

    def _place_building(self, lm, x, y, z, w, h, wall_type, floor_type):
        """Place a rectangular building with walls and floor."""
        for dy in range(h):
            for dx in range(w):
                bx, by = x + dx, y + dy
                if not (0 <= bx < LOCAL_W and 0 <= by < LOCAL_H):
                    continue
                is_wall = dx == 0 or dx == w - 1 or dy == 0 or dy == h - 1
                if is_wall:
                    lm.set_tile(bx, by, z, ZTile(wall_type))
                else:
                    lm.set_tile(bx, by, z, ZTile(floor_type))
        # Door at bottom center
        door_x = x + w // 2
        door_y = y + h - 1
        if 0 <= door_x < LOCAL_W and 0 <= door_y < LOCAL_H:
            lm.set_tile(door_x, door_y, z, ZTile(LT_DOOR))

    # ── vegetation overlay ────────────────────────────────────

    def _apply_vegetation_overlay(self, lm, area_tile):
        """Scale vegetation based on area_tile.vegetation_density."""
        vd = area_tile.vegetation_density
        if vd < 0.05:
            return
        # Sparse: add a few trees/bushes on grass tiles
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                tile = lm.get_tile(x, y, SURFACE_Z)
                if tile is None or tile.terrain != LT_GRASS:
                    continue
                n = self.noise.get(x * 0.18 + 50, y * 0.18 + 50)
                if n > (1.0 - vd * 0.4):
                    t = LT_TREE_TRUNK if n > 0.9 else LT_BUSH
                    lm.set_tile(x, y, SURFACE_Z, ZTile(t))

    # ── utility helpers ───────────────────────────────────────

    def _fill_ground(self, lm, terrain):
        """Fill entire surface with a single terrain type."""
        for y in range(LOCAL_H):
            for x in range(LOCAL_W):
                lm.set_tile(x, y, SURFACE_Z, ZTile(terrain))

    def _fill_rect(self, lm, x, y, w, h, terrain):
        """Fill a rectangle at Z=0 with the given terrain."""
        for dy in range(h):
            for dx in range(w):
                rx, ry = x + dx, y + dy
                if 0 <= rx < LOCAL_W and 0 <= ry < LOCAL_H:
                    lm.set_tile(rx, ry, SURFACE_Z, ZTile(terrain))

    def _draw_ring(self, lm, cx, cy, inner_r, outer_r, terrain):
        """Draw a ring of terrain between inner and outer radius."""
        for dy in range(-outer_r - 1, outer_r + 2):
            for dx in range(-outer_r - 1, outer_r + 2):
                dist = (dx**2 + dy**2) ** 0.5
                if inner_r <= dist <= outer_r:
                    rx, ry = cx + dx, cy + dy
                    if 0 <= rx < LOCAL_W and 0 <= ry < LOCAL_H:
                        lm.set_tile(rx, ry, SURFACE_Z, ZTile(terrain))
