## Requirements Summary

**Domain**: Game Engine (world generation, tile streaming, procedural content, persistence, simulation)
**Goal**: Implement a three-tier map hierarchy (region -> area -> local) with 1:1 meter-scale local maps, ±32 Z-levels, full clan simulation, historical road network, hand-crafted POIs, and full world state persistence.
**Complexity**: Complex (8+ new files, 4+ modified files, fundamental architecture change)
**Approach**: C — True 1:1 Streaming with Region Hierarchy (Dwarf Fortress-style)

### Functional Requirements

- [FR-1]: **Three-Tier Map Hierarchy**
  - Region Map: existing 240x130 grid (serves as travel map)
  - Area Map: ~100x100 per region tile (~100m² each), contains terrain biome, roads, building footprints
  - Local Map: 100x100x64 (±32 Z-levels) per area tile at 1:1 meter scale, generated on demand
  - Acceptance: Player can view all three tiers; region and local are distinct gameplay surfaces

- [FR-2]: **Travel Map (Region Map)**
  - Existing 240x130 grid preserved as the travel/overworld map
  - Player moves tile-by-tile for long-distance travel
  - All current cities, terrain, rivers, roads visible at this scale
  - Press explicit key to "enter" a region tile and transition to local map
  - Acceptance: Travel from Edo to Kyoto using existing movement on region map

- [FR-3]: **Local Map (1:1 Meter Scale)**
  - Each tile represents 1 meter squared
  - Adaptive viewport — uses available terminal size
  - Z-levels: ±32 levels (mountains have real elevation, caves go underground)
  - Buildings, trees, hills represented to scale vertically
  - Press explicit key to "exit" back to travel map
  - Acceptance: Walk through a forest at 1:1 scale, enter a building, go upstairs

- [FR-4]: **Hand-Crafted POIs (Hybrid Template + Override)**
  - Templates for common structures: castle, temple, village, port, waystation, inn
  - JSON override files for historically significant locations (Edo Castle, Kinkakuji, Mt. Fuji, etc.)
  - All 38 current CITIES entries become hand-crafted POIs at local map scale
  - Natural wonders (Mt. Fuji, hot springs, etc.) also hand-crafted
  - Acceptance: Enter Edo and see a recognizable castle layout, not random generation

- [FR-5]: **Procedural Generation**
  - Wilderness, minor towns, caves generated procedurally from deterministic seed
  - Seed derived from coordinates — same location always generates same terrain
  - Terrain type, elevation, and biome inherited from region/area map tier
  - Generated areas must feel natural (forests, clearings, streams, trails)
  - Acceptance: Visit a forest tile, leave, return — same layout both times

- [FR-6]: **Z-Level System**
  - ±32 levels per area tile (level 0 = ground surface)
  - Mountains: positive Z-levels with climbable terrain
  - Caves/mines: negative Z-levels
  - Buildings: multi-story (castles up to 5+ floors, houses 1-2)
  - Player can look above and below current Z-level
  - Acceptance: Climb a mountain, descend into a cave, ascend a castle keep

- [FR-7]: **Full Clan Simulation (~50+ Sengoku Clans)**
  - Each notable clan has defined territory (provinces), daimyo, retainers
  - Inter-clan diplomacy: alliances, wars, treaties
  - Clans wage war, gain/lose territory over time
  - Player can join, oppose, or ignore clan politics
  - Clan-specific NPCs with unique dialog and quests
  - Dynamic world state: wars change borders, sieges change cities
  - Acceptance: Oda clan expands territory over game time; player can influence outcomes

- [FR-8]: **Full Historical Road Network**
  - All five Gokaido highways (Tokaido, Nakasendo, Koshu Kaido, Nikko Kaido, Oshu Kaido)
  - Secondary and tertiary provincial roads
  - Waystations (shukuba) at historical intervals (~10km apart)
  - Checkpoints (sekisho) at province borders
  - Road signs at intersections pointing to destinations
  - Inns at waystations with lodging, food, and information
  - Acceptance: Follow the Tokaido from Edo to Kyoto, encountering waystations at historically accurate intervals

- [FR-9]: **Static Explored Areas**
  - Once a player explores a local area, it remains exactly the same on return
  - Player modifications (dropped items, killed NPCs, built fires) persist permanently
  - Full world state saved: NPC movement, item decay, weather state per area
  - Acceptance: Drop a sword in a forest, travel across Japan, return — sword is still there

- [FR-10]: **Wilderness Navigation to POIs**
  - Player can reach hand-crafted POIs from wilderness by finding roads and reading signs
  - Roads visible on local map as distinct terrain
  - Signs at intersections with text pointing to nearby destinations
  - Waystations provide information about nearby cities and distances
  - Acceptance: Start in wilderness, find a road, follow signs to reach Kyoto

### Non-Functional Requirements

- [NFR-1]: **Memory**: Active local map area should fit in ~80-100MB RAM (LRU cache for surrounding areas)
- [NFR-2]: **Load time**: Transitioning between travel and local map should take <2 seconds
- [NFR-3]: **Save size**: Full world state saves should be manageable (<500MB for heavily explored world)
- [NFR-4]: **Generation consistency**: Deterministic seeding — same seed + coordinates = same output, always
- [NFR-5]: **Performance**: Local map rendering at 30+ FPS equivalent (curses redraw < 33ms)

### Constraints

- Pure Python (no C extensions beyond stdlib)
- Curses-based terminal renderer (existing)
- Must remain playable on 120x40 terminal minimum
- Existing gameplay systems (combat, debate, survival) must continue working on local map

### Scope Boundary

**IN scope**:
- Three-tier map architecture (region, area, local)
- Z-level system (±32)
- Procedural generation with deterministic seeding
- Hand-crafted POI template + override system
- Full clan simulation with dynamic territories
- Full Gokaido road network + secondary roads + waystations
- Save/load system (SQLite + compressed flat files)
- Travel map <-> local map explicit transition
- Sign/waystation navigation system

**OUT of scope**:
- Graphical renderer (stays curses)
- Multiplayer
- Mod/plugin system
- Map editor GUI
- Real-time simulation when player is absent (areas only simulate when loaded)
- Ocean travel / naval mechanics
- Okinawa / Ryukyu islands

### Dependencies

- **Depends on**: Current codebase (world.py, data.py, entities.py, game.py, renderer.py, mechanics.py)
- **Blocks**: Nothing external — this is a self-contained feature

### Assumptions (MUST VALIDATE)

- Python's `sqlite3` module is sufficient for save/load performance — **risk if wrong**: need alternative storage
- Curses can render Z-level indicators without major performance issues — **risk if wrong**: need renderer optimization
- Deterministic seeding with Python's `random.Random(seed)` produces consistent cross-platform results — **risk if wrong**: saves not portable
- 100x100 area tiles provide sufficient granularity for road/building placement — **risk if wrong**: need different area tile size

### Red Flags Identified

- **Scale**: 375 billion potential tiles. Mitigated by on-demand generation + deterministic seeding (only modified tiles stored).
- **Scope**: "Full Japan + all clans + full simulation" is a multi-year game development effort in reality. Architecture-first approach means we design for completeness but implement incrementally.
- **Hand-crafting**: ~38 cities + temples + natural wonders need detailed layouts. Template system reduces labor but still significant data authoring.
- **Clan simulation**: Dynamic territory changes affect the travel map, area maps, AND local maps simultaneously. Complex state synchronization.

### Open Questions

- Historical accuracy sources: which references to use for waystation placement? (Recommend: Tokaido Gojusan-tsugi woodblock prints + modern historical databases)
- Clan starting territories: use 1560 (pre-Nobunaga unification push) as the base year?
- Default: Yes, 1560 as canonical starting state

### Implementation Strategy

Full architecture first, then implement in waves:
1. Core 3-tier map data structures + generation pipeline
2. Z-level system + local map renderer
3. Travel <-> local transition + persistence (SQLite + flat files)
4. Procedural generation (terrain, buildings, vegetation)
5. POI template system + hand-crafted overrides
6. Road network + waystations + signs
7. Clan data + territory system
8. Clan simulation (diplomacy, war, dynamic borders)
