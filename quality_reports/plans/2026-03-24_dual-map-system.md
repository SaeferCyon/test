# Plan: Dual Map System with 1:1 Scale, Z-Levels, and Clan Simulation

**Ticket:** FR-1774377928 | **Milestone:** local | **Readiness:** 78/100
**Branch:** feature-1774377928

## Context

Implement a three-tier map hierarchy (region -> area -> local) for the ENGI roguelike,
transforming the game from a single 240x130 overview grid into a dual-map system with
1:1 meter-scale local maps, ±32 Z-levels, full Sengoku clan simulation, historical
Gokaido road network with waystations, and full world state persistence via SQLite +
compressed flat files.

Selected Approach: C — True 1:1 Streaming with Region Hierarchy (Dwarf Fortress-style)

## Impact Analysis

- Files affected: 8 new + 6 modified = 14 total
- Highest risk: HIGH (world.py refactor into region_map.py, game.py transition system)
- Affected test packages: all (new test files needed)
- This is a foundational architecture change — all existing modules are impacted

## Approach

Three-tier map hierarchy with deterministic seeding:
- Region Map (existing 240x130 grid) serves as travel map
- Area Map (~100x100 per region tile, ~100m² each) provides mid-tier structure
- Local Map (100x100x64 per area tile, ±32 Z-levels, 1:1 meter scale) is primary gameplay
- Explicit enter/exit transition between travel and local
- Deterministic procedural generation from coordinate-based seeds
- Hybrid POI system: templates for common structures, JSON overrides for historical locations
- Full clan simulation with dynamic territories
- SQLite + compressed flat files for full world state persistence

## Tasks

### Task 1: Core Data Structures & Constants
- **Files:** `data.py` (modify), `clan_data.py` (create)
- **Depends on:** none
- **Blocks:** Tasks 2, 3, 4, 5, 6, 7, 8, 9
- **Size:** L
- **Description:** Define new terrain types for local-scale map (grass varieties, individual
  trees, building wall/floor/door/window tiles, cave tiles, road surface, sign posts, stair
  tiles, ladder tiles). Add Z-level constants (MIN_Z=-32, MAX_Z=31, SURFACE_Z=0). Extend
  WORLD constants for area/local tile sizes (AREA_W=100, AREA_H=100, LOCAL_W=100, LOCAL_H=100,
  Z_LEVELS=64). Define all ~50+ Sengoku clans with territory, daimyo, capital, relations,
  military strength in clan_data.py. Define Gokaido waystation data. Define POI template types.

### Task 2: Z-Level Data Structures
- **Files:** `z_level.py` (create)
- **Depends on:** Task 1
- **Blocks:** Tasks 3, 5, 6
- **Size:** M
- **Description:** Create ZTile class (terrain, elevation, items, npc_id, feature per level).
  ZColumn class (sparse dict of z-level -> ZTile, with air as default). Vertical navigation
  rules (stairs connect Z and Z+1, ladders allow climbing, climbable terrain like cliff faces,
  fall damage calculation). Surface detection (find ground level at any x,y). Utility functions:
  is_solid(x,y,z), is_air(x,y,z), get_surface_z(x,y), can_move_vertical(x,y,z,direction).

### Task 3: Local Map Core
- **Files:** `local_map.py` (create)
- **Depends on:** Tasks 1, 2
- **Blocks:** Tasks 5, 6, 7, 8, 10, 11
- **Size:** L
- **Description:** LocalMap class — 100x100 grid of ZColumn objects. Tile access: get_tile(x,y,z),
  set_tile(x,y,z,tile). Walkability: is_walkable(x,y,z) checking terrain + NPC + Z-level validity.
  FOV: compute_fov_3d(origin_x, origin_y, origin_z, radius) — adapts existing raycasting for
  Z-level awareness. Entity management: place_entity(entity,x,y,z), move_entity(), remove_entity().
  Modified flag tracking (for save system — which tiles have player changes). Coordinate mapping:
  local_to_area(x,y) and local_to_region(x,y) with stored origin coordinates.

### Task 4: Area Map Layer
- **Files:** `area_map.py` (create)
- **Depends on:** Task 1
- **Blocks:** Tasks 5, 7, 8
- **Size:** L
- **Description:** AreaMap class — 100x100 grid per region tile. AreaTile stores: biome (from
  region terrain), base_elevation (from region elevation model), road_info (direction, type),
  building_type (None, house, shop, temple, castle_wall, etc.), poi_ref (key into POI system),
  is_water, vegetation_density. Generation: generate_from_region(region_col, region_row, seed)
  uses deterministic noise to distribute biomes, place building footprints, route roads through
  the area. Each region tile has one AreaMap; area tiles inform local map generation.

### Task 5: Procedural Generation Engine
- **Files:** `local_gen.py` (create)
- **Depends on:** Tasks 1, 2, 3, 4
- **Blocks:** Tasks 7, 8, 10
- **Size:** L
- **Description:** LocalGenerator class with generate(area_tile, local_x, local_y, seed) method.
  Terrain generation: multi-octave noise for ground cover, tree/rock placement, stream carving.
  Z-level terrain: hill slopes (fill Z-levels with earth/rock up to elevation), cliff generation,
  cave system generation (worm algorithm for tunnels, room placement). Building generation from
  area_tile.building_type — wall placement, floor tiling, door/window insertion, furniture.
  Village layout: road through center, buildings along road, well/shrine. Town layout: grid
  streets, market area, walls. Vegetation by biome and season. Natural feature generation (waterfalls,
  hot springs, clearings).

### Task 6: POI Template & Override System
- **Files:** `poi_loader.py` (create), `poi_data.py` (create), `templates/` directory (create)
- **Depends on:** Tasks 1, 2, 3
- **Blocks:** Tasks 7, 10
- **Size:** L
- **Description:** Template format: JSON files defining tile layouts for structure types. Each
  template specifies: dimensions (w,h,z_levels), tile data per level, NPC spawn points, item
  spawn points, entrance/exit points. POILoader class: load_template(type), apply_override(name),
  place_poi(local_map, x, y, z, template). poi_data.py defines the registry: which POI names
  map to which templates and overrides. Create templates: castle (scalable by size), temple,
  village_house, inn, waystation, shrine, port_dock, blacksmith, market_stall. Create overrides:
  Edo Castle, Kyoto Imperial Palace, Osaka Castle, Kinkakuji, Mt. Fuji summit, Todaiji.

### Task 7: Road Network & Waystations
- **Files:** `road_network.py` (create)
- **Depends on:** Tasks 1, 4, 5, 6
- **Blocks:** Task 10
- **Size:** L
- **Description:** RoadNetwork class managing the five Gokaido highways and secondary roads.
  Highway definitions: ordered waypoint lists with lat/lon coordinates for each station.
  Tokaido: 53 stations from Edo to Kyoto. Nakasendo: 69 stations. Koshu Kaido, Nikko Kaido,
  Oshu Kaido defined similarly. Waystation class: name, services (inn, stable, checkpoint, tea
  house), NPC spawns, dialog about destinations/distances. SignPost class: location, directions
  list (destination + distance + direction arrow). Checkpoint class: clan territory border,
  papers check, toll. Road rendering at area and local level: packed earth path, stone-paved
  for major highways, dirt track for secondary. Integration: road_network places roads on
  area_map during generation; local_gen renders road surface tiles.

### Task 8: Chunk Manager & Streaming
- **Files:** `chunk_manager.py` (create)
- **Depends on:** Tasks 3, 4, 5
- **Blocks:** Tasks 10, 11
- **Size:** M
- **Description:** ChunkManager class with LRU cache (max ~25 local maps in memory). Methods:
  get_local_map(region_col, region_row, area_x, area_y) — returns cached or generates new.
  evict_chunk(key) — saves if modified, then frees memory. preload_adjacent(player_area_x,
  player_area_y) — background load of neighboring chunks. Track modified status per chunk.
  Coordinate system: (region_col, region_row, area_x, area_y) uniquely identifies a chunk.
  Memory budget tracking and adaptive cache sizing.

### Task 9: Save/Load System
- **Files:** `save_manager.py` (create)
- **Depends on:** Task 1
- **Blocks:** Tasks 10, 11
- **Size:** M
- **Description:** SaveManager class. SQLite schema: tables for player_state, game_state,
  clan_state, explored_areas (region_col, region_row, area_x, area_y, modified flag),
  npc_state (for persistent NPCs), global_events. Flat file storage: one compressed file per
  modified chunk, stored at saves/{slot}/chunks/{region_col}_{region_row}/{area_x}_{area_y}.dat.
  Compression: zlib on serialized chunk data. Methods: save_game(slot), load_game(slot),
  save_chunk(chunk_key, local_map), load_chunk(chunk_key), auto_save(). Save on area transition.
  Save file size estimation and warnings.

### Task 10: Region Map Refactor & Transition System
- **Files:** `region_map.py` (create from world.py), `world.py` (modify), `game.py` (modify)
- **Depends on:** Tasks 3, 4, 5, 6, 7, 8, 9
- **Blocks:** Tasks 11, 12
- **Size:** L
- **Description:** Extract current World class into RegionMap — same 240x130 generation but
  renamed and adapted as the region (travel) tier. world.py becomes a thin wrapper that imports
  from region_map.py for backward compatibility. Add GameWorld class that owns RegionMap +
  ChunkManager + AreaMap cache + SaveManager — the unified world interface. Update Game class
  in game.py: add mode="travel" vs mode="local" game states. Add transition keys: Enter to
  "zoom in" from travel to local map, Escape/M to "zoom out" from local to travel. On enter:
  determine area tile under player, load/generate local map via chunk_manager, place player at
  appropriate local coordinates. On exit: save current chunk state, return player to region
  tile. Preserve ALL existing gameplay inputs for both modes.

### Task 11: Renderer Updates
- **Files:** `renderer.py` (modify)
- **Depends on:** Tasks 3, 8, 10
- **Blocks:** Task 12
- **Size:** L
- **Description:** Add draw_local_map(local_map, player, game_state) — renders the 1:1 local
  view with the current Z-level slice. Z-level indicator in title bar: "Z: 0 (Ground) ▲2 ▼5"
  showing current level and visible levels up/down. New terrain characters for local-scale
  tiles (individual tree trunks, walls, doors, stairs ↑↓, etc.). Adapt color pairs for new
  terrain types. Add draw_area_map() for mid-tier view. Update draw_world_map() to show
  "Region Map" label. Transition message overlay ("Entering [location name]..."). Dim rendering
  for tiles on adjacent Z-levels visible through open space. Update sidebar for local map
  (show local coordinates, area name, Z-level).

### Task 12: Entity System Z-Level Integration
- **Files:** `entities.py` (modify), `mechanics.py` (modify)
- **Depends on:** Tasks 2, 3, 10, 11
- **Blocks:** Task 13
- **Size:** M
- **Description:** Add z attribute to Player and NPC classes (default 0). Update all movement
  code: _try_move() checks Z-level walkability, add vertical movement keys (< for up, > for
  down — DF convention). NPC AI: ai_tick() considers Z-level for pathfinding, chase only on
  same Z. Combat: can only attack on same Z-level. Update FOV: player.fov_radius applies
  horizontally, separate vertical visibility rules. Fall damage: moving to air tile causes
  fall to next solid Z below, damage based on distance. Climbing: mountainous terrain allows
  slow ascent (stamina cost). Update interaction (talk, trade, debate) to require same Z-level.

### Task 13: Clan Simulation Engine
- **Files:** `clan_sim.py` (create)
- **Depends on:** Tasks 1, 10, 12
- **Blocks:** Task 14
- **Size:** L
- **Description:** ClanSimulation class manages all clan state. ClanState: territory (list of
  region tiles), military_strength, treasury, daimyo (NPC reference), allies, enemies, truces.
  Simulation tick (runs once per game day): evaluate war declarations (based on strength ratio,
  neighbor relations, historical tendencies), resolve battles (army strength + terrain + random),
  territory changes (loser cedes border region tiles to winner), diplomacy events (alliance
  offers, betrayals, marriages). Player interaction: can join a clan (affects reputation, dialog,
  available quests), can influence battles by participating, can broker peace/war through debate.
  Territory changes update region map tile factions and affect NPC spawning in those areas.
  Historical accuracy: starting state reflects ~1560 Sengoku period clan boundaries.

### Task 14: Integration & Polish
- **Files:** `game.py` (modify), `engi.py` (modify)
- **Depends on:** Tasks 10, 11, 12, 13
- **Blocks:** none
- **Size:** M
- **Description:** Final integration pass. Wire clan simulation into game loop (daily tick).
  Verify travel→enter→explore→exit→re-enter roundtrip preserves state. Test save/load cycle
  with modified chunks. Verify combat, debate, survival systems work on local map. Add
  character creation option for starting province (affects which clan territory you start in).
  Update _post_creation_messages for dual-map intro. Add help text for new controls. Startup
  flow: generate region map, then place player on travel map (existing behavior). Polish
  transition messages. Update README.md with new controls and map system description.

## File Ownership Matrix

| File | Task | Action |
|------|------|--------|
| `data.py` | Task 1 | Modify |
| `clan_data.py` | Task 1 | Create |
| `z_level.py` | Task 2 | Create |
| `local_map.py` | Task 3 | Create |
| `area_map.py` | Task 4 | Create |
| `local_gen.py` | Task 5 | Create |
| `poi_loader.py` | Task 6 | Create |
| `poi_data.py` | Task 6 | Create |
| `templates/` | Task 6 | Create (directory + JSON files) |
| `road_network.py` | Task 7 | Create |
| `chunk_manager.py` | Task 8 | Create |
| `save_manager.py` | Task 9 | Create |
| `region_map.py` | Task 10 | Create (from world.py) |
| `world.py` | Task 10 | Modify (thin wrapper) |
| `game.py` | Task 10, 14 | Modify |
| `renderer.py` | Task 11 | Modify |
| `entities.py` | Task 12 | Modify |
| `mechanics.py` | Task 12 | Modify |
| `clan_sim.py` | Task 13 | Create |
| `engi.py` | Task 14 | Modify |

## Execution Waves

| Wave | Tasks | Parallel | Description |
|------|-------|----------|-------------|
| 1 | Task 1 | No | Core data structures & constants |
| 2 | Task 2, Task 4, Task 9 | Yes | Z-levels, area map, save system |
| 3 | Task 3 | No | Local map core (needs Z-level) |
| 4 | Task 5, Task 6, Task 8 | Yes | Proc-gen, POI system, chunk manager |
| 5 | Task 7 | No | Road network |
| 6 | Task 10 | No | Region map refactor + transitions |
| 7 | Task 11, Task 12 | Yes | Renderer + entity Z-integration |
| 8 | Task 13, Task 14 | Yes | Clan simulation + final integration |

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| Memory blow-up from ±32 Z-levels | High | High | Sparse Z-level storage (dict, not array) |
| Proc-gen produces unnatural terrain | Medium | Medium | Template system + iterative tuning |
| Curses redraw too slow for 1:1 map | Medium | High | Viewport culling, dirty-tile tracking |
| Deterministic seeding cross-platform drift | Low | Medium | Pin seed algorithm, test |
| Save file size grows unbounded | Medium | Medium | Compress chunks, save only modified |
| Scope creep in hand-crafting POIs | High | Medium | Templates first, overrides incrementally |
| Region→local transition breaks gameplay | Medium | High | Preserve existing input handlers |
| Clan simulation cascading bugs | Medium | High | Independent sim, explicit territory-change events |

## Testing Strategy

- **Unit:** test_z_level.py, test_local_map.py, test_area_map.py, test_local_gen.py,
  test_chunk_manager.py, test_save_manager.py, test_clan_sim.py, test_road_network.py
- **Integration:** Travel→enter→explore→exit→re-enter roundtrip; save/load full cycle;
  clan territory change propagation; POI override loading
- **Edge cases:** Chunk boundary crossing; Z-level limits (±32); empty area tiles;
  water-only region tiles; POI at region boundary; save during transition
- **Regression:** Combat, debate, survival, NPC AI on local map

## Readiness Breakdown

| Dimension | Score | Notes |
|-----------|-------|-------|
| Requirements | 18/20 | LISA spec comprehensive; historical accuracy details TBD per-POI |
| Codebase | 16/20 | Full codebase read; world.py refactor well-understood |
| Design | 15/20 | 3-tier architecture clear; proc-gen details emerge during impl |
| Risk | 14/20 | Memory and performance risks identified; mitigations planned |
| Operational | 15/20 | Branch created; no external blockers |
| **Total** | **78/100** | Proceed — gaps are implementation details, not design gaps |
