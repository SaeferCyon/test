"""
region_map.py - Region Map Layer for ENGI
Wraps the existing World class as the travel/region tier of the 3-tier map system.
Adds GameWorld facade that coordinates region, area, and local map layers.
"""

import random
from data import *
from world import World, geo_to_grid, grid_to_geo, ValueNoise
from area_map import AreaMap, generate_area_seed
from local_map import LocalMap
from local_gen import LocalGenerator
from chunk_manager import ChunkManager
from save_manager import SaveManager
from road_network import RoadNetwork
from poi_loader import POILoader


class RegionMap:
    """Thin wrapper around World that identifies it as the region (travel) tier."""

    def __init__(self, world=None):
        self.world = world or World()

    def generate(self, seed=12345):
        self.world.generate(seed)

    @property
    def tiles(self):
        return self.world.tiles

    @property
    def npcs(self):
        return self.world.npcs

    @property
    def items(self):
        return self.world.items

    @property
    def cities(self):
        return self.world.cities

    def get_tile(self, col, row):
        return self.world.get_tile(col, row)

    def is_walkable(self, col, row):
        return self.world.is_walkable(col, row)

    def compute_fov(self, col, row, radius):
        return self.world.compute_fov(col, row, radius)

    def get_feature_desc(self, col, row):
        return self.world.get_feature_desc(col, row)

    def move_npc(self, npc, new_col, new_row):
        return self.world.move_npc(npc, new_col, new_row)

    def remove_npc(self, npc):
        return self.world.remove_npc(npc)

    def get_terrain_at(self, col, row):
        """Get terrain type ID at region coordinates."""
        tile = self.world.get_tile(col, row)
        if tile:
            return tile.terrain
        return T_DEEP_SEA

    def get_elevation_at(self, col, row):
        """Get elevation at region coordinates."""
        tile = self.world.get_tile(col, row)
        if tile:
            return tile.elevation
        return 0.0


class GameWorld:
    """Unified world interface coordinating all three map tiers.

    Provides the single point of access for:
    - Region map (travel): 240x130, ~1km per tile
    - Area map (mid-tier): 100x100 per region tile, ~100m per tile
    - Local map (gameplay): 100x100x64 per area tile, 1m per tile with Z-levels
    """

    def __init__(self, seed=12345, save_dir="saves"):
        self.seed = seed
        self.region_map = RegionMap()
        self.chunk_manager = ChunkManager()
        self.save_manager = SaveManager(save_dir=save_dir)
        self.road_network = RoadNetwork()
        self.poi_loader = POILoader()
        self.generator = LocalGenerator(seed)
        self.chunk_manager.generator = self.generator

        # Current local map (the one the player is on, or None if on travel map)
        self.current_local = None

        # Player's position in the local map
        self.local_player_x = 0
        self.local_player_y = 0
        self.local_player_z = SURFACE_Z

        # Which region tile the player is viewing locally
        self.local_region_col = 0
        self.local_region_row = 0
        self.local_area_x = 0
        self.local_area_y = 0

    def generate_region(self):
        """Generate the region (travel) map."""
        self.region_map.generate(self.seed)

    def enter_local(self, region_col, region_row, area_x=None, area_y=None):
        """Transition from travel map to local map at the given region tile.

        Returns the LocalMap the player enters, or None if the tile is not enterable.
        """
        terrain = self.region_map.get_terrain_at(region_col, region_row)
        elevation = self.region_map.get_elevation_at(region_col, region_row)

        # Default to center of area map
        if area_x is None:
            area_x = AREA_W // 2
        if area_y is None:
            area_y = AREA_H // 2

        # Get or generate the local map
        local_map = self.chunk_manager.get_local_map(
            region_col, region_row, area_x, area_y,
            terrain, elevation
        )

        if local_map is None:
            return None

        self.current_local = local_map
        self.local_region_col = region_col
        self.local_region_row = region_row
        self.local_area_x = area_x
        self.local_area_y = area_y

        # Place player at center of local map, on the surface
        from z_level import find_surface
        self.local_player_x = LOCAL_W // 2
        self.local_player_y = LOCAL_H // 2
        col = local_map.get_column(self.local_player_x, self.local_player_y)
        if col:
            self.local_player_z = find_surface(col)
        else:
            self.local_player_z = SURFACE_Z

        return local_map

    def exit_local(self):
        """Transition from local map back to travel map.

        Saves the current chunk if modified.
        """
        if self.current_local and self.current_local.modified:
            if self.save_manager and self.chunk_manager.save_manager:
                self.chunk_manager.save_manager.save_chunk(
                    self.chunk_manager.save_slot or "default",
                    self.local_region_col, self.local_region_row,
                    self.local_area_x, self.local_area_y,
                    self.current_local.to_save_data()
                )
        self.current_local = None

    def is_in_local(self):
        """True if the player is currently on a local map."""
        return self.current_local is not None

    def move_to_adjacent_area(self, direction):
        """Move to an adjacent area tile when the player reaches the edge.

        direction: "north", "south", "east", "west"
        Returns new LocalMap or None if can't move.
        """
        dx, dy = {"north": (0, -1), "south": (0, 1),
                  "east": (1, 0), "west": (-1, 0)}.get(direction, (0, 0))

        new_ax = self.local_area_x + dx
        new_ay = self.local_area_y + dy

        # Check if we've left the current region tile
        new_rc = self.local_region_col
        new_rr = self.local_region_row
        if new_ax < 0:
            new_rc -= 1
            new_ax = AREA_W - 1
        elif new_ax >= AREA_W:
            new_rc += 1
            new_ax = 0
        if new_ay < 0:
            new_rr -= 1
            new_ay = AREA_H - 1
        elif new_ay >= AREA_H:
            new_rr += 1
            new_ay = 0

        # Bounds check on region map
        if not (0 <= new_rc < WORLD_W and 0 <= new_rr < WORLD_H):
            return None

        terrain = self.region_map.get_terrain_at(new_rc, new_rr)
        elevation = self.region_map.get_elevation_at(new_rc, new_rr)

        local_map = self.chunk_manager.get_local_map(
            new_rc, new_rr, new_ax, new_ay, terrain, elevation
        )

        if local_map:
            self.current_local = local_map
            self.local_region_col = new_rc
            self.local_region_row = new_rr
            self.local_area_x = new_ax
            self.local_area_y = new_ay
            # Position player at the entry edge
            if direction == "north":
                self.local_player_y = LOCAL_H - 1
            elif direction == "south":
                self.local_player_y = 0
            elif direction == "east":
                self.local_player_x = 0
            elif direction == "west":
                self.local_player_x = LOCAL_W - 1

        return local_map

    def get_location_name(self, region_col, region_row):
        """Get the name of the location at a region tile, if any."""
        tile = self.region_map.get_tile(region_col, region_row)
        if tile and tile.feature:
            return tile.feature.get("name", "")
        return ""

    def get_local_tile(self, x, y, z):
        """Get tile from current local map."""
        if self.current_local:
            return self.current_local.get_tile(x, y, z)
        return None
