"""Chunk Manager — LRU cache for local map streaming.

Manages loading, generating, caching, and saving of LocalMap chunks
using an OrderedDict-based LRU eviction strategy.
"""

import random
from collections import OrderedDict

from area_map import AreaMap, generate_area_seed
from data import AREA_H, AREA_W, CHUNK_CACHE_MAX, CHUNK_PRELOAD_RADIUS
from local_map import LocalMap
from save_manager import deserialize_chunk, serialize_chunk


class ChunkManager:
    """LRU-cached chunk loader for streaming local maps on demand."""

    def __init__(self, save_manager=None, save_slot=None):
        self.cache = (
            OrderedDict()
        )  # (region_col, region_row, area_x, area_y) -> LocalMap
        self.max_cache = CHUNK_CACHE_MAX
        self.area_cache = {}  # (region_col, region_row) -> AreaMap
        self.save_manager = save_manager
        self.save_slot = save_slot
        self.generator = None  # set externally (LocalGenerator)

    # -- area map caching ---------------------------------------------------

    def get_area_map(self, region_col, region_row, region_terrain, region_elevation):
        """Return cached AreaMap for the region tile, generating if needed."""
        key = (region_col, region_row)
        if key in self.area_cache:
            return self.area_cache[key]
        seed = generate_area_seed(region_col, region_row)
        area_map = AreaMap(region_col, region_row)
        area_map.generate(region_terrain, region_elevation, seed)
        self.area_cache[key] = area_map
        return area_map

    # -- local map access ---------------------------------------------------

    def get_local_map(
        self, region_col, region_row, area_x, area_y, region_terrain, region_elevation
    ):
        """Return the LocalMap for the given coordinates, using cache/save/gen."""
        key = (region_col, region_row, area_x, area_y)

        # Cache hit — move to end for LRU freshness
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]

        # Try loading from save
        local_map = self._load_from_save(key)

        # Generate new if not saved
        if local_map is None:
            local_map = self._generate_chunk(
                region_col,
                region_row,
                area_x,
                area_y,
                region_terrain,
                region_elevation,
            )

        # Insert into cache, evict if over capacity
        self.cache[key] = local_map
        if len(self.cache) > self.max_cache:
            self.evict_lru()

        return local_map

    # -- eviction -----------------------------------------------------------

    def evict_chunk(self, key):
        """Evict a specific chunk, saving if modified."""
        if key not in self.cache:
            return
        chunk = self.cache[key]
        if chunk.modified:
            self._save_chunk(key, chunk)
        del self.cache[key]

    def evict_lru(self):
        """Evict the oldest (least-recently-used) cache entry."""
        if not self.cache:
            return
        key, chunk = self.cache.popitem(last=False)
        if chunk.modified:
            self._save_chunk(key, chunk)

    # -- bulk operations ----------------------------------------------------

    def save_all_modified(self):
        """Persist every modified chunk in the cache."""
        for key, chunk in self.cache.items():
            if chunk.modified:
                self._save_chunk(key, chunk)

    def clear_cache(self):
        """Save all modified chunks, then empty the cache."""
        self.save_all_modified()
        self.cache.clear()

    # -- preloading ---------------------------------------------------------

    def preload_adjacent(
        self, region_col, region_row, area_x, area_y, region_terrain, region_elevation
    ):
        """Preload chunks within CHUNK_PRELOAD_RADIUS of the position."""
        r = CHUNK_PRELOAD_RADIUS
        for dy in range(-r, r + 1):
            for dx in range(-r, r + 1):
                nx = area_x + dx
                ny = area_y + dy
                # Skip out-of-bounds area coordinates
                if nx < 0 or nx >= AREA_W or ny < 0 or ny >= AREA_H:
                    continue
                key = (region_col, region_row, nx, ny)
                if key in self.cache:
                    continue
                self.get_local_map(
                    region_col,
                    region_row,
                    nx,
                    ny,
                    region_terrain,
                    region_elevation,
                )

    # -- info ---------------------------------------------------------------

    def get_cache_size(self):
        """Return the number of chunks currently cached."""
        return len(self.cache)

    # -- private helpers ----------------------------------------------------

    def _load_from_save(self, key):
        """Attempt to load a chunk from the save manager."""
        if self.save_manager is None or self.save_slot is None:
            return None
        region_col, region_row, area_x, area_y = key
        chunk_data = self.save_manager.load_chunk(
            self.save_slot,
            region_col,
            region_row,
            area_x,
            area_y,
        )
        if chunk_data is None:
            return None
        return LocalMap.from_save_data(chunk_data)

    def _generate_chunk(
        self, region_col, region_row, area_x, area_y, region_terrain, region_elevation
    ):
        """Generate a fresh LocalMap for the given coordinates."""
        area_map = self.get_area_map(
            region_col,
            region_row,
            region_terrain,
            region_elevation,
        )
        area_tile = area_map.get_tile(area_x, area_y)
        seed = generate_area_seed(region_col, region_row, area_x, area_y)
        local_map = LocalMap(region_col, region_row, area_x, area_y)
        if self.generator:
            self.generator.rng = random.Random(seed)
            self.generator.generate(local_map, area_tile)
        return local_map

    def _save_chunk(self, key, chunk):
        """Persist a single chunk via the save manager."""
        if self.save_manager is None or self.save_slot is None:
            return
        region_col, region_row, area_x, area_y = key
        self.save_manager.save_chunk(
            self.save_slot,
            region_col,
            region_row,
            area_x,
            area_y,
            chunk.to_save_data(),
        )
        chunk.modified = False
